// ── State ─────────────────────────────────────────────────────────────────────

let allProducts = [];
let editingProductId = null;
let pendingDeleteId = null;
let pendingImageFile = null;

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
    await loadCategories();
    await loadProducts();
    setupEventListeners();
}

// ── Load products ─────────────────────────────────────────────────────────────

async function loadProducts() {
    try {
        const res = await fetch("/api/products");

        if (res.status === 403) {
            window.location.href = "/login";
            return;
        }

        allProducts = await res.json();
        renderProducts(allProducts);

    } catch (err) {
        document.getElementById("productsGrid").innerHTML =
            `<div class="products-empty"><p>Failed to load products.</p></div>`;
    }
}

// ── Load categories ───────────────────────────────────────────────────────────

async function loadCategories() {
    try {
        const res = await fetch("/api/seller/categories");
        const categories = await res.json();
        const select = document.getElementById("productCategory");

        // Clear existing options except the placeholder
        select.innerHTML = `<option value="">Select a category</option>`;

        categories.forEach(cat => {
            const opt = document.createElement("option");
            opt.value = cat.id;
            opt.textContent = cat.name;
            select.appendChild(opt);
        });

    } catch (err) {
        console.error("Failed to load categories:", err);
    }
}

// ── Render products ───────────────────────────────────────────────────────────

function renderProducts(products) {
    const grid = document.getElementById("productsGrid");
    const count = document.getElementById("productCount");

    count.textContent = products.length === 0
        ? "No products yet"
        : `${products.length} product${products.length > 1 ? "s" : ""}`;

    if (products.length === 0) {
        grid.innerHTML = `
            <div class="products-empty">
                <span>📦</span>
                <h3>No products yet</h3>
                <p>Click "Add Product" to list your first item.</p>
            </div>`;
        return;
    }

    grid.innerHTML = products.map(product => `
        <div class="product-card" data-id="${product.id}">
            <div class="product-card-image">
                ${product.image_name
                    ? `<img src="/static/uploads/product_images/${product.image_name}" alt="${product.name}">`
                    : `<div class="product-card-no-image">📷</div>`
                }
            </div>
            <div class="product-card-body">
                <div class="product-card-category">${product.category_name}</div>
                <h4 class="product-card-name">${product.name}</h4>
                <p class="product-card-desc">${product.description || "No description provided."}</p>
                <div class="product-card-footer">
                    <span class="product-card-price">৳${product.price.toFixed(2)}</span>
                    <span class="product-card-stock ${product.stock_quantity === 0 ? 'out-of-stock' : ''}">
                        ${product.stock_quantity === 0 ? "Out of stock" : `${product.stock_quantity} in stock`}
                    </span>
                </div>
            </div>
            <div class="product-card-actions">
                <button class="btn-card-edit" onclick="openEditModal(${product.id})">✎ Edit</button>
                <button class="btn-card-delete" onclick="openDeleteModal(${product.id}, '${product.name.replace(/'/g, "\\'")}')">🗑 Delete</button>
            </div>
        </div>
    `).join("");
}

// ── Add modal ─────────────────────────────────────────────────────────────────

function openAddModal() {
    editingProductId = null;
    pendingImageFile = null;

    document.getElementById("modalTitle").textContent = "Add Product";
    document.getElementById("saveProductBtnText").textContent = "Add Product";
    document.getElementById("editProductId").value = "";
    document.getElementById("productName").value = "";
    document.getElementById("productDescription").value = "";
    document.getElementById("productPrice").value = "";
    document.getElementById("productStock").value = "";
    document.getElementById("productCategory").value = "";
    resetImagePreview();
    hideModalError();

    document.getElementById("imageUploadGroup").style.display = "block";
    document.getElementById("modalOverlay").classList.remove("hidden");
}

// ── Edit modal ────────────────────────────────────────────────────────────────

function openEditModal(productId) {
    const product = allProducts.find(p => p.id === productId);
    if (!product) return;

    editingProductId = productId;
    pendingImageFile = null;

    document.getElementById("modalTitle").textContent = "Edit Product";
    document.getElementById("saveProductBtnText").textContent = "Save Changes";
    document.getElementById("editProductId").value = productId;
    document.getElementById("productName").value = product.name;
    document.getElementById("productDescription").value = product.description;
    document.getElementById("productPrice").value = product.price;
    document.getElementById("productStock").value = product.stock_quantity;
    document.getElementById("productCategory").value = product.category_id || "";
    hideModalError();

    // Show existing image if present
    if (product.image_name) {
        const preview = document.getElementById("imagePreview");
        preview.src = `/static/uploads/product_images/${product.image_name}`;
        preview.classList.remove("hidden");
        document.getElementById("imageUploadPlaceholder").style.display = "none";
    } else {
        resetImagePreview();
    }

    document.getElementById("imageUploadGroup").style.display = "block";
    document.getElementById("modalOverlay").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("modalOverlay").classList.add("hidden");
    editingProductId = null;
    pendingImageFile = null;
}

// ── Save product (add or update) ──────────────────────────────────────────────

