async function loadUsers() {

    const res = await fetch("http://127.0.0.1:5000/users");
    const users = await res.json();

    const tbody = document.getElementById("usersBody");
    tbody.innerHTML = "";

    if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#888;">No users found.</td></tr>`;
        return;
    }

    users.forEach(user => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.address || "—"}</td>
            <td class="action-btns">
                <button class="btn-delete" onclick="deleteUser(${user.id})">Delete</button>
            </td>
        `;

        tbody.appendChild(row);
    });
}

async function deleteUser(id) {

    const confirmed = confirm("Are you sure you want to delete this user?");
    if (!confirmed) return;

    await fetch(`http://127.0.0.1:5000/users/${id}`, {
        method: "DELETE"
    });

    loadUsers();
}

loadUsers();