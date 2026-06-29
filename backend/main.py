from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from blockchain import Blockchain
from db import init_db

app = FastAPI(title="L1 Demo Blockchain")

# ------------------------
# CORS (ВАЖНО для Vercel)
# ------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # потом можно ограничить доменом Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# создаём один экземпляр цепочки (наш "нода")
# ------------------------

chain = Blockchain()


# ------------------------
# STARTUP (ВОТ СЮДА ВСТАВКА БЫЛА НУЖНА)
# ------------------------

@app.on_event("startup")
def startup():
    init_db()


# ------------------------
# MODELS (API)
# ------------------------

class TransactionRequest(BaseModel):
    sender: str
    receiver: str
    amount: float


# ------------------------
# HEALTH
# ------------------------

@app.get("/")
def root():
    return {"status": "L1 node is running"}


# ------------------------
# CHAIN
# ------------------------

@app.get("/chain")
def get_chain():
    return {
        "length": len(chain.get_chain()),
        "chain": chain.get_chain()
    }


# ------------------------
# MEMPOOL
# ------------------------

@app.get("/mempool")
def get_mempool():
    return {
        "size": len(chain.get_mempool()),
        "mempool": chain.get_mempool()
    }


# ------------------------
# BALANCE
# ------------------------

@app.get("/balance/{address}")
def get_balance(address: str):
    balance = chain.get_balance(address)

    return {
        "address": address,
        "balance": balance
    }


# ------------------------
# CREATE TRANSACTION
# ------------------------

@app.post("/transaction")
def create_transaction(tx: TransactionRequest):
    if tx.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be > 0")

    result = chain.add_transaction(
        sender=tx.sender,
        receiver=tx.receiver,
        amount=tx.amount
    )

    return {
        "status": "added to mempool",
        "transaction": result
    }


# ------------------------
# MINE BLOCK
# ------------------------

@app.post("/mine")
def mine_block():
    block = chain.mine_block()

    if not block:
        raise HTTPException(status_code=400, detail="No transactions to mine")

    return {
        "status": "block mined",
        "block": block
    }


# ------------------------
# WALLETS (debug endpoint)
# ------------------------

@app.get("/wallets")
def get_wallets():
    return chain.wallets
