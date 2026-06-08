/**
 * Search Analytics Demo — Frontend
 *
 * Blog 2 (active):    Search form, result rendering
 * Blog 3 (active):    Click tracking
 * Blog 4 (active):    Add to cart tracking
 */

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

// State
let lastQueryId = null;
let lastQuery = null;

// Module scope so trackClick() / addToCart() can read it when Blog 3/4 are enabled
const CLIENT_ID = localStorage.getItem("search_client_id")
    || (() => {
        const id = crypto.randomUUID();
        localStorage.setItem("search_client_id", id);
        return id;
    })();

document.addEventListener("DOMContentLoaded", () => {
    const clientIdEl = document.getElementById("client-id");
    const searchForm = document.getElementById("search-form");
    const searchInput = document.getElementById("search-input");
    const statsEl = document.getElementById("stats");

    if (!clientIdEl || !searchForm || !searchInput || !statsEl) {
        console.error("Search UI failed to initialize: missing DOM elements");
        return;
    }

    clientIdEl.textContent = CLIENT_ID;

    searchForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        statsEl.textContent = "Searching…";

        try {
            const response = await fetch("/api/search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query, page: 1, page_size: 12 }),
            });

            if (!response.ok) {
                const detail = await response.text();
                console.error(`Search failed: ${response.status}`, detail);
                statsEl.textContent = `Search error: ${response.status} ${response.statusText}`;
                return;
            }

            const data = await response.json();
            lastQueryId = data.query_id;
            lastQuery = query;

            statsEl.textContent = `${data.total} results in ${data.took_ms}ms`;
            renderResults(data.hits || []);
        } catch (err) {
            console.error("Search request failed:", err);
            statsEl.textContent = "Search failed — check the server is running.";
        }
    });
});


function renderResults(hits) {
    const container = document.getElementById("results");
    if (!container) return;

    if (hits.length === 0) {
        container.innerHTML = '<div id="empty-state">No results found</div>';
        return;
    }

    container.innerHTML = hits.map((hit, i) => {
        const position = i + 1;
        const rating = Number(hit.rating) || 0;
        const stars = "★".repeat(Math.round(rating)) + "☆".repeat(5 - Math.round(rating));
        const stockLabel = hit.in_stock
            ? ""
            : '<span class="out-of-stock">Out of Stock</span>';
        const price = Number(hit.price) || 0;

        return `
            <div class="result-card" data-id="${escapeHtml(hit.id)}" data-position="${position}" data-price="${price}">
                <h3>${escapeHtml(hit.title)}</h3>
                <div class="meta">${escapeHtml(hit.brand)} · ${escapeHtml(hit.category)}</div>
                <div class="price">$${price.toFixed(2)} ${stockLabel}</div>
                <div class="rating">${stars} (${Number(hit.review_count) || 0} reviews)</div>
                <button class="cart-btn" data-id="${hit.id}" data-position="${position}" data-price="${price}">Add to Cart</button>
            </div>
        `;
    }).join("");

    // ╔══════════════════════════════════════════════════════════════╗
    // ║  BLOG 3: Click Tracking                                    ║
    // ║  Uncomment the block below to send click events.           ║
    // ║  Also uncomment the Blog 3 section in app.py.              ║
    // ╚══════════════════════════════════════════════════════════════╝

    document.querySelectorAll(".result-card").forEach(card => {
        card.addEventListener("click", (e) => {
            if (e.target.classList.contains("cart-btn")) return;
            trackClick(card.dataset.id, parseInt(card.dataset.position));
        });
    });

    // ╔══════════════════════════════════════════════════════════════╗
    // ║  BLOG 4: Cart Tracking                                     ║
    // ║  Uncomment the block below to send add-to-cart events.     ║
    // ║  Also uncomment the Blog 4 section in app.py and the       ║
    // ║  cart button HTML above + CSS in index.html.               ║
    // ║  Requires: Blog 3 must be uncommented first.               ║
    // ╚══════════════════════════════════════════════════════════════╝

    document.querySelectorAll(".cart-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            addToCart(btn.dataset.id, parseInt(btn.dataset.position), parseFloat(btn.dataset.price));
        });
    });
}


// ╔══════════════════════════════════════════════════════════════════╗
// ║  BLOG 3: Click Tracking Functions                              ║
// ║  Uncomment the function below.                                 ║
// ╚══════════════════════════════════════════════════════════════════╝

async function trackClick(objectId, position) {
    try {
        await fetch("/api/events", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                object_id: objectId,
                position: position,
                query_id: lastQueryId,
                client_id: CLIENT_ID,
                user_query: lastQuery,
            }),
        });
        console.log(`Click tracked: ${objectId} at position ${position}`);
    } catch (err) {
        console.error("Click tracking failed:", err);
    }
}


// ╔══════════════════════════════════════════════════════════════════╗
// ║  BLOG 4: Cart Tracking Functions                               ║
// ║  Uncomment the function below.                                 ║
// ║  Requires: Blog 3 must be uncommented first.                   ║
// ╚══════════════════════════════════════════════════════════════════╝

async function addToCart(objectId, position, price) {
    try {
        await fetch("/api/cart/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                object_id: objectId,
                position: position,
                query_id: lastQueryId,
                client_id: CLIENT_ID,
                user_query: lastQuery,
                quantity: 1,
                price: price,
            }),
        });
        console.log(`Added to cart: ${objectId} at $${price}`);
    } catch (err) {
        console.error("Cart tracking failed:", err);
    }
}
