#!/usr/bin/env python3
"""
Generate demo traffic for Search Analytics with OTel.

Sends realistic search, click, cart, and purchase events through the API,
creating OTel spans that flow to Elastic APM.

Usage:
    python generate_traffic.py --blog 2 --sessions 20    # Search only
    python generate_traffic.py --blog 3 --sessions 50    # + clicks
    python generate_traffic.py --blog 4 --sessions 100   # + cart + purchases
"""
import argparse
import random
import time
import uuid
import sys

import httpx

# =============================================================================
# Query distribution — designed for interesting analytics
# =============================================================================

# High volume: common searches with good results
HIGH_VOLUME_QUERIES = [
    "laptop", "headphones", "running shoes", "coffee maker", "yoga mat",
    "bluetooth speaker", "keyboard", "wireless mouse",
]

# Medium volume: moderate traffic
MEDIUM_VOLUME_QUERIES = [
    "backpack", "desk lamp", "water bottle", "phone case",
    "usb hub", "leather wallet", "sunglasses", "travel mug",
]

# Low volume: occasional searches
LOW_VOLUME_QUERIES = [
    "garden tools", "chess set", "meditation cushion", "balance board",
    "solar charger", "foam roller",
]

# Zero-result queries: these won't match any products
ZERO_RESULT_QUERIES = [
    "quantum physics calculator", "unicorn saddle",
    "holographic projector", "time machine parts",
]

# Click position weights: position 1 gets clicked most, then 2, etc.
POSITION_WEIGHTS = [0.35, 0.20, 0.12, 0.08, 0.06, 0.05, 0.04, 0.03, 0.03, 0.02, 0.01, 0.01]


def pick_query() -> str:
    """Pick a query weighted by expected volume."""
    roll = random.random()
    if roll < 0.50:
        return random.choice(HIGH_VOLUME_QUERIES)
    elif roll < 0.80:
        return random.choice(MEDIUM_VOLUME_QUERIES)
    elif roll < 0.92:
        return random.choice(LOW_VOLUME_QUERIES)
    else:
        return random.choice(ZERO_RESULT_QUERIES)


def simulate_session(client: httpx.Client, base_url: str, blog_level: int, verbose: bool):
    """Simulate one user session: search, optionally click, cart, purchase."""
    client_id = f"user-{random.randint(1000, 9999)}"
    query = pick_query()

    # --- Search ---
    try:
        resp = client.post(f"{base_url}/api/search", json={
            "query": query, "page": 1, "page_size": 12,
        })
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ✗ Search failed for '{query}': {e}")
        return

    hits = data.get("hits", [])
    query_id = data.get("query_id")
    total = data.get("total", 0)

    if verbose:
        print(f"  Search: '{query}' → {total} results")

    # Stop here for Blog 2 (search only) or if no results
    if blog_level < 3 or not hits:
        return

    # --- Click (Blog 3+) ---
    if random.random() < 0.60:  # 60% of searches get a click
        max_pos = min(len(hits), 12)
        weights = POSITION_WEIGHTS[:max_pos]
        position = random.choices(range(1, max_pos + 1), weights=weights)[0]
        hit = hits[position - 1]

        try:
            client.post(f"{base_url}/api/events", json={
                "object_id": hit["id"],
                "position": position,
                "query_id": query_id,
                "client_id": client_id,
                "user_query": query,
            })
            if verbose:
                print(f"    Click: {hit['id']} at position {position}")
        except Exception as e:
            print(f"  ✗ Click failed: {e}")
            return

        # Sometimes a second click on a different result
        if random.random() < 0.15 and max_pos > 1:
            pos2 = random.choices(range(1, max_pos + 1), weights=weights)[0]
            if pos2 != position:
                hit2 = hits[pos2 - 1]
                try:
                    client.post(f"{base_url}/api/events", json={
                        "object_id": hit2["id"],
                        "position": pos2,
                        "query_id": query_id,
                        "client_id": client_id,
                        "user_query": query,
                    })
                except Exception:
                    pass

        # Stop here for Blog 3 (search + clicks)
        if blog_level < 4:
            return

        # --- Add to Cart (Blog 4+) ---
        if random.random() < 0.30:  # 30% of clicks become carts
            try:
                client.post(f"{base_url}/api/cart/add", json={
                    "object_id": hit["id"],
                    "position": position,
                    "query_id": query_id,
                    "client_id": client_id,
                    "user_query": query,
                    "quantity": random.choice([1, 1, 1, 2]),
                    "price": hit.get("price"),
                })
                if verbose:
                    print(f"    Cart: {hit['id']} at ${hit.get('price', '?')}")
            except Exception as e:
                print(f"  ✗ Cart failed: {e}")
                return

            # --- Purchase (Blog 4+) ---
            if random.random() < 0.40:  # 40% of carts become purchases
                order_id = str(uuid.uuid4())[:8]
                price = hit.get("price", 29.99)
                try:
                    client.post(f"{base_url}/api/checkout", json={
                        "order_id": order_id,
                        "total_amount": price,
                        "items": [{"object_id": hit["id"], "quantity": 1, "price": price}],
                        "client_id": client_id,
                        "query_id": query_id,
                        "user_query": query,
                    })
                    if verbose:
                        print(f"    Purchase: order {order_id} for ${price}")
                except Exception as e:
                    print(f"  ✗ Purchase failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate demo traffic for search analytics"
    )
    parser.add_argument(
        "--blog", type=int, default=2, choices=[2, 3, 4],
        help="Blog level: 2=search only, 3=+clicks, 4=+cart+purchase (default: 2)"
    )
    parser.add_argument(
        "--sessions", type=int, default=50,
        help="Number of user sessions to simulate (default: 50)"
    )
    parser.add_argument(
        "--url", type=str, default="http://localhost:8000",
        help="Base URL of the search API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print details for each session"
    )
    parser.add_argument(
        "--delay", type=float, default=0.1,
        help="Delay between sessions in seconds (default: 0.1)"
    )
    args = parser.parse_args()

    blog_labels = {2: "search only", 3: "search + clicks", 4: "search + clicks + cart + purchases"}
    print(f"Generating {args.sessions} sessions (Blog {args.blog}: {blog_labels[args.blog]})")
    print(f"Target: {args.url}")
    print()

    with httpx.Client(timeout=10.0) as client:
        # Verify server is running
        try:
            client.get(f"{args.url}/")
        except httpx.ConnectError:
            print(f"Error: Cannot connect to {args.url}")
            print("Start the server first: python app.py")
            sys.exit(1)

        for i in range(args.sessions):
            if not args.verbose and (i + 1) % 10 == 0:
                print(f"  Session {i + 1}/{args.sessions}")

            simulate_session(client, args.url, args.blog, args.verbose)
            time.sleep(args.delay)

    print(f"\nDone! {args.sessions} sessions generated.")
    print(f"Check Kibana > Discover > traces-apm-* to see the data.")
    print(f"Try the queries in queries/blog{args.blog}_*.esql")


if __name__ == "__main__":
    main()
