const API =
    window.location.hostname === "localhost"
        ? "http://localhost:8000"
        : "https://YOUR-BACKEND.up.railway.app";

let wallet = null;

// --------------------
// API
// --------------------

async function api(endpoint, options = {}) {
    const response = await fetch(`${API}${endpoint}`, options);

    const json = await response.json();

    if (!response.ok) {
        throw new Error(json.detail || "Request failed");
    }

    return json;
}

// --------------------
// LOGIN
// --------------------

async function login() {
    const privateKey = document
        .getElementById("privateKey")
        .value
        .trim();

    if (!privateKey) {
        alert("No private key");
        return;
    }

    wallet = {
        privateKey: privateKey
    };

    localStorage.setItem("privateKey", privateKey);

    try {
        await fetchAddress();

        document.getElementById("loginBox").style.display = "none";
        document.getElementById("dashboard").style.display = "block";
    }
    catch (err) {
        alert(err.message);
    }
}

// --------------------
// ADDRESS
// --------------------

async function fetchAddress() {

    const wallets = await api("/wallets");

    const match = Object.values(wallets).find(
        walletData => walletData.private_key === wallet.privateKey
    );

    if (!match) {
        throw new Error("Wallet not found");
    }

    wallet.address = match.address;

    document.getElementById("address").innerText =
        wallet.address;
}

// --------------------
// BALANCE
// --------------------

async function getBalance() {

    if (!wallet) return;

    const data = await api(`/balance/${wallet.address}`);

    document.getElementById("balance").innerText =
        data.balance;
}

// --------------------
// SEND TX
// --------------------

async function sendTx() {

    const receiver = document
        .getElementById("to")
        .value
        .trim();

    const amount = parseFloat(
        document.getElementById("amount").value
    );

    if (!receiver) {
        alert("Receiver required");
        return;
    }

    if (isNaN(amount) || amount <= 0) {
        alert("Invalid amount");
        return;
    }

    try {

        const result = await api("/transaction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sender: wallet.address,
                receiver: receiver,
                amount: amount
            })
        });

        document.getElementById("txResult").innerText =
            JSON.stringify(result, null, 2);

    } catch (err) {

        alert(err.message);

    }

}

// --------------------
// LOGOUT
// --------------------

function logout() {

    localStorage.removeItem("privateKey");

    wallet = null;

    location.reload();

}

// --------------------
// AUTO LOGIN
// --------------------

window.onload = async () => {

    const savedKey = localStorage.getItem("privateKey");

    if (!savedKey) {
        return;
    }

    wallet = {
        privateKey: savedKey
    };

    try {

        await fetchAddress();

        document.getElementById("loginBox").style.display = "none";
        document.getElementById("dashboard").style.display = "block";

    } catch (err) {

        console.error(err);

        localStorage.removeItem("privateKey");

    }

};
