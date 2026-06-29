from db import insert_block, load_chain


# ------------------------
# BLOCK STORAGE API
# ------------------------

def save_block(block: dict):
    """
    Сохраняет блок в Postgres
    """
    insert_block(block)


# ------------------------
# LOAD CHAIN
# ------------------------

def get_chain():
    """
    Загружает всю цепочку из Postgres
    """
    return load_chain()


# ------------------------
# OPTIONAL: future extension point
# ------------------------

def get_block_by_index(index: int, chain: list):
    """
    Быстрый поиск блока (пока in-memory)
    """
    for block in chain:
        if block["index"] == index:
            return block
    return None


def get_transaction_from_chain(tx_hash: str, chain: list):
    """
    Поиск транзакции по всей цепочке
    """
    for block in chain:
        for tx in block["transactions"]:
            if tx.get("tx_hash") == tx_hash:
                return tx, block
    return None, None
