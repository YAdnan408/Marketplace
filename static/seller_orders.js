// ── State ─────────────────────────────────────────────────────────────────────

let allOrders = [];
let activeFilter = "";   // "", "pending", "approved"

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
    await loadOrders();
    setupTabs();
    setupLogout();
}

// ── Fetch orders ──────────────────────────────────────────────────────────────

async function loadOrders() {
    try {
        const res = await fetch("/api/orders/");

        if (res.status === 401 || res.status === 403) {
            window.location.href = "/login";
            return;
        }

        allOrders = await res.json();

        document.getElementById("ordersLoading").classList.add("hidden");
        renderOrders(getFiltered());

    } catch (err) {
        document.getElementById("ordersLoading").innerHTML =
            `<p style="color:var(--text-muted)">Failed to load orders. Please refresh.</p>`;
    }
}

// ── Filter ────────────────────────────────────────────────────────────────────

function getFiltered() {
    if (!activeFilter) return allOrders;
    return allOrders.filter(o => o.status === activeFilter);
}

// ── Render ────────────────────────────────────────────────────────────────────

function renderOrders(orders) {
    const list  = document.getElementById("ordersList");
    const empty = document.getElementById("ordersEmpty");
    const count = document.getElementById("ordersCount");

    count.textContent = `${orders.length} order${orders.length !== 1 ? "s" : ""}`;

    if (orders.length === 0) {
        list.classList.add("hidden");
        empty.classList.remove("hidden");
        return;
    }

    empty.classList.add("hidden");
    list.classList.remove("hidden");

    list.innerHTML = orders.map(order => `
        <div class="order-card" id="order-${order.id}">

            <div class="order-card-header">
                <div class="order-card-meta">
                    <span class="order-id">Order #${order.id}</span>
                    <span class="order-date">${order.created_at}</span>
                </div>
                <span class="order-status order-status-${order.status}">${capitalise(order.status)}</span>
            </div>

            <!-- Customer info -->
            <div class="seller-order-customer">
                <span class="seller-order-customer-label">Customer:</span>
                <span class="seller-order-customer-name">${escHtml(order.customer_name)}</span>
                <span class="seller-order-customer-email">${escHtml(order.customer_email)}</span>
            </div>

            <!-- Items (highlight seller's own items) -->
            <div class="order-items-preview">
                ${order.items.map(item => `
                    <div class="order-item-row ${item.is_mine ? "order-item-mine" : "order-item-other"}">
                        <div class="order-item-img">
                            ${item.image_name
                                ? `<img src="/static/uploads/product_images/${item.image_name}" alt="${escHtml(item.product_name)}">`
                                : `<span>📷</span>`
                            }
                        </div>
                        <div class="order-item-info">
                            <span class="order-item-name">${escHtml(item.product_name)}</span>
                            <span class="order-item-qty">Qty: ${item.quantity} × ৳${item.unit_price.toLocaleString("en-BD", { minimumFractionDigits: 2 })}</span>
                            ${!item.is_mine ? `<span class="order-item-other-label">Other seller's item</span>` : ""}
                        </div>
                        <span class="order-item-subtotal">
                            ৳${item.subtotal.toLocaleString("en-BD", { minimumFractionDigits: 2 })}
                        </span>
                    </div>
                `).join("")}
            </div>

            <div class="order-card-footer">
                <div class="order-shipping">
                    <span class="order-shipping-label">Ship to:</span>
                    <span class="order-shipping-addr">${escHtml(order.shipping_address.replace(/\n/g, ", "))}</span>
                </div>
                <div class="seller-order-totals">
                    <div class="seller-order-subtotal">
                        Your items: <strong>৳${order.seller_subtotal.toLocaleString("en-BD", { minimumFractionDigits: 2 })}</strong>
                    </div>
                    ${order.status === "pending" ? `
                        <button
                            class="seller-approve-btn"
                            onclick="approveOrder(${order.id}, this)"
                        >
                            ✓ Approve Order
                        </button>
                    ` : `
                        <div class="seller-order-approved-badge">
                            ${order.status === "approved" ? "✓ Approved" : capitalise(order.status)}
                        </div>
                    `}
                </div>
            </div>

        </div>
    `).join("");
}

// ── Approve order ─────────────────────────────────────────────────────────────

async function approveOrder(orderId, btn) {
    btn.disabled = true;
    btn.textContent = "Approving…";

    try {
        const res = await fetch(`/api/orders/approve/${orderId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
        });

        const json = await res.json();

        if (!res.ok) {
            btn.disabled = false;
            btn.textContent = "✓ Approve Order";
            showToast(json.error?.message || "Could not approve order.", "error");
            return;
        }

        // Update local state and re-render
        const order = allOrders.find(o => o.id === orderId);
        if (order) order.status = json.order.status;

        renderOrders(getFiltered());
        showToast(`Order #${orderId} approved successfully.`, "success");

    } catch (err) {
        btn.disabled = false;
        btn.textContent = "✓ Approve Order";
        showToast("Network error. Please try again.", "error");
    }
}

// ── Tabs ──────────────────────────────────────────────────────────────────────

function setupTabs() {
    document.querySelectorAll(".seller-orders-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".seller-orders-tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            activeFilter = tab.dataset.status;
            renderOrders(getFiltered());
        });
    });
}

// ── Toast notification ────────────────────────────────────────────────────────

function showToast(msg, type = "success") {
    const existing = document.getElementById("sellerToast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.id = "sellerToast";
    toast.className = `seller-toast seller-toast-${type}`;
    toast.textContent = msg;
    document.body.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add("seller-toast-show"));

    setTimeout(() => {
        toast.classList.remove("seller-toast-show");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ── Logout ────────────────────────────────────────────────────────────────────

function setupLogout() {
    document.getElementById("logoutBtn")?.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/logout", { method: "POST" });
            if (res.ok) window.location.href = "/login";
        } catch (err) {
            console.error("Logout failed:", err);
        }
    });
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