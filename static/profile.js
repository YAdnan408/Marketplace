let currentUserType = "";

// ── Load profile on page load ─────────────────────────────────────────────────

async function loadProfile() {
    try {
        const res = await fetch("/api/profile");

        if (res.status === 401) {
            window.location.href = "/login";
            return;
        }

        const profile = await res.json();
        currentUserType = profile.user_type || "";

        // Populate left card
        document.getElementById("profileName").textContent = profile.name || "—";
        document.getElementById("profileEmail").textContent = profile.email || "—";
        document.getElementById("profileBadge").textContent =
            currentUserType === "seller" ? "Seller" : "Customer";

        // Set profile image
        if (profile.profile_image) {
            document.getElementById("profileImage").src =
                `/static/uploads/profile_images/${profile.profile_image}`;
        }

        // Update address label for sellers
        if (currentUserType === "seller") {
            document.getElementById("addressLabel").textContent = "Business Address";
            document.getElementById("editAddressLabel").textContent = "Business Address";
        }

        // Populate view mode
        document.getElementById("viewName").textContent = profile.name || "—";
        document.getElementById("viewEmail").textContent = profile.email || "—";
        document.getElementById("viewPhone").textContent = profile.phone_number || "Not provided";
        document.getElementById("viewAddress").textContent = profile.address || "Not provided";

        // Pre-fill edit fields
        document.getElementById("editName").value = profile.name || "";
        document.getElementById("editPhone").value = profile.phone_number || "";
        document.getElementById("editAddress").value = profile.address || "";

        // Set back button destination
        document.getElementById("backBtn").href =
            currentUserType === "seller" ? "/seller/dashboard" : "/customer/dashboard";

    } catch (err) {
        console.error("Failed to load profile:", err);
    }
}

// ── Edit / Cancel toggle ──────────────────────────────────────────────────────

document.getElementById("editBtn").addEventListener("click", function () {
    document.getElementById("viewMode").classList.add("hidden");
    document.getElementById("editMode").classList.remove("hidden");
    document.getElementById("editBtn").style.display = "none";
    hideMessages();
});

document.getElementById("cancelBtn").addEventListener("click", function () {
    document.getElementById("editMode").classList.add("hidden");
    document.getElementById("viewMode").classList.remove("hidden");
    document.getElementById("editBtn").style.display = "inline-flex";
    hideMessages();
});

// ── Save profile changes ──────────────────────────────────────────────────────

document.getElementById("saveBtn").addEventListener("click", async function () {
    const saveBtnText = document.getElementById("saveBtnText");
    const saveBtnLoader = document.getElementById("saveBtnLoader");

    const data = {
        name: document.getElementById("editName").value.trim(),
        phone_number: document.getElementById("editPhone").value.trim(),
        address: document.getElementById("editAddress").value.trim()
    };

    if (!data.name) {
        showError("Name cannot be empty.");
        return;
    }

    saveBtnText.textContent = "Saving...";
    saveBtnLoader.style.display = "inline-block";

    try {
        const res = await fetch("/api/profile", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const json = await res.json();

        if (!res.ok) {
            showError(json.error || "Failed to update profile.");
            return;
        }

        const updated = json.profile;

        // Update view mode values
        document.getElementById("viewName").textContent = updated.name;
        document.getElementById("viewPhone").textContent = updated.phone_number || "Not provided";
        document.getElementById("viewAddress").textContent = updated.address || "Not provided";
        document.getElementById("profileName").textContent = updated.name;

        // Switch back to view mode
        document.getElementById("editMode").classList.add("hidden");
        document.getElementById("viewMode").classList.remove("hidden");
        document.getElementById("editBtn").style.display = "inline-flex";

        showSuccess("Profile updated successfully.");

    } catch (err) {
        showError("Network error. Please try again.");
    } finally {
        saveBtnText.textContent = "Save Changes";
        saveBtnLoader.style.display = "none";
    }
});

// ── Profile image upload ──────────────────────────────────────────────────────

document.getElementById("imageInput").addEventListener("change", async function () {
    const file = this.files[0];
    if (!file) return;

    // Show a local preview immediately
    const reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById("profileImage").src = e.target.result;
    };
    reader.readAsDataURL(file);

    // Upload to server
    const formData = new FormData();
    formData.append("image", file);

    try {
        const res = await fetch("/api/profile/image", {
            method: "POST",
            body: formData
        });

        const json = await res.json();

        if (!res.ok) {
            showError(json.error || "Image upload failed.");
            return;
        }

        showSuccess("Profile image updated successfully.");

    } catch (err) {
        showError("Network error during image upload.");
    }
});

// ── Logout ────────────────────────────────────────────────────────────────────

document.getElementById("logoutBtn").addEventListener("click", async function () {
    await fetch("/api/logout", { method: "POST" });
    window.location.href = "/login";
});

// ── Helpers ───────────────────────────────────────────────────────────────────

function showSuccess(msg) {
    const el = document.getElementById("successMsg");
    el.textContent = msg;
    el.classList.remove("hidden");
    document.getElementById("errorMsg").classList.add("hidden");
}

function showError(msg) {
    const el = document.getElementById("errorMsg");
    el.textContent = msg;
    el.classList.remove("hidden");
    document.getElementById("successMsg").classList.add("hidden");
}

function hideMessages() {
    document.getElementById("successMsg").classList.add("hidden");
    document.getElementById("errorMsg").classList.add("hidden");
}

// ── Init ──────────────────────────────────────────────────────────────────────

loadProfile();