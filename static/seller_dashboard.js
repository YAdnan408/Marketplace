// ── Seller Dashboard ──────────────────────────────────────────────────────────

async function init() {
    await Promise.all([loadSellerStats(), loadOrderStats()]);
}

// ── Product stats ─────────────────────────────────────────────────────────────

async function loadSellerStats() {
    try {
        const res = await fetch("/api/products/");
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

// ── Order stats ───────────────────────────────────────────────────────────────

async function loadOrderStats() {
    try {
        const res = await fetch("/api/orders/");
        if (!res.ok) return;

        const orders = await res.json();
        const pending = orders.filter(o => o.status === "pending").length;

        const statPending = document.getElementById("statPendingOrders");
        if (statPending) statPending.textContent = pending;

    } catch (err) {
        console.error("Failed to load order stats:", err);
    }
}

init();