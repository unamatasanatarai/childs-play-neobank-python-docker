const API_URL = "http://localhost:8000/api/v1";
let token = localStorage.getItem("token");

// State Management
const updateUI = async () => {
    if (!token) {
        document.getElementById("auth-section").classList.remove("hidden");
        document.getElementById("dashboard-section").classList.add("hidden");
        return;
    }

    document.getElementById("auth-section").classList.add("hidden");
    document.getElementById("dashboard-section").classList.remove("hidden");

    // Fetch Balance
    try {
        const res = await fetch(`${API_URL}/banking/account/balance`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await res.json();
        // Convert minor units (cents) to decimal string for UI
        document.getElementById("balance-display").innerText = `$${(data.balance / 100).toFixed(2)}`;
        document.getElementById("account-number").innerText = data.account_number;
        document.getElementById("amount").value = ""

        // Fetch Available Accounts
        await fetchAccounts();
    } catch (err) {
        console.error("Session expired");
        logout();
    }
};

// Login Handler
document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    if (res.ok) {
        const data = await res.json();
        token = data.access_token;
        localStorage.setItem("token", token);
        updateUI();
    } else {
        alert("Authentication Failed");
    }
});

// Transfer Handler
document.getElementById("transfer-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const recipient_id = document.getElementById("recipient_id").value;
    const amountFloat = parseFloat(document.getElementById("amount").value);

    // Convert to minor units (cents) for the backend
    const amount = Math.round(amountFloat * 100);

    const res = await fetch(`${API_URL}/banking/transfer`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ recipient_id, amount })
    });

    if (res.ok) {
        alert("Transfer Successful!");
        updateUI();
    } else {
        const err = await res.json();

        let message = "Something went wrong";

        if (typeof err.detail === "string") {
            // Your HTTPException case
            message = err.detail;
        } else if (Array.isArray(err.detail)) {
            // FastAPI validation error
            const firstError = err.detail[0];
            const field = firstError.loc?.slice(-1)[0] || "field";
            message = `${field}: ${firstError.msg}`;
        }

        alert(`Error: ${message}`);
    }
});

const logout = () => {
    localStorage.removeItem("token");
    token = null;
    updateUI();
};

const fetchAccounts = async () => {
    try {
        const res = await fetch(`${API_URL}/banking/accounts`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (!res.ok) return;

        const accounts = await res.json();
        const select = document.getElementById("recipient_id");

        // Clear existing options except the first one
        while (select.options.length > 1) {
            select.remove(1);
        }

        accounts.forEach(account => {
            const option = document.createElement("option");
            option.value = account.id;
            option.textContent = account.display_name;
            select.appendChild(option);
        });
    } catch (err) {
        console.error("Failed to fetch accounts", err);
    }
};

// Initialize
updateUI();
