import os
import json
import psycopg


DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/l1"
)


# ------------------------
# CONNECTION
# ------------------------

def get_connection():
    return psycopg.connect(DB_URL)


# ------------------------
# INIT SCHEMA
# ------------------------

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:

            # BLOCKS TABLE
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blocks (
                    index INTEGER PRIMARY KEY,
                    timestamp DOUBLE PRECISION,
                    previous_hash TEXT,
                    block_hash TEXT,
                    nonce INTEGER,
                    transactions JSONB
                );
            """)

        conn.commit()


# ------------------------
# INSERT BLOCK (PURE STORAGE)
# ------------------------

def insert_block(block: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO blocks (
                    index,
                    timestamp,
                    previous_hash,
                    block_hash,
                    nonce,
                    transactions
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (index) DO NOTHING;
            """, (
                block["index"],
                block["timestamp"],
                block["previous_hash"],
                block["block_hash"],
                block["nonce"],
                json.dumps(block["transactions"])
            ))

        conn.commit()


# ------------------------
# LOAD FULL CHAIN
# ------------------------

def load_chain():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT index, timestamp, previous_hash, block_hash, nonce, transactions
                FROM blocks
                ORDER BY index ASC;
            """)

            rows = cur.fetchall()

            chain = []
            for r in rows:
                chain.append({
                    "index": r[0],
                    "timestamp": r[1],
                    "previous_hash": r[2],
                    "block_hash": r[3],
                    "nonce": r[4],
                    "transactions": r[5],
                })

            return chain