async function saveProduct() {
    const btnText = document.getElementById("saveProductBtnText");
    const btnLoader = document.getElementById("saveProductBtnLoader");

    const data = {
        name: document.getElementById("productName").value.trim(),
        description: document.getElementById("productDescription").value.trim(),
        price: document.getElementById("productPrice").value,
        stock_quantity: document.getElementById("productStock").value,
        category_id: document.getElementById("productCategory").value || null
    };

    if (!data.name) {
        showModalError("Product name is required.");
        return;
    }
    if (!data.price) {
        showModalError("Price is required.");
        return;
    }

    btnText.textContent = editingProductId ? "Saving..." : "Adding...";
    btnLoader.style.display = "inline-block";

    try {
        let res, json;

        if (editingProductId) {
            // Update existing product
            res = await fetch(`/api/product/${editingProductId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
        } else {
            // Add new product
            res = await fetch("/api/product", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
        }

        json = await res.json();

        if (!res.ok) {
            showModalError(json.error || "Something went wrong.");
            return;
        }

        const savedProduct = json.product;

        // If there's a pending image file, upload it now
        if (pendingImageFile) {
            await uploadProductImage(savedProduct.id, pendingImageFile);
        }

        closeModal();
        showPageSuccess(editingProductId ? "Product updated successfully." : "Product added successfully.");
        await loadProducts();

    } catch (err) {
        showModalError("Network error. Please try again.");
    } finally {
        btnText.textContent = editingProductId ? "Save Changes" : "Add Product";
        btnLoader.style.display = "none";
    }
}

// ── Upload product image ──────────────────────────────────────────────────────

async function uploadProductImage(productId, file) {
    const formData = new FormData();
    formData.append("image", file);

    try {
        await fetch(`/api/product/${productId}/image`, {
            method: "POST",
            body: formData
        });
    } catch (err) {
        console.error("Image upload failed:", err);
    }
}

// ── Delete modal ──────────────────────────────────────────────────────────────

function openDeleteModal(productId, productName) {
    pendingDeleteId = productId;
    document.getElementById("deleteProductName").textContent = productName;
    document.getElementById("deleteOverlay").classList.remove("hidden");
}

function closeDeleteModal() {
    pendingDeleteId = null;
    document.getElementById("deleteOverlay").classList.add("hidden");
}

async function confirmDelete() {
    if (!pendingDeleteId) return;

    const btnText = document.getElementById("deleteBtnText");
    const btnLoader = document.getElementById("deleteBtnLoader");

    btnText.textContent = "Deleting...";
    btnLoader.style.display = "inline-block";

    try {
        const res = await fetch(`/api/product/${pendingDeleteId}`, {
            method: "DELETE"
        });

        if (!res.ok) {
            const json = await res.json();
            showPageError(json.error || "Failed to delete product.");
            return;
        }

        closeDeleteModal();
        showPageSuccess("Product deleted successfully.");
        await loadProducts();

    } catch (err) {
        showPageError("Network error. Please try again.");
    } finally {
        btnText.textContent = "Delete";
        btnLoader.style.display = "none";
    }
}

// ── Image upload preview ──────────────────────────────────────────────────────

function handleImageSelect(file) {
    if (!file) return;
    pendingImageFile = file;

    const reader = new FileReader();
    reader.onload = function (e) {
        const preview = document.getElementById("imagePreview");
        preview.src = e.target.result;
        preview.classList.remove("hidden");
        document.getElementById("imageUploadPlaceholder").style.display = "none";
    };
    reader.readAsDataURL(file);
}

function resetImagePreview() {
    const preview = document.getElementById("imagePreview");
    preview.src = "";
    preview.classList.add("hidden");
    document.getElementById("imageUploadPlaceholder").style.display = "flex";
    document.getElementById("productImage").value = "";
}

// ── Event listeners ───────────────────────────────────────────────────────────

function setupEventListeners() {

    document.getElementById("openAddModal").addEventListener("click", openAddModal);
    document.getElementById("closeModal").addEventListener("click", closeModal);
    document.getElementById("cancelModal").addEventListener("click", closeModal);
    document.getElementById("saveProductBtn").addEventListener("click", saveProduct);

    document.getElementById("closeDeleteModal").addEventListener("click", closeDeleteModal);
    document.getElementById("cancelDelete").addEventListener("click", closeDeleteModal);
    document.getElementById("confirmDeleteBtn").addEventListener("click", confirmDelete);

    // Close modals on overlay click
    document.getElementById("modalOverlay").addEventListener("click", function (e) {
        if (e.target === this) closeModal();
    });
    document.getElementById("deleteOverlay").addEventListener("click", function (e) {
        if (e.target === this) closeDeleteModal();
    });

    // Image upload area click
    document.getElementById("imageUploadArea").addEventListener("click", function () {
        document.getElementById("productImage").click();
    });

    document.getElementById("productImage").addEventListener("change", function () {
        if (this.files[0]) handleImageSelect(this.files[0]);
    });

    // Drag and drop
    const uploadArea = document.getElementById("imageUploadArea");
    uploadArea.addEventListener("dragover", function (e) {
        e.preventDefault();
        this.classList.add("drag-over");
    });
    uploadArea.addEventListener("dragleave", function () {
        this.classList.remove("drag-over");
    });
    uploadArea.addEventListener("drop", function (e) {
        e.preventDefault();
        this.classList.remove("drag-over");
        const file = e.dataTransfer.files[0];
        if (file) handleImageSelect(file);
    });

    // Logout
    document.getElementById("logoutBtn").addEventListener("click", async function () {
        await fetch("/api/logout", { method: "POST" });
        window.location.href = "/login";
    });
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function showModalError(msg) {
    const el = document.getElementById("modalError");
    el.textContent = msg;
    el.classList.remove("hidden");
}

function hideModalError() {
    document.getElementById("modalError").classList.add("hidden");
}

function showPageSuccess(msg) {
    const el = document.getElementById("successMsg");
    el.textContent = msg;
    el.classList.remove("hidden");
    document.getElementById("errorMsg").classList.add("hidden");
    setTimeout(() => el.classList.add("hidden"), 4000);
}

function showPageError(msg) {
    const el = document.getElementById("errorMsg");
    el.textContent = msg;
    el.classList.remove("hidden");
    document.getElementById("successMsg").classList.add("hidden");
}

// ── Start ─────────────────────────────────────────────────────────────────────

init();