import os
import json
import psycopg


# ------------------------
# DB URL (ONLY ENV)
# ------------------------

DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise RuntimeError("DATABASE_URL is not set")


# ------------------------
# CONNECTION
# ------------------------

def get_connection():
    """
    Creates fresh connection to Postgres
    (simple version for L1-demo, no pool yet)
    """
    return psycopg.connect(DB_URL)


# ------------------------
# INIT SCHEMA
# ------------------------

def init_db():
    """
    Creates tables if they don't exist
    """

    with get_connection() as conn:
        with conn.cursor() as cur:

            # BLOCKS TABLE
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blocks (
                    index INTEGER PRIMARY KEY,
                    timestamp DOUBLE PRECISION,
                    previous_hash TEXT NOT NULL,
                    block_hash TEXT NOT NULL,
                    nonce INTEGER DEFAULT 0,
                    transactions JSONB NOT NULL
                );
            """)

        conn.commit()


# ------------------------
# INSERT BLOCK
# ------------------------

def insert_block(block: dict):
    """
    Stores a full block in Postgres
    """

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
                block.get("nonce", 0),
                json.dumps(block["transactions"])
            ))

        conn.commit()


# ------------------------
# LOAD CHAIN
# ------------------------

def load_chain():
    """
    Loads full blockchain from Postgres
    """

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
