from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from blockchain import Blockchain
from db import init_db

app = FastAPI(title="L1 Demo Blockchain Node")

# ------------------------
# CORS (frontend: Vercel)
# ------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# INIT BLOCKCHAIN
# ------------------------

chain = Blockchain()


@app.on_event("startup")
def startup():
    init_db()


# ------------------------
# MODELS
# ------------------------

class LoginRequest(BaseModel):
    private_key: str


class TransactionRequest(BaseModel):
    receiver: str
    amount: float


# ------------------------
# HEALTH
# ------------------------

@app.get("/")
def root():
    return {
        "status": "L1 node running"
    }


# ------------------------
# LOGIN
# ------------------------

@app.post("/login")
def login(req: LoginRequest):
    result = chain.login(req.private_key)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid private key")

    return {
        "success": True,
        "data": result
    }


# ------------------------
# BALANCE
# ------------------------

@app.get("/balance/{address}")
def balance(address: str):
    bal = chain.get_balance(address)

    return {
        "success": True,
        "data": {
            "address": address,
            "balance": bal
        }
    }


# ------------------------
# TRANSACTION (AUTH VIA TOKEN)
# ------------------------

@app.post("/transaction")
def transaction(
    req: TransactionRequest,
    authorization: str = Header(None)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")

    # expected format: "Bearer <token>"
    try:
        token = authorization.split(" ")[1]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token format")

    try:
        tx = chain.add_transaction(
            token=token,
            receiver=req.receiver,
            amount=req.amount
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    return {
        "success": True,
        "data": tx
    }


# ------------------------
# MINE BLOCK
# ------------------------

@app.post("/mine")
def mine():
    block = chain.mine_block()

    if not block:
        raise HTTPException(status_code=400, detail="No transactions to mine")

    return {
        "success": True,
        "data": block
    }


# ------------------------
# TRANSACTIONS VIEWER
# ------------------------

@app.get("/transactions")
def transactions():
    return {
        "success": True,
        "data": chain.get_transactions()
    }


# ------------------------
# SINGLE TRANSACTION
# ------------------------

@app.get("/transaction/{tx_hash}")
def get_transaction(tx_hash: str):
    result = chain.get_transaction(tx_hash)

    return {
        "success": True,
        "data": result
    }


# ------------------------
# CHAIN (EXPLORER CORE)
# ------------------------

@app.get("/chain")
def chain_view():
    return {
        "success": True,
        "data": chain.get_chain()
    }


# ------------------------
# MEMPOOL
# ------------------------

@app.get("/mempool")
def mempool():
    return {
        "success": True,
        "data": chain.get_mempool()
    }


# ------------------------
# EXPLORER
# ------------------------

@app.get("/explorer")
def explorer():
    return {
        "success": True,
        "data": chain.get_explorer()
    }
