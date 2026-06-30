import time
import json
import uuid
from pathlib import Path

from crypto import sha256, generate_keypair, public_key_to_address


DATA_DIR = Path(__file__).parent / "data"
WALLETS_FILE = DATA_DIR / "wallets.json"


class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = []

        # session_token -> address
        self.sessions = {}

        self.wallets = self.load_wallets()

        self.create_genesis_block()

    # ------------------------
    # WALLET SYSTEM
    # ------------------------

    def load_wallets(self):
        with open(WALLETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {w["name"]: w for w in data["wallets"]}

    def login(self, private_key: str):
        """
        returns session_token + wallet info
        """
        for wallet in self.wallets.values():
            if wallet["private_key"] == private_key:

                token = str(uuid.uuid4())
                self.sessions[token] = wallet["address"]

                return {
                    "token": token,
                    "address": wallet["address"],
                    "public_key": wallet["public_key"]
                }

        return None

    def get_address_by_token(self, token: str):
        return self.sessions.get(token)

    # ------------------------
    # TRANSACTIONS
    # ------------------------

    def create_transaction_hash(self, tx: dict) -> str:
        return sha256(json.dumps(tx, sort_keys=True))

    def add_transaction(self, token: str, receiver: str, amount: float):
        sender = self.get_address_by_token(token)

        if not sender:
            raise ValueError("Invalid session token")

        tx = {
            "from": sender,
            "to": receiver,
            "amount": amount,
            "timestamp": time.time(),
        }

        tx["tx_hash"] = self.create_transaction_hash(tx)

        self.mempool.append(tx)
        return tx

    # ------------------------
    # BLOCKS
    # ------------------------

    def create_block_hash(self, block: dict) -> str:
        return sha256(json.dumps(block, sort_keys=True))

    def create_genesis_block(self):
        genesis_tx = {
            "from": "SYSTEM",
            "to": self.wallets["A"]["address"],
            "amount": 1000,
            "timestamp": time.time(),
        }

        genesis_tx["tx_hash"] = self.create_transaction_hash(genesis_tx)

        block = {
            "index": 0,
            "timestamp": time.time(),
            "transactions": [genesis_tx],
            "previous_hash": "0" * 64,
            "nonce": 0,
        }

        block["block_hash"] = self.create_block_hash(block)

        self.chain.append(block)

    def mine_block(self):
        if not self.mempool:
            return None

        prev_block = self.chain[-1]

        block = {
            "index": len(self.chain),
            "timestamp": time.time(),
            "transactions": self.mempool.copy(),
            "previous_hash": prev_block["block_hash"],
            "nonce": 0,
        }

        block["block_hash"] = self.create_block_hash(block)

        self.chain.append(block)
        self.mempool.clear()

        return block

    # ------------------------
    # BALANCE
    # ------------------------

    def get_balance(self, address: str):
        balance = 0

        for block in self.chain:
            for tx in block["transactions"]:

                if tx["to"] == address:
                    balance += tx["amount"]

                if tx["from"] == address:
                    balance -= tx["amount"]

        return balance

    # ------------------------
    # TRANSACTION VIEWER
    # ------------------------

    def get_transactions(self):
        txs = []

        for block in self.chain:
            for tx in block["transactions"]:
                txs.append({
                    **tx,
                    "block_index": block["index"]
                })

        return txs

    def get_transaction(self, tx_hash: str):
        for block in self.chain:
            for tx in block["transactions"]:
                if tx["tx_hash"] == tx_hash:
                    return {
                        "found": True,
                        "transaction": tx,
                        "block_index": block["index"]
                    }

        return {"found": False}

    # ------------------------
    # EXPLORER
    # ------------------------

    def get_explorer(self):
        return {
            "height": len(self.chain),
            "mempool_size": len(self.mempool),
            "blocks": [
                {
                    "index": b["index"],
                    "tx_count": len(b["transactions"]),
                    "hash": b["block_hash"]
                }
                for b in self.chain
            ]
        }

    # ------------------------
    # GETTERS
    # ------------------------

    def get_chain(self):
        return self.chain

    def get_mempool(self):
        return self.mempool

    def get_last_block(self):
        return self.chain[-1]
