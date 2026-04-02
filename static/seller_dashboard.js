// ── Seller Dashboard ──────────────────────────────────────────────────────────

async function init() {
    await loadSellerStats();
}

async function loadSellerStats() {
    try {
        const res = await fetch("/api/products");
        if (res.status === 403) { window.location.href = "/login"; return; }

        const products = await res.json();

        const statMyProducts = document.getElementById("statMyProducts");
        const statInStock    = document.getElementById("statInStock");

        if (statMyProducts) statMyProducts.textContent = products.length;
        if (statInStock)    statInStock.textContent    = products.filter(p => p.stock_quantity > 0).length;

    } catch (err) {
        console.error("Failed to load seller stats:", err);
    }
}

init();