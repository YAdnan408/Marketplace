// ── State ─────────────────────────────────────────────────────────────────────
let allProducts = [];
let activeCategory = "";

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
    await loadProducts();

    // Check for ?cat= param in URL
    const params = new URLSearchParams(window.location.search);
    const cat = params.get("cat");
    if (cat) {
        const pill = document.querySelector(`.category-pill[data-category="${cat}"]`);
        if (pill) {
            document.querySelectorAll(".category-pill").forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            activeCategory = cat;
            renderAll(allProducts.filter(p => String(p.category_id) === cat));
        }
    }

    setupCategoryPills();
    setupSearch();
    setupLogout();
}

async function loadProducts() {
    try {
        const res = await fetch("/api/products");
        if (res.status === 403) { window.location.href = "/login"; return; }
        allProducts = await res.json();
        renderAll(allProducts);
    } catch (err) {
        document.getElementById("pageGrid").innerHTML =
            `<div class="featured-empty"><span>⚠️</span><p>Failed to load. Please refresh.</p></div>`;
    }
}

function renderAll(products) {
    const grid = document.getElementById("pageGrid");
    const count = document.getElementById("pageCount");
    if (count) count.textContent = `${products.length} product${products.length !== 1 ? "s" : ""}`;

    if (products.length === 0) {
        grid.innerHTML = `<div class="featured-empty"><span>🛍</span><p>No products found.</p></div>`;
        return;
    }

    grid.innerHTML = products.map((p, i) => `
        <div class="feat-card" style="animation-delay:${i * 0.03}s; cursor:pointer;" onclick="window.location.href='/product/${p.id}'">
            <div class="feat-card-image">
                ${p.image_name
                    ? `<img src="/static/uploads/product_images/${p.image_name}" alt="${escapeHtml(p.name)}" loading="lazy">`
                    : `<div class="feat-card-no-image">📷</div>`}
                <div class="feat-card-badge">${p.category_name || "General"}</div>
            </div>
            <div class="feat-card-body">
                <h4 class="feat-card-name">${escapeHtml(p.name)}</h4>
                <p class="feat-card-desc">${escapeHtml(p.description || "No description provided.")}</p>
                <div class="feat-card-footer">
                    <span class="feat-card-price">৳${parseFloat(p.price).toLocaleString("en-BD", {minimumFractionDigits: 2})}</span>
                    <span class="feat-card-stock ${p.stock_quantity === 0 ? "out" : ""}">
                        ${p.stock_quantity === 0 ? "Out of stock" : `${p.stock_quantity} left`}
                    </span>
                </div>
            </div>
        </div>
    `).join("");
}

function getFiltered() {
    const search = document.getElementById("pageSearch").value.toLowerCase().trim();
    return allProducts.filter(p => {
        const matchesCat = !activeCategory || String(p.category_id) === activeCategory;
        const matchesSearch = !search || p.name.toLowerCase().includes(search) ||
            (p.description && p.description.toLowerCase().includes(search));
        return matchesCat && matchesSearch;
    });
}

function setupCategoryPills() {
    document.querySelectorAll(".category-pill").forEach(pill => {
        pill.addEventListener("click", () => {
            document.querySelectorAll(".category-pill").forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            activeCategory = pill.dataset.category;
            renderAll(getFiltered());
        });
    });
}

function setupSearch() {
    document.getElementById("pageSearch").addEventListener("input", () => renderAll(getFiltered()));
}

function setupLogout() {
    const btn = document.getElementById("logoutBtn");
    if (!btn) return;
    btn.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/logout", { method: "POST" });
            if (res.ok) window.location.href = "/login";
        } catch (err) { console.error("Logout failed:", err); }
    });
}

function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
}

// Also add products page layout CSS inline for the header
document.addEventListener("DOMContentLoaded", () => {
    const style = document.createElement("style");
    style.textContent = `
        .products-page { padding: 56px 0 72px; background: var(--cream); min-height: 60vh; }
        .products-page-inner { max-width: 1200px; margin: 0 auto; padding: 0 44px; }
        .products-page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px; gap: 20px; flex-wrap: wrap; }
        .products-page-title { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; color: var(--espresso); }
        .products-page-count { font-size: 0.85rem; color: var(--text-muted); }
        @media (max-width: 768px) { .products-page-inner { padding: 0 20px; } .products-page-header { flex-direction: column; align-items: flex-start; } }
    `;
    document.head.appendChild(style);
});

init();