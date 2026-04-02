// ── Shared: Logout ────────────────────────────────────────────────────────────

document.getElementById("logoutBtn").addEventListener("click", async function () {
    try {
        const res = await fetch("/api/logout", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
        if (res.ok) window.location.href = "/login";
    } catch (err) {
        console.error("Logout failed:", err);
    }
});