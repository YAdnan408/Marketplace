// ── Init ──────────────────────────────────────────────────────────────────────

let currentProduct = null;
let qty = 1;

async function init() {
    const productId = getProductIdFromUrl();
    if (!productId) {
        showError("Invalid product URL.");
        return;
    }
    await loadProduct(productId);
    setupQtyControls();
}

// ── Get product ID from URL ───────────────────────────────────────────────────

function getProductIdFromUrl() {
    // URL pattern: /product/<id>
    const parts = window.location.pathname.split("/");
    const id = parseInt(parts[parts.length - 1]);
    return isNaN(id) ? null : id;
}

// ── Fetch product ─────────────────────────────────────────────────────────────

async function loadProduct(productId) {
    try {
        const res = await fetch(`/api/product/${productId}`);

        if (res.status === 401 || res.status === 403) {
            window.location.href = "/login";
            return;
        }

        if (res.status === 404) {
            showError("This product does not exist or has been removed.");
            return;
        }

        if (!res.ok) {
            showError("Failed to load product. Please try again.");
            return;
        }

        const product = await res.json();
        currentProduct = product;
        renderProduct(product);

    } catch (err) {
        showError("Something went wrong. Please refresh the page.");
        console.error(err);
    }
}

// ── Render ────────────────────────────────────────────────────────────────────

function renderProduct(p) {
    // Breadcrumb
    document.getElementById("breadcrumbName").textContent = p.name;
    document.title = `${p.name} – Marketplace`;

    // Image
    const img = document.getElementById("pdImage");
    const placeholder = document.getElementById("pdImagePlaceholder");
    if (p.image_name) {
        img.src = `/static/uploads/product_images/${p.image_name}`;
        img.alt = p.name;
        img.classList.remove("hidden");
    } else {
        placeholder.classList.remove("hidden");
    }

    // Category badge on image
    document.getElementById("pdCategoryBadge").textContent = p.category_name || "Uncategorized";

    // Title, category, price
    document.getElementById("pdCategory").textContent = p.category_name || "Uncategorized";
    document.getElementById("pdTitle").textContent = p.name;
    document.getElementById("pdPrice").textContent =
        `৳${parseFloat(p.price).toLocaleString("en-BD", { minimumFractionDigits: 2 })}`;

    // Stock badge
    const stockBadge = document.getElementById("pdStockBadge");
    if (p.stock_quantity === 0) {
        stockBadge.textContent = "Out of Stock";
        stockBadge.className = "pd-stock-badge out";
    } else if (p.stock_quantity <= 5) {
        stockBadge.textContent = `Only ${p.stock_quantity} left!`;
        stockBadge.className = "pd-stock-badge low";
    } else {
        stockBadge.textContent = "In Stock";
        stockBadge.className = "pd-stock-badge in";
    }

    // Description
    document.getElementById("pdDescription").textContent =
        p.description || "No description provided for this product.";

    // Details grid
    document.getElementById("pdDetailCategory").textContent = p.category_name || "Uncategorized";
    document.getElementById("pdDetailStock").textContent =
        p.stock_quantity > 0 ? `${p.stock_quantity} units available` : "Out of stock";
    document.getElementById("pdDetailDate").textContent = formatDate(p.created_at);
    document.getElementById("pdDetailId").textContent = `#${p.id}`;

    // Seller card
    const sellerName = p.seller_name || "Unknown Seller";
    document.getElementById("pdSellerName").textContent = sellerName;
    document.getElementById("pdSellerMeta").textContent = p.seller_email || "";
    document.getElementById("pdSellerInitial").textContent = sellerName.charAt(0).toUpperCase();

    if (p.seller_image) {
        const sellerImg = document.getElementById("pdSellerImg");
        sellerImg.src = `/static/uploads/profile_images/${p.seller_image}`;
        sellerImg.alt = sellerName;
        sellerImg.classList.remove("hidden");
        document.getElementById("pdSellerInitial").classList.add("hidden");
    }

    // Add to cart button
    const addCartBtn = document.getElementById("pdAddCart");
    const cartNote = document.getElementById("pdCartNote");
    if (p.stock_quantity > 0) {
        addCartBtn.disabled = false;
        addCartBtn.classList.remove("disabled");
        cartNote.textContent = "Cart functionality coming soon.";
        cartNote.className = "pd-cart-note";
    } else {
        addCartBtn.disabled = true;
        addCartBtn.classList.add("disabled");
        document.getElementById("pdAddCartText").textContent = "Out of Stock";
        cartNote.textContent = "This product is currently unavailable.";
        cartNote.className = "pd-cart-note out";
        document.getElementById("pdQtyMinus").disabled = true;
        document.getElementById("pdQtyPlus").disabled = true;
    }

    // Show layout, hide loading
    document.getElementById("pdLoading").classList.add("hidden");
    document.getElementById("pdLayout").classList.remove("hidden");
}

// ── Quantity controls ─────────────────────────────────────────────────────────

function setupQtyControls() {
    document.getElementById("pdQtyMinus").addEventListener("click", () => {
        if (qty > 1) {
            qty--;
            document.getElementById("pdQtyVal").textContent = qty;
        }
    });

    document.getElementById("pdQtyPlus").addEventListener("click", () => {
        const maxStock = currentProduct?.stock_quantity ?? 99;
        if (qty < maxStock) {
            qty++;
            document.getElementById("pdQtyVal").textContent = qty;
        }
    });

    document.getElementById("pdAddCart").addEventListener("click", () => {
        // Cart not implemented yet — placeholder
        const btn = document.getElementById("pdAddCart");
        const originalText = document.getElementById("pdAddCartText").textContent;
        document.getElementById("pdAddCartText").textContent = "✓ Added!";
        btn.style.background = "var(--mocha)";
        setTimeout(() => {
            document.getElementById("pdAddCartText").textContent = originalText;
            btn.style.background = "";
        }, 1500);
    });
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function showError(msg) {
    document.getElementById("pdLoading").classList.add("hidden");
    document.getElementById("pdErrorMsg").textContent = msg;
    document.getElementById("pdError").classList.remove("hidden");
}

function formatDate(dateStr) {
    if (!dateStr) return "—";
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
}

// ── Start ─────────────────────────────────────────────────────────────────────

init();