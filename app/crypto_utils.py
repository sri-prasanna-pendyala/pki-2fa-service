import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization


# --------------------------
# Load student private key
# --------------------------
def load_private_key():
    """
    Loads student_private.pem from /keys folder.
    """
    with open("keys/student_private.pem", "rb") as f:
        key_data = f.read()

    private_key = serialization.load_pem_private_key(
        key_data,
        password=None
    )
    return private_key


# --------------------------
# RSA OAEP SHA-256 decryption
# --------------------------
def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64 encrypted seed using RSA OAEP SHA-256.

    Returns:
        64-character hex string.
    """

    # 1. Base64 decode
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64)
    except Exception:
        raise ValueError("Invalid base64")

    # 2. RSA OAEP decryption
    try:
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise ValueError("RSA decryption failed")

    # 3. Decode bytes → UTF-8
    try:
        seed_hex = plaintext_bytes.decode("utf-8").strip()
    except Exception:
        raise ValueError("Invalid UTF-8 plaintext")

    # 4. Validate 64-character hex
    if len(seed_hex) != 64:
        raise ValueError("Seed must be 64 hex chars")

    try:
        int(seed_hex, 16)
    except:
        raise ValueError("Seed contains non-hex characters")

    return seed_hex
