/**
 * Search Analytics Demo — Frontend
 *
 * Blog 2 (active):    Search form, result rendering
 * Blog 3 (commented): Click tracking
 * Blog 4 (commented): Add to cart tracking
 */

// =============================================================================
// Client Identity (persistent across sessions)
// =============================================================================

const CLIENT_ID = localStorage.getItem("search_client_id")
    || (() => { const id = crypto.randomUUID(); localStorage.setItem("search_client_id", id); return id; })();

document.getElementById("client-id").textContent = CLIENT_ID;

// State
let lastQueryId = null;
let lastQuery = null;


// =============================================================================
// Search
// =============================================================================

document.getElementById("search-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = document.getElementById("search-input").value.trim();

    const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, page: 1, page_size: 12 }),
    });
    const data = await response.json();

    lastQueryId = data.query_id;
    lastQuery = query;

    document.getElementById("stats").textContent =
        `${data.total} results in ${data.took_ms}ms`;

    renderResults(data.hits);
});


function renderResults(hits) {
    const container = document.getElementById("results");

    if (hits.length === 0) {
        container.innerHTML = '<div id="empty-state">No results found</div>';
        return;
    }

    container.innerHTML = hits.map((hit, i) => {
        const position = i + 1;
        const stars = "★".repeat(Math.round(hit.rating)) + "☆".repeat(5 - Math.round(hit.rating));
        const stockLabel = hit.in_stock ? "" : '<span class="out-of-stock">Out of Stock</span>';

        return `
            <div class="result-card" data-id="${hit.id}" data-position="${position}" data-price="${hit.price}">
                <h3>${hit.title}</h3>
                <div class="meta">${hit.brand} · ${hit.category}</div>
                <div class="price">$${hit.price.toFixed(2)} ${stockLabel}</div>
                <div class="rating">${stars} (${hit.review_count} reviews)</div>
                ${ /* BLOG 4: Uncomment the line below to show Add to Cart button */ ""}
                ${ /* `<button class="cart-btn" data-id="${hit.id}" data-position="${position}" data-price="${hit.price}">Add to Cart</button>` */ ""}
            </div>
        `;
    }).join("");

    // ╔══════════════════════════════════════════════════════════════╗
    // ║  BLOG 3: Click Tracking                                    ║
    // ║  Uncomment the block below to send click events.           ║
    // ║  Also uncomment the Blog 3 section in app.py.              ║
    // ╚══════════════════════════════════════════════════════════════╝

    // document.querySelectorAll(".result-card").forEach(card => {
    //     card.addEventListener("click", (e) => {
    //         // Don't track if clicking the cart button
    //         if (e.target.classList.contains("cart-btn")) return;
    //         trackClick(card.dataset.id, parseInt(card.dataset.position));
    //     });
    // });

    // ╔══════════════════════════════════════════════════════════════╗
    // ║  BLOG 4: Cart Tracking                                     ║
    // ║  Uncomment the block below to send add-to-cart events.     ║
    // ║  Also uncomment the Blog 4 section in app.py and the       ║
    // ║  cart button HTML above + CSS in index.html.               ║
    // ║  Requires: Blog 3 must be uncommented first.               ║
    // ╚══════════════════════════════════════════════════════════════╝

    // document.querySelectorAll(".cart-btn").forEach(btn => {
    //     btn.addEventListener("click", (e) => {
    //         e.stopPropagation();
    //         addToCart(btn.dataset.id, parseInt(btn.dataset.position), parseFloat(btn.dataset.price));
    //     });
    // });
}


// ╔══════════════════════════════════════════════════════════════════╗
// ║  BLOG 3: Click Tracking Functions                              ║
// ║  Uncomment the function below.                                 ║
// ╚══════════════════════════════════════════════════════════════════╝

// async function trackClick(objectId, position) {
//     try {
//         await fetch("/api/events", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({
//                 object_id: objectId,
//                 position: position,
//                 query_id: lastQueryId,
//                 client_id: CLIENT_ID,
//                 user_query: lastQuery,
//             }),
//         });
//         console.log(`Click tracked: ${objectId} at position ${position}`);
//     } catch (err) {
//         console.error("Click tracking failed:", err);
//     }
// }


// ╔══════════════════════════════════════════════════════════════════╗
// ║  BLOG 4: Cart Tracking Functions                               ║
// ║  Uncomment the function below.                                 ║
// ║  Requires: Blog 3 must be uncommented first.                   ║
// ╚══════════════════════════════════════════════════════════════════╝

// async function addToCart(objectId, position, price) {
//     try {
//         await fetch("/api/cart/add", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({
//                 object_id: objectId,
//                 position: position,
//                 query_id: lastQueryId,
//                 client_id: CLIENT_ID,
//                 user_query: lastQuery,
//                 quantity: 1,
//                 price: price,
//             }),
//         });
//         console.log(`Added to cart: ${objectId} at $${price}`);
//     } catch (err) {
//         console.error("Cart tracking failed:", err);
//     }
// }
