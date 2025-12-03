import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

def load_private_key():
    with open("student_private.pem", "rb") as f:
        key_data = f.read()
    private_key = serialization.load_pem_private_key(
        key_data,
        password=None
    )
    return private_key

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64 encrypted seed using RSA-OAEP-SHA256
    and return a validated 64-char hex string.
    """

    # 1. Base64 decode
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64)
    except Exception as e:
        raise ValueError("Invalid base64 seed: " + str(e))

    # 2. RSA OAEP SHA256 decryption
    try:
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        raise ValueError("RSA decryption failed: " + str(e))

    # 3. Decode to UTF-8 string
    try:
        seed_hex = plaintext_bytes.decode("utf-8").strip()
    except Exception:
        raise ValueError("Decrypted seed is not a UTF-8 string")

    # 4. Validate hex seed
    if len(seed_hex) != 64:
        raise ValueError("Seed must be 64 characters long")

    try:
        int(seed_hex, 16)  # Validate hex
    except ValueError:
        raise ValueError("Seed contains non-hex characters")

    return seed_hex


if __name__ == "__main__":
    private_key = load_private_key()

    # Read encrypted seed from file
    with open("encrypted_seed.txt", "r") as f:
        encrypted_b64 = f.read().strip()

    seed = decrypt_seed(encrypted_b64, private_key)
    print("Decrypted seed:", seed)
