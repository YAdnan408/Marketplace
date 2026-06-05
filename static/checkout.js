// ── Shipping config (must match cart_page.js) ─────────────────────────────────

const SHIPPING = {
    inside_dhaka:  80,
    outside_dhaka: 130
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function getShippingCost() {
    const zone = sessionStorage.getItem("mp_shipping_zone");
    if (zone && SHIPPING[zone] !== undefined) return SHIPPING[zone];
    return 0;   // default to 0 (free) if no zone selected
}

function getShippingLabel() {
    const zone = sessionStorage.getItem("mp_shipping_zone");
    if (zone === "inside_dhaka")  return "Inside Dhaka — ৳80.00";
    if (zone === "outside_dhaka") return "Outside Dhaka — ৳130.00";
    return "Free";
}

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
    const items = Cart.get();

    if (items.length === 0) {
        document.getElementById("checkoutEmpty").classList.remove("hidden");
        return;
    }

    document.getElementById("checkoutLayout").classList.remove("hidden");
    renderOrderSummary(items);
    await prefillProfileAddress();
    setupEventListeners();
}

// ── Render order summary ──────────────────────────────────────────────────────

function renderOrderSummary(items) {
    const list         = document.getElementById("checkoutItemsList");
    const totalItems   = items.reduce((s, i) => s + i.qty, 0);
    const subtotal     = Cart.total();
    const shippingCost = getShippingCost();
    const total        = subtotal + shippingCost;

    list.innerHTML = items.map(item => `
        <div class="checkout-item">
            <div class="checkout-item-img">
                ${item.image_name
                    ? `<img src="/static/uploads/product_images/${item.image_name}" alt="${escHtml(item.name)}">`
                    : `<span>📷</span>`
                }
            </div>
            <div class="checkout-item-info">
                <span class="checkout-item-name">${escHtml(item.name)}</span>
                <span class="checkout-item-qty">Qty: ${item.qty}</span>
            </div>
            <span class="checkout-item-price">
                ৳${(item.price * item.qty).toLocaleString("en-BD", { minimumFractionDigits: 2 })}
            </span>
        </div>
    `).join("");

    document.getElementById("checkoutItemCount").textContent = totalItems;
    document.getElementById("checkoutSubtotal").textContent =
        `৳${subtotal.toLocaleString("en-BD", { minimumFractionDigits: 2 })}`;

    // Show correct shipping cost
    const shippingEl = document.getElementById("checkoutShipping");
    if (shippingEl) {
        shippingEl.textContent = shippingCost > 0
            ? `৳${shippingCost.toLocaleString("en-BD", { minimumFractionDigits: 2 })}`
            : "Free";
    }

    document.getElementById("checkoutTotal").textContent =
        `৳${total.toLocaleString("en-BD", { minimumFractionDigits: 2 })}`;
}

// ── Prefill address from profile ──────────────────────────────────────────────

async function prefillProfileAddress() {
    try {
        const res = await fetch("/api/profile");
        if (!res.ok) return;
        const profile = await res.json();
        if (profile.name)         document.getElementById("shippingName").value    = profile.name;
        if (profile.phone_number) document.getElementById("shippingPhone").value   = profile.phone_number;
        if (profile.address)      document.getElementById("shippingAddress").value = profile.address;
    } catch {
        // Silently fail — user can fill manually
    }
}

// ── Place order ───────────────────────────────────────────────────────────────

async function placeOrder() {
    const btnText   = document.getElementById("placeOrderBtnText");
    const btnLoader = document.getElementById("placeOrderBtnLoader");
    const errorEl   = document.getElementById("checkoutError");

    // Collect shipping details
    const name    = document.getElementById("shippingName").value.trim();
    const phone   = document.getElementById("shippingPhone").value.trim();
    const address = document.getElementById("shippingAddress").value.trim();

    // Validate
    errorEl.classList.add("hidden");

    if (!name) {
        showError("Please enter your full name.");
        return;
    }
    if (!address) {
        showError("Please enter your delivery address.");
        return;
    }

    const cartItems = Cart.get();
    if (cartItems.length === 0) {
        showError("Your cart is empty.");
        return;
    }

    // Build full shipping address string
    const fullAddress = phone ? `${name}\n${phone}\n${address}` : `${name}\n${address}`;

    // Show loading
    btnText.textContent = "Placing order…";
    btnLoader.style.display = "inline-block";
    document.getElementById("placeOrderBtn").disabled = true;

    try {
        const res = await fetch("/api/orders/checkout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cart_items:       cartItems,
                shipping_address: fullAddress,
                shipping_cost:    getShippingCost()    // send shipping cost to backend
            })
        });

        const json = await res.json();

        if (!res.ok) {
            showError(json.error || "Order could not be placed. Please try again.");
            return;
        }

        // Success — clear cart + shipping zone, redirect to confirmation
        Cart.clear();
        sessionStorage.removeItem("mp_shipping_zone");
        window.location.href = `/orders?new=${json.order.order_id}`;

    } catch (err) {
        showError("Network error. Please check your connection and try again.");
    } finally {
        btnText.textContent = "Place Order →";
        btnLoader.style.display = "none";
        document.getElementById("placeOrderBtn").disabled = false;
    }
}

// ── Use profile address button ────────────────────────────────────────────────

document.getElementById("useProfileAddressBtn")?.addEventListener("click", prefillProfileAddress);

// ── Event listeners ───────────────────────────────────────────────────────────

function setupEventListeners() {
    document.getElementById("placeOrderBtn").addEventListener("click", placeOrder);
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function showError(msg) {
    const el = document.getElementById("checkoutError");
    el.textContent = msg;
    el.classList.remove("hidden");
    el.scrollIntoView({ behavior: "smooth", block: "center" });
}

function escHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

// ── Start ─────────────────────────────────────────────────────────────────────

init();