/* ═══════════════════════════════════════════════════════════════════════════
   cart.js  —  Cookie-based cart for Marketplace
   
   Cart is stored as a JSON string in a cookie named "mp_cart".
   Each item: { id, name, price, image_name, category_name, stock_quantity, qty }
   
   Public API (used by other JS files):
     Cart.add(product, qty)
     Cart.remove(productId)
     Cart.update(productId, newQty)
     Cart.get()
     Cart.count()
     Cart.clear()
     Cart.total()
═══════════════════════════════════════════════════════════════════════════ */

const CART_COOKIE = "mp_cart";
const CART_EXPIRY_DAYS = 7;

// ── Cookie helpers ────────────────────────────────────────────────────────────

function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return match ? decodeURIComponent(match[1]) : null;
}

function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

// ── Cart core ─────────────────────────────────────────────────────────────────

const Cart = {

    // Read cart from cookie
    get() {
        try {
            const raw = getCookie(CART_COOKIE);
            return raw ? JSON.parse(raw) : [];
        } catch {
            return [];
        }
    },

    // Write cart to cookie
    _save(items) {
        setCookie(CART_COOKIE, JSON.stringify(items), CART_EXPIRY_DAYS);
        Cart._notifyUpdate();
    },

    // Add a product to cart (or increase qty if already there)
    add(product, qty = 1) {
        const items = Cart.get();
        const existing = items.find(i => i.id === product.id);

        if (existing) {
            const newQty = existing.qty + qty;
            existing.qty = Math.min(newQty, product.stock_quantity);
        } else {
            items.push({
                id:             product.id,
                name:           product.name,
                price:          parseFloat(product.price),
                image_name:     product.image_name || "",
                category_name:  product.category_name || "Uncategorized",
                stock_quantity: product.stock_quantity,
                qty:            Math.min(qty, product.stock_quantity)
            });
        }

        Cart._save(items);
        return Cart.get();
    },

    // Remove a product from cart entirely
    remove(productId) {
        const items = Cart.get().filter(i => i.id !== productId);
        Cart._save(items);
        return items;
    },

    // Update quantity for a product (removes if qty <= 0)
    update(productId, newQty) {
        let items = Cart.get();
        if (newQty <= 0) {
            items = items.filter(i => i.id !== productId);
        } else {
            const item = items.find(i => i.id === productId);
            if (item) {
                item.qty = Math.min(newQty, item.stock_quantity);
            }
        }
        Cart._save(items);
        return items;
    },

    // Total number of items (sum of all quantities)
    count() {
        return Cart.get().reduce((sum, i) => sum + i.qty, 0);
    },

    // Total price
    total() {
        return Cart.get().reduce((sum, i) => sum + i.price * i.qty, 0);
    },

    // Empty the cart
    clear() {
        deleteCookie(CART_COOKIE);
        Cart._notifyUpdate();
    },

    // Notify all cart badge elements on the page
    _notifyUpdate() {
        const count = Cart.count();
        document.querySelectorAll(".cart-badge").forEach(el => {
            el.textContent = count;
            el.style.display = count > 0 ? "flex" : "none";
        });
        // Fire a custom event so other scripts can react
        window.dispatchEvent(new CustomEvent("cartUpdated", { detail: { count } }));
    }
};

// ── Auto-update badge on page load ────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
    Cart._notifyUpdate();
});