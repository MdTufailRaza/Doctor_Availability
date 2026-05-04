async function request(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.message || "Request failed.");
    }
    return data;
}

function showError(message) {
    const box = document.getElementById("errorBox");
    box.textContent = message;
    box.classList.remove("hidden");
}

document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const role = document.getElementById("role").value;

    try {
        await request("/api/auth/login", {
            method: "POST",
            body: JSON.stringify({
                role,
                username: document.getElementById("username").value,
                password: document.getElementById("password").value,
            }),
        });
        window.location.href = role === "admin" ? "/dashboard/admin" : "/dashboard/user";
    } catch (error) {
        showError(error.message);
    }
});
