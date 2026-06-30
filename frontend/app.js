const API =
    window.location.hostname === "localhost"
        ? "http://localhost:8000"
        : "https://YOUR-BACKEND.up.railway.app";

let wallet = {
    privateKey: null,
    address: null,
    token: null
};

// --------------------
// API HELPER
// --------------------

async function api(endpoint, options = {}) {
    const res = await fetch(`${API}${endpoint}`, options);
    const data = await res.json();

    if (!res.ok || data.success === false) {
        throw new Error(data.detail || "Request failed");
    }

    return data.data;
}

// --------------------
// LOGIN
// --------------------

async function login() {
    const privateKey = document.getElementById("privateKey").value.trim();

    if (!privateKey) {
        alert("No private key");
        return;
    }

    try {
        const data = await api("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                private_key: privateKey
            })
        });

        wallet.privateKey = privateKey;
        wallet.address = data.address;
        wallet.token = data.token;

        localStorage.setItem("token", data.token);
        localStorage.setItem("address", data.address);

        document.getElementById("loginBox").style.display = "none";
        document.getElementById("dashboard").style.display = "block";

        document.getElementById("address").innerText = data.address;

    } catch (err) {
        alert(err.message);
    }
}

// --------------------
// AUTO LOGIN
// --------------------

window.onload = async () => {
    const token = localStorage.getItem("token");
    const address = localStorage.getItem("address");

    if (!token || !address) return;

    wallet.token = token;
    wallet.address = address;

    document.getElementById("loginBox").style.display = "none";
    document.getElementById("dashboard").style.display = "block";

    document.getElementById("address").innerText = address;
};

// --------------------
// BALANCE
// --------------------

async function getBalance() {
    try {
        const data = await api(`/balance/${wallet.address}`);

        document.getElementById("balance").innerText = data.balance;

    } catch (err) {
        alert(err.message);
    }
}

// --------------------
// SEND TRANSACTION
// --------------------

async function sendTx() {
    const receiver = document.getElementById("to").value.trim();
    const amount = parseFloat(document.getElementById("amount").value);

    if (!receiver) {
        alert("Receiver required");
        return;
    }

    if (isNaN(amount) || amount <= 0) {
        alert("Invalid amount");
        return;
    }

    try {
        const data = await api("/transaction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${wallet.token}`
            },
            body: JSON.stringify({
                receiver,
                amount
            })
        });

        document.getElementById("txResult").innerText =
            JSON.stringify(data, null, 2);

    } catch (err) {
        alert(err.message);
    }
}

// --------------------
// MINE BLOCK
// --------------------

async function mine() {
    try {
        const data = await api("/mine", {
            method: "POST"
        });

        alert("Block mined!");
        console.log(data);

    } catch (err) {
        alert(err.message);
    }
}

// --------------------
// TRANSACTIONS VIEWER
// --------------------

async function loadTransactions() {
    try {
        const data = await api("/transactions");

        console.log("TXS:", data);

        document.getElementById("txResult").innerText =
            JSON.stringify(data, null, 2);

    } catch (err) {
        alert(err.message);
    }
}

// --------------------
// LOGOUT
// --------------------

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("address");

    location.reload();
}
