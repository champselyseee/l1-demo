const API = "http://localhost:8000";

let wallet = null;

// --------------------
// LOGIN
// --------------------

function login() {
    const privateKey = document.getElementById("privateKey").value;

    if (!privateKey) return alert("No private key");

    wallet = {
        privateKey: privateKey
    };

    localStorage.setItem("privateKey", privateKey);

    document.getElementById("loginBox").style.display = "none";
    document.getElementById("dashboard").style.display = "block";

    // тут потом дернем backend для получения address
    fetchAddress();
}

// --------------------
// GET ADDRESS (упрощённо через backend позже)
async function fetchAddress() {
    const res = await fetch(`${API}/wallets`);
    const data = await res.json();

    const pk = wallet.privateKey;

    // временно: просто ищем по wallets.json (dev режим)
    const match = Object.values(data.wallets).find(w => w.private_key === pk);

    if (match) {
        wallet.address = match.address;
        document.getElementById("address").innerText = match.address;
    }
}

// --------------------
// BALANCE
// --------------------

async function getBalance() {
    const res = await fetch(`${API}/balance/${wallet.address}`);
    const data = await res.json();

    document.getElementById("balance").innerText = data.balance;
}

// --------------------
// SEND TX
// --------------------

async function sendTx() {
    const to = document.getElementById("to").value;
    const amount = document.getElementById("amount").value;

    const res = await fetch(`${API}/transaction`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            sender: wallet.address,
            receiver: to,
            amount: parseFloat(amount)
        })
    });

    const data = await res.json();

    document.getElementById("txResult").innerText =
        JSON.stringify(data);
}

// --------------------
// LOGOUT
// --------------------

function logout() {
    localStorage.removeItem("privateKey");
    location.reload();
}
