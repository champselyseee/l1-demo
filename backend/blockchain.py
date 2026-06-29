import hashlib
import json
import time
from pathlib import Path


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

        return {
            wallet["name"]: wallet
            for wallet in data["wallets"]
        }

    # ------------------------
    # Hash
    # ------------------------

    def calculate_hash(
        self,
        index,
        timestamp,
        transactions,
        previous_hash,
        nonce,
    ):
        block_string = json.dumps(
            {
                "index": index,
                "timestamp": timestamp,
                "transactions": transactions,
                "previous_hash": previous_hash,
                "nonce": nonce,
            },
            sort_keys=True,
        )

        return hashlib.sha256(block_string.encode()).hexdigest()

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

        timestamp = time.time()

        block = {
            "index": 0,
            "timestamp": timestamp,
            "transactions": [genesis_tx],
            "previous_hash": "0" * 64,
            "nonce": 0,
        }

        block["hash"] = self.calculate_hash(
            block["index"],
            block["timestamp"],
            block["transactions"],
            block["previous_hash"],
            block["nonce"],
        )

        self.chain.append(block)

    # ------------------------
    # Transactions
    # ------------------------

    def add_transaction(self, sender, receiver, amount):
        tx = {
            "from": sender,
            "to": receiver,
            "amount": amount,
            "timestamp": time.time(),
        }

        self.mempool.append(tx)

        return tx

    # ------------------------
    # Mining
    # ------------------------

    def mine_block(self):
        if not self.mempool:
            return None

        previous_block = self.chain[-1]

        timestamp = time.time()

        block = {
            "index": len(self.chain),
            "timestamp": timestamp,
            "transactions": self.mempool.copy(),
            "previous_hash": previous_block["hash"],
            "nonce": 0,
        }

        block["hash"] = self.calculate_hash(
            block["index"],
            block["timestamp"],
            block["transactions"],
            block["previous_hash"],
            block["nonce"],
        )

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

    def get_last_block(self):
        return self.chain[-1]

    def get_mempool(self):
        return self.mempool
