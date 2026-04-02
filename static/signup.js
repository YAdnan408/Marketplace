// Dynamically update address label based on role selection
const roleRadios = document.querySelectorAll('input[name="user_type"]');
const addressLabel = document.getElementById("addressLabel");

roleRadios.forEach(radio => {
    radio.addEventListener("change", () => {
        if (radio.value === "seller") {
            addressLabel.textContent = "Business Address";
        } else {
            addressLabel.textContent = "Delivery Address";
        }
    });
});

// Signup form submission
document.getElementById("signupForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const errorMsg = document.getElementById("errorMsg");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    // Hide any previous error
    errorMsg.classList.add("hidden");

    // Show loading state
    btnText.textContent = "Creating account...";
    btnLoader.classList.remove("hidden");

    const user_type = document.querySelector('input[name="user_type"]:checked').value;

    const data = {
        user_type: user_type,
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value,
        phone_number: document.getElementById("phone_number").value.trim(),
        address: document.getElementById("address").value.trim()
    };

    try {
        const res = await fetch("/api/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const json = await res.json();

        if (!res.ok) {
            // Show error
            errorMsg.textContent = json.error || "Something went wrong. Please try again.";
            errorMsg.classList.remove("hidden");
            btnText.textContent = "Create Account";
            btnLoader.classList.add("hidden");
            return;
        }

        // Redirect based on user type
        if (json.user.user_type === "seller") {
            window.location.href = "/seller/dashboard";
        } else {
            window.location.href = "/customer/dashboard";
        }

    } catch (err) {
        errorMsg.textContent = "Network error. Please check your connection.";
        errorMsg.classList.remove("hidden");
        btnText.textContent = "Create Account";
        btnLoader.classList.add("hidden");
    }
});