// ── State ─────────────────────────────────────────────────────────────────────
let allProducts     = [];
let activeCategory  = "";
let activePriceMin  = null;   // null = no filter
let activePriceMax  = null;
let activeSort      = "default";

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
    await loadProducts();

    // Honour ?cat= URL param
    const params = new URLSearchParams(window.location.search);
    const cat = params.get("cat");
    if (cat) {
        const pill = document.querySelector(`.category-pill[data-category="${cat}"]`);
        if (pill) {
            document.querySelectorAll(".category-pill").forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            activeCategory = cat;
        }
    }

    setupCategoryPills();
    setupSearch();
    setupPriceFilter();
    setupPresetPills();
    setupSort();
    setupClearFilters();
    setupLogout();
    renderAll(getFiltered());
}

// ── Fetch ─────────────────────────────────────────────────────────────────────
async function loadProducts() {
    try {
        const res = await fetch("/api/products");
        if (res.status === 403) { window.location.href = "/login"; return; }
        allProducts = await res.json();
    } catch (err) {
        document.getElementById("pageGrid").innerHTML =
            `<div class="featured-empty"><span>⚠️</span><p>Failed to load. Please refresh.</p></div>`;
    }
}

// ── Render ─────────────────────────────────────────────────────────────────────
function renderAll(products) {
    const grid  = document.getElementById("pageGrid");
    const count = document.getElementById("pageCount");
    if (count) count.textContent = `${products.length} product${products.length !== 1 ? "s" : ""}`;

    if (products.length === 0) {
        grid.innerHTML = `<div class="featured-empty"><span>🛍</span><p>No products match your filters.</p></div>`;
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

// ── Filter + Sort pipeline ────────────────────────────────────────────────────
function getFiltered() {
    const search = document.getElementById("pageSearch").value.toLowerCase().trim();

    let results = allProducts.filter(p => {
        // Category filter
        const matchesCat = !activeCategory || String(p.category_id) === activeCategory;

        // Search filter
        const matchesSearch = !search ||
            p.name.toLowerCase().includes(search) ||
            (p.description && p.description.toLowerCase().includes(search));

        // Price filter
        const price = parseFloat(p.price);
        const aboveMin = activePriceMin === null || price >= activePriceMin;
        const belowMax = activePriceMax === null || price <= activePriceMax;

        return matchesCat && matchesSearch && aboveMin && belowMax;
    });

    // Sort
    switch (activeSort) {
        case "price_asc":
            results.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
            break;
        case "price_desc":
            results.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
            break;
        case "name_asc":
            results.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case "name_desc":
            results.sort((a, b) => b.name.localeCompare(a.name));
            break;
        default:
            // keep API order (newest first)
            break;
    }

    return results;
}

// ── Apply price filter and update UI ─────────────────────────────────────────
function applyPriceFilter() {
    const minVal = document.getElementById("priceMin").value.trim();
    const maxVal = document.getElementById("priceMax").value.trim();

    activePriceMin = minVal !== "" ? parseFloat(minVal) : null;
    activePriceMax = maxVal !== "" ? parseFloat(maxVal) : null;

    // Validate: min can't exceed max
    if (activePriceMin !== null && activePriceMax !== null && activePriceMin > activePriceMax) {
        activePriceMin = null;
        activePriceMax = null;
        document.getElementById("priceMin").value = "";
        document.getElementById("priceMax").value = "";
    }

    updateFilterUI();
    renderAll(getFiltered());
}

// ── Update filter tags row and clear button visibility ────────────────────────
function updateFilterUI() {
    const tags       = [];
    const tagsInner  = document.getElementById("filterTagsInner");
    const tagsRow    = document.getElementById("filterTagsRow");
    const clearBtn   = document.getElementById("clearFiltersBtn");

    if (activePriceMin !== null || activePriceMax !== null) {
        let label = "৳";
        if (activePriceMin !== null && activePriceMax !== null) {
            label += `${activePriceMin.toLocaleString()} – ${activePriceMax.toLocaleString()}`;
        } else if (activePriceMin !== null) {
            label += `${activePriceMin.toLocaleString()}+`;
        } else {
            label += `Up to ${activePriceMax.toLocaleString()}`;
        }
        tags.push({ label, action: "clearPrice" });
    }

    if (activeSort !== "default") {
        const sortLabels = {
            price_asc:  "Price: Low–High",
            price_desc: "Price: High–Low",
            name_asc:   "Name: A–Z",
            name_desc:  "Name: Z–A"
        };
        tags.push({ label: sortLabels[activeSort], action: "clearSort" });
    }

    const hasFilters = tags.length > 0;

    tagsRow.classList.toggle("hidden", !hasFilters);
    clearBtn.classList.toggle("hidden", !hasFilters);

    tagsInner.innerHTML = tags.map(t => `
        <span class="filter-tag" data-action="${t.action}">
            ${t.label} <button class="filter-tag-remove">✕</button>
        </span>
    `).join("");

    // Wire tag remove buttons
    tagsInner.querySelectorAll(".filter-tag").forEach(tag => {
        tag.querySelector(".filter-tag-remove").addEventListener("click", () => {
            if (tag.dataset.action === "clearPrice") clearPriceFilter();
            if (tag.dataset.action === "clearSort")  clearSortFilter();
        });
    });
}

function clearPriceFilter() {
    activePriceMin = null;
    activePriceMax = null;
    document.getElementById("priceMin").value = "";
    document.getElementById("priceMax").value = "";
    // Deactivate any active preset pill
    document.querySelectorAll(".filter-preset-pill").forEach(p => p.classList.remove("active"));
    updateFilterUI();
    renderAll(getFiltered());
}

function clearSortFilter() {
    activeSort = "default";
    document.getElementById("sortSelect").value = "default";
    updateFilterUI();
    renderAll(getFiltered());
}

function clearAllFilters() {
    clearPriceFilter();
    clearSortFilter();
}

// ── Setup functions ───────────────────────────────────────────────────────────
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

function setupPriceFilter() {
    document.getElementById("applyPriceBtn").addEventListener("click", applyPriceFilter);

    // Also apply on Enter key
    ["priceMin", "priceMax"].forEach(id => {
        document.getElementById(id).addEventListener("keydown", e => {
            if (e.key === "Enter") applyPriceFilter();
        });
    });
}

function setupPresetPills() {
    document.querySelectorAll(".filter-preset-pill").forEach(pill => {
        pill.addEventListener("click", () => {
            // Toggle: clicking active preset deactivates it
            if (pill.classList.contains("active")) {
                pill.classList.remove("active");
                clearPriceFilter();
                return;
            }

            document.querySelectorAll(".filter-preset-pill").forEach(p => p.classList.remove("active"));
            pill.classList.add("active");

            const min = pill.dataset.min !== "" ? parseFloat(pill.dataset.min) : null;
            const max = pill.dataset.max !== "" ? parseFloat(pill.dataset.max) : null;

            activePriceMin = min;
            activePriceMax = max;

            // Sync manual inputs
            document.getElementById("priceMin").value = min !== null ? min : "";
            document.getElementById("priceMax").value = max !== null ? max : "";

            updateFilterUI();
            renderAll(getFiltered());
        });
    });
}

function setupSort() {
    document.getElementById("sortSelect").addEventListener("change", e => {
        activeSort = e.target.value;
        updateFilterUI();
        renderAll(getFiltered());
    });
}

function setupClearFilters() {
    document.getElementById("clearFiltersBtn").addEventListener("click", clearAllFilters);
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

// ── Util ──────────────────────────────────────────────────────────────────────
function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
}

// Products page layout CSS (keeps layout self-contained)
document.addEventListener("DOMContentLoaded", () => {
    const style = document.createElement("style");
    style.textContent = `
        .products-page { padding: 40px 0 72px; background: var(--cream); min-height: 60vh; }
        .products-page-inner { max-width: 1200px; margin: 0 auto; padding: 0 44px; }
        .products-page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px; gap: 20px; flex-wrap: wrap; }
        .products-page-title { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; color: var(--espresso); }
        .products-page-count { font-size: 0.85rem; color: var(--text-muted); }
        @media (max-width: 768px) { .products-page-inner { padding: 0 20px; } .products-page-header { flex-direction: column; align-items: flex-start; } }
    `;
    document.head.appendChild(style);
});

init();