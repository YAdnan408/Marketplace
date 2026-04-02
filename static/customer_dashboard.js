// ── Config ────────────────────────────────────────────────────────────────────

const FEATURED_LIMIT = 8; // max products shown on landing page

// ── State ─────────────────────────────────────────────────────────────────────

let allProducts = [];
let activeCategory = null;

// Category emoji map
const CAT_ICONS = {
    "Smartphones":          "📱",
    "Laptops":              "💻",
    "Clothing":             "👕",
    "Musical Instruments":  "🎸",
    "Books & Stationery":   "📚",
    "Sports & Fitness Gear":"⚽",
};

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
    await Promise.all([loadProducts(), loadCategories()]);
    setupEventListeners();
}

// ── Fetch ─────────────────────────────────────────────────────────────────────

async function loadProducts() {
    try {
        const res = await fetch("/api/products");
        if (res.status === 403) { window.location.href = "/login"; return; }

        allProducts = await res.json();

        // Update hero stat
        const statEl = document.getElementById("statProducts");
        if (statEl) statEl.textContent = allProducts.length + "+";

        renderFeatured(allProducts);

    } catch (err) {
        const grid = document.getElementById("featuredGrid");
        if (grid) grid.innerHTML = `<div class="featured-empty"><span>⚠️</span><p>Failed to load products. Please refresh.</p></div>`;
    }
}

async function loadCategories() {
    try {
        const res = await fetch("/api/customer/categories");
        const categories = await res.json();
        renderCategoryStrip(categories);
    } catch (err) {
        console.error("Failed to load categories:", err);
    }
}

// ── Render: Category Strip ────────────────────────────────────────────────────

function renderCategoryStrip(categories) {
    const strip = document.getElementById("categoryStrip");
    if (!strip) return;

    const allPill = document.createElement("button");
    allPill.className = "category-pill active";
    allPill.dataset.id = "";
    allPill.innerHTML = `<span class="category-pill-icon">🛍</span> All`;
    allPill.addEventListener("click", () => filterByCategory(null, allPill));
    strip.appendChild(allPill);

    categories.forEach(cat => {
        const pill = document.createElement("button");
        pill.className = "category-pill";
        pill.dataset.id = cat.id;
        const icon = CAT_ICONS[cat.name] || "🏷";
        pill.innerHTML = `<span class="category-pill-icon">${icon}</span> ${cat.name}`;
        pill.addEventListener("click", () => filterByCategory(cat.id, pill));
        strip.appendChild(pill);
    });
}

// ── Render: Featured Grid ─────────────────────────────────────────────────────

function renderFeatured(products) {
    const grid = document.getElementById("featuredGrid");
    const seeMoreBtn = document.getElementById("seeMoreBtn");
    const seeMoreMobile = document.getElementById("seeMoreMobile");
    const subtitle = document.getElementById("featuredSubtitle");
    if (!grid) return;

    const hasMore = products.length > FEATURED_LIMIT;
    const toShow = products.slice(0, FEATURED_LIMIT);

    if (seeMoreBtn) seeMoreBtn.style.display = hasMore ? "inline-flex" : "none";
    if (seeMoreMobile) seeMoreMobile.style.display = hasMore ? "block" : "none";
    if (subtitle) {
        subtitle.textContent = activeCategory
            ? `${products.length} product${products.length !== 1 ? "s" : ""} in this category`
            : "Handpicked from our latest listings";
    }

    if (toShow.length === 0) {
        grid.innerHTML = `<div class="featured-empty"><span>🛍</span><p>No products found in this category.</p></div>`;
        return;
    }

    grid.innerHTML = toShow.map(p => `
        <div class="featured-card" onclick="window.location.href='/product/${p.id}'" style="cursor:pointer;">
            <div class="featured-card-img">
                ${p.image_name
                    ? `<img src="/static/uploads/product_images/${p.image_name}" alt="${escHtml(p.name)}" loading="lazy">`
                    : `<div class="featured-card-no-img">📷</div>`
                }
            </div>
            <div class="featured-card-body">
                <div class="featured-card-cat">${escHtml(p.category_name || "Uncategorized")}</div>
                <h4 class="featured-card-name">${escHtml(p.name)}</h4>
                <p class="featured-card-desc">${escHtml(p.description || "No description provided.")}</p>
                <div class="featured-card-footer">
                    <span class="featured-card-price">৳${parseFloat(p.price).toLocaleString("en-BD", {minimumFractionDigits: 2})}</span>
                    <span class="featured-card-stock ${p.stock_quantity === 0 ? 'out' : ''}">
                        ${p.stock_quantity === 0 ? "Out of stock" : "In stock"}
                    </span>
                </div>
            </div>
        </div>
    `).join("");
}

// ── Filter by category ────────────────────────────────────────────────────────

function filterByCategory(categoryId, clickedPill) {
    activeCategory = categoryId;

    // Update active pill styling
    document.querySelectorAll(".category-pill").forEach(p => p.classList.remove("active"));
    if (clickedPill) clickedPill.classList.add("active");

    const filtered = categoryId
        ? allProducts.filter(p => String(p.category_id) === String(categoryId))
        : allProducts;

    renderFeatured(filtered);

    // Smooth scroll to featured section
    document.getElementById("featured")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Navbar search (live filter) ───────────────────────────────────────────────

function handleNavSearch(term) {
    if (!term.trim()) {
        renderFeatured(allProducts);
        return;
    }
    const lower = term.toLowerCase();
    const filtered = allProducts.filter(p =>
        p.name.toLowerCase().includes(lower) ||
        (p.description && p.description.toLowerCase().includes(lower)) ||
        (p.category_name && p.category_name.toLowerCase().includes(lower))
    );
    renderFeatured(filtered);
    document.getElementById("featured")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Event Listeners ───────────────────────────────────────────────────────────

function setupEventListeners() {
    const navSearch = document.getElementById("navSearchInput");
    if (navSearch) {
        navSearch.addEventListener("input", e => handleNavSearch(e.target.value));
    }

    document.getElementById("logoutBtn")?.addEventListener("click", async function () {
        try {
            const res = await fetch("/api/logout", { method: "POST" });
            if (res.ok) window.location.href = "/login";
        } catch (err) {
            console.error("Logout failed:", err);
        }
    });
}

// ── Util ──────────────────────────────────────────────────────────────────────

function escHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

// ── Start ─────────────────────────────────────────────────────────────────────

init();