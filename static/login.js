document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const errorMsg = document.getElementById("errorMsg");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    errorMsg.classList.add("hidden");

    btnText.textContent = "Signing in...";
    btnLoader.classList.remove("hidden");

    const data = {
        user_type: document.querySelector('input[name="user_type"]:checked').value,
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value
    };

    try {
        const res = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const json = await res.json();

        if (!res.ok) {
            errorMsg.textContent = json.error || "Login failed. Please try again.";
            errorMsg.classList.remove("hidden");
            btnText.textContent = "Sign In";
            btnLoader.classList.add("hidden");
            return;
        }

        // On success — keep spinner going while page navigates away
        if (json.user.user_type === "seller") {
            window.location.href = "/seller/dashboard";
        } else {
            window.location.href = "/customer/dashboard";
        }

    } catch (err) {
        errorMsg.textContent = "Network error. Please check your connection.";
        errorMsg.classList.remove("hidden");
        btnText.textContent = "Sign In";
        btnLoader.classList.add("hidden");
    }
});