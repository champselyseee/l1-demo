import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


# ------------------------
# HASH (для tx, block и т.д.)
# ------------------------

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# ------------------------
# KEY GENERATION
# ------------------------

def generate_keypair():
    """
    Создаёт пару ключей (как в реальных блокчейнах)
    """
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    return {
        "private_key": base64.b64encode(private_bytes).decode(),
        "public_key": base64.b64encode(public_bytes).decode(),
    }


# ------------------------
# YOUR CUSTOM WALLET FORMAT
# ------------------------

def public_key_to_address(public_key_b64: str) -> str:
    """
    ТВОЙ формат кошелька (L1-style address)
    """
    pub_bytes = base64.b64decode(public_key_b64)

    h = hashlib.sha256(pub_bytes).hexdigest()

    # кастомный адрес L1
    return "L1" + h[:30]


# ------------------------
# SIGNING
# ------------------------

def sign(private_key_b64: str, message: str) -> str:
    """
    Подпись транзакции
    """
    priv_bytes = base64.b64decode(private_key_b64)

    private_key = Ed25519PrivateKey.from_private_bytes(priv_bytes)
    signature = private_key.sign(message.encode("utf-8"))

    return base64.b64encode(signature).decode()


# ------------------------
# VERIFY SIGNATURE
# ------------------------

def verify(public_key_b64: str, message: str, signature_b64: str) -> bool:
    """
    Проверка подписи
    """
    pub_bytes = base64.b64decode(public_key_b64)
    signature = base64.b64decode(signature_b64)

    public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)

    try:
        public_key.verify(signature, message.encode("utf-8"))
        return True
    except Exception:
        return False


# ------------------------
# MESSAGE FORMAT (ВАЖНО ДЛЯ БЛОКЧЕЙНА)
# ------------------------

def make_tx_message(sender: str, receiver: str, amount: float, timestamp: float) -> str:
    """
    Единый формат того, что подписывается
    (очень важно для консистентности сети)
    """
    return f"{sender}|{receiver}|{amount}|{timestamp}"
