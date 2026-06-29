import time
import json
from pathlib import Path

from crypto import sha256


DATA_DIR = Path(__file__).parent / "data"
WALLETS_FILE = DATA_DIR / "wallets.json"


class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = []

        self.wallets = self.load_wallets()

        self.create_genesis_block()

    # ------------------------
    # Wallets
    # ------------------------

    def load_wallets(self):
        with open(WALLETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {w["name"]: w for w in data["wallets"]}

    # ------------------------
    # Transactions
    # ------------------------

    def create_transaction_hash(self, tx: dict) -> str:
        tx_string = json.dumps(tx, sort_keys=True)
        return sha256(tx_string)

    def add_transaction(self, sender, receiver, amount):
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
    # Blocks
    # ------------------------

    def create_block_hash(self, block: dict) -> str:
        block_string = json.dumps(block, sort_keys=True)
        return sha256(block_string)

    # ------------------------
    # Genesis
    # ------------------------

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

    # ------------------------
    # Mining
    # ------------------------

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
    # Balance
    # ------------------------

    def get_balance(self, address):
        balance = 0

        for block in self.chain:
            for tx in block["transactions"]:

                if tx["to"] == address:
                    balance += tx["amount"]

                if tx["from"] == address:
                    balance -= tx["amount"]

        return balance

    # ------------------------
    # Getters
    # ------------------------

    def get_chain(self):
        return self.chain

    def get_mempool(self):
        return self.mempool

    def get_last_block(self):
        return self.chain[-1]
