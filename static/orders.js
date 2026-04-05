// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
    await loadOrders();
    checkForNewOrder();
}

// ── Load orders ───────────────────────────────────────────────────────────────

async function loadOrders() {
    try {
        const res = await fetch("/api/orders");

        if (res.status === 401 || res.status === 403) {
            window.location.href = "/login";
            return;
        }

        const orders = await res.json();

        document.getElementById("ordersLoading").classList.add("hidden");

        if (orders.length === 0) {
            document.getElementById("ordersEmpty").classList.remove("hidden");
            return;
        }

        document.getElementById("ordersCount").textContent =
            `${orders.length} order${orders.length !== 1 ? "s" : ""}`;

        renderOrders(orders);
        document.getElementById("ordersList").classList.remove("hidden");

    } catch (err) {
        document.getElementById("ordersLoading").innerHTML =
            `<p style="color:var(--text-muted)">Failed to load orders. Please refresh.</p>`;
    }
}

// ── Render orders ─────────────────────────────────────────────────────────────

function renderOrders(orders) {
    const list = document.getElementById("ordersList");

    list.innerHTML = orders.map(order => `
        <div class="order-card ${isNewOrder(order.id) ? 'order-card-new' : ''}" id="order-${order.id}">

            <div class="order-card-header">
                <div class="order-card-meta">
                    <span class="order-id">Order #${order.id}</span>
                    <span class="order-date">${order.created_at}</span>
                </div>
                <span class="order-status order-status-${order.status}">${capitalise(order.status)}</span>
            </div>

            <div class="order-items-preview">
                ${order.items.map(item => `
                    <div class="order-item-row">
                        <div class="order-item-img">
                            ${item.image_name
                                ? `<img src="/static/uploads/product_images/${item.image_name}" alt="${escHtml(item.product_name)}">`
                                : `<span>📷</span>`
                            }
                        </div>
                        <div class="order-item-info">
                            <span class="order-item-name">${escHtml(item.product_name)}</span>
                            <span class="order-item-qty">Qty: ${item.quantity} × ৳${item.unit_price.toLocaleString("en-BD", { minimumFractionDigits: 2 })}</span>
                        </div>
                        <span class="order-item-subtotal">
                            ৳${item.subtotal.toLocaleString("en-BD", { minimumFractionDigits: 2 })}
                        </span>
                    </div>
                `).join("")}
            </div>

            <div class="order-card-footer">
                <div class="order-shipping">
                    <span class="order-shipping-label">Shipping to:</span>
                    <span class="order-shipping-addr">${escHtml(order.shipping_address.replace(/\n/g, ", "))}</span>
                </div>
                <div class="order-total">
                    <span>Total</span>
                    <strong>৳${order.total_price.toLocaleString("en-BD", { minimumFractionDigits: 2 })}</strong>
                </div>
            </div>

        </div>
    `).join("");
}

// ── New order banner ──────────────────────────────────────────────────────────

function checkForNewOrder() {
    const params = new URLSearchParams(window.location.search);
    const newOrderId = params.get("new");
    if (!newOrderId) return;

    // Show success banner at top
    const banner = document.createElement("div");
    banner.className = "order-success-banner";
    banner.innerHTML = `
        <span class="order-success-icon">✅</span>
        <div>
            <strong>Order #${newOrderId} placed successfully!</strong>
            <p>We've received your order. It will be processed shortly.</p>
        </div>
    `;
    document.querySelector(".orders-page").insertAdjacentElement("afterbegin", banner);

    // Scroll to the new order card after render
    setTimeout(() => {
        const card = document.getElementById(`order-${newOrderId}`);
        if (card) card.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 300);

    // Clean URL
    window.history.replaceState({}, "", "/orders");
}

function isNewOrder(orderId) {
    const params = new URLSearchParams(window.location.search);
    return String(params.get("new")) === String(orderId);
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function capitalise(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
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