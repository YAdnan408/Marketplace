// ── Shipping config ───────────────────────────────────────────────────────────

const SHIPPING = {
    inside_dhaka:  80,
    outside_dhaka: 130
};

// ── State ─────────────────────────────────────────────────────────────────────

let activeShippingZone = "";   // "", "inside_dhaka", or "outside_dhaka"

// ── Init ──────────────────────────────────────────────────────────────────────

function init() {
    restoreShippingZone();
    renderCart();
    setupEventListeners();
}

// ── Restore saved shipping zone from sessionStorage ───────────────────────────

function restoreShippingZone() {
    const saved = sessionStorage.getItem("mp_shipping_zone");
    if (saved && SHIPPING[saved] !== undefined) {
        activeShippingZone = saved;
    }
}

// ── Shipping cost helper ──────────────────────────────────────────────────────

function getShippingCost() {
    if (!activeShippingZone) return null;       // not selected yet
    return SHIPPING[activeShippingZone] || 0;
}

// ── Render cart ───────────────────────────────────────────────────────────────

function renderCart() {
    const items       = Cart.get();
    const cartEmpty   = document.getElementById("cartEmpty");
    const cartContent = document.getElementById("cartContent");
    const cartItemCount = document.getElementById("cartItemCount");

    if (items.length === 0) {
        cartEmpty.classList.remove("hidden");
        cartContent.classList.add("hidden");
        cartItemCount.textContent = "";
        return;
    }

    cartEmpty.classList.add("hidden");
    cartContent.classList.remove("hidden");

    const totalItems = items.reduce((sum, i) => sum + i.qty, 0);
    cartItemCount.textContent = `${totalItems} item${totalItems !== 1 ? "s" : ""}`;

    renderItems(items);
    renderSummary(items);
    syncShippingSelector();
}

function renderItems(items) {
    const container = document.getElementById("cartItems");

    container.innerHTML = items.map(item => `
        <div class="cart-item" data-id="${item.id}">
            <div class="cart-item-image">
                ${item.image_name
                    ? `<img src="/static/uploads/product_images/${item.image_name}" alt="${escHtml(item.name)}">`
                    : `<div class="cart-item-no-image">📷</div>`
                }
            </div>
            <div class="cart-item-info">
                <div class="cart-item-category">${escHtml(item.category_name)}</div>
                <h4 class="cart-item-name">${escHtml(item.name)}</h4>
                <div class="cart-item-price">৳${item.price.toLocaleString("en-BD", { minimumFractionDigits: 2 })}</div>
            </div>
            <div class="cart-item-controls">
                <div class="cart-qty-wrap">
                    <button class="cart-qty-btn" onclick="changeQty(${item.id}, ${item.qty - 1})" ${item.qty <= 1 ? "disabled" : ""}>−</button>
                    <span class="cart-qty-val">${item.qty}</span>
                    <button class="cart-qty-btn" onclick="changeQty(${item.id}, ${item.qty + 1})" ${item.qty >= item.stock_quantity ? "disabled" : ""}>+</button>
                </div>
                <div class="cart-item-subtotal">৳${(item.price * item.qty).toLocaleString("en-BD", { minimumFractionDigits: 2 })}</div>
                <button class="cart-remove-btn" onclick="removeItem(${item.id})" title="Remove">✕</button>
            </div>
        </div>
    `).join("");
}

function renderSummary(items) {
    const totalItems   = items.reduce((sum, i) => sum + i.qty, 0);
    const subtotal     = Cart.total();
    const shippingCost = getShippingCost();

    // Subtotal
    document.getElementById("summaryItemCount").textContent = totalItems;
    document.getElementById("summarySubtotal").textContent  =
        `৳${subtotal.toLocaleString("en-BD", { minimumFractionDigits: 2 })}`;

    // Shipping row
    const shippingEl = document.getElementById("summaryShipping");
    const hintEl     = document.getElementById("shippingHint");

    if (shippingCost === null) {
        // No zone selected yet
        shippingEl.textContent  = "—";
        shippingEl.className    = "cart-shipping-value cart-shipping-pending";
        hintEl.classList.remove("hidden");
    } else {
        shippingEl.textContent  = `৳${shippingCost.toLocaleString("en-BD", { minimumFractionDigits: 2 })}`;
        shippingEl.className    = "cart-shipping-value cart-shipping-amount";
        hintEl.classList.add("hidden");
    }

    // Total = subtotal + shipping (only add shipping when selected)
    const total = subtotal + (shippingCost ?? 0);
    document.getElementById("summaryTotal").textContent =
        `৳${total.toLocaleString("en-BD", { minimumFractionDigits: 2 })}`;
}

// ── Sync the select element to match current state ────────────────────────────

function syncShippingSelector() {
    const select = document.getElementById("shippingZone");
    if (select) select.value = activeShippingZone;
}

// ── Actions ───────────────────────────────────────────────────────────────────

function changeQty(productId, newQty) {
    Cart.update(productId, newQty);
    renderCart();
}

function removeItem(productId) {
    Cart.remove(productId);
    renderCart();
}

// ── Event Listeners ───────────────────────────────────────────────────────────

function setupEventListeners() {

    // Shipping zone selector
    document.getElementById("shippingZone").addEventListener("change", function () {
        activeShippingZone = this.value;
        // Persist across page refreshes within the session
        if (activeShippingZone) {
            sessionStorage.setItem("mp_shipping_zone", activeShippingZone);
        } else {
            sessionStorage.removeItem("mp_shipping_zone");
        }
        renderSummary(Cart.get());
    });

    // Clear cart
    document.getElementById("clearCartBtn").addEventListener("click", function () {
        if (confirm("Are you sure you want to clear your entire cart?")) {
            Cart.clear();
            renderCart();
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