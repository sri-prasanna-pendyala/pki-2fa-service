#!/usr/bin/env python3

import base64
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


# -------------------------------
# Load keys
# -------------------------------
def load_student_private_key():
    with open("keys/student_private.pem", "rb") as f:
        data = f.read()
    private_key = serialization.load_pem_private_key(
        data,
        password=None,
    )
    return private_key


def load_instructor_public_key():
    with open("keys/instructor_public.pem", "rb") as f:
        data = f.read()
    public_key = serialization.load_pem_public_key(data)
    return public_key


# -------------------------------
# 1. Sign commit hash (RSA-PSS-SHA256)
# -------------------------------
def sign_message(message: str, private_key) -> bytes:
    """
    Sign a message using RSA-PSS with SHA-256.

    - message: commit hash as ASCII string (40 hex chars)
    - returns: signature bytes
    """
    message_bytes = message.encode("utf-8")  # CRITICAL: ASCII/UTF-8 string

    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,  # maximum salt length
        ),
        hashes.SHA256(),
    )
    return signature


# -------------------------------
# 2. Encrypt signature (RSA-OAEP-SHA256)
# -------------------------------
def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA/OAEP with SHA-256.
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext


# -------------------------------
# 3. Get latest commit hash
# -------------------------------
def get_latest_commit_hash() -> str:
    """
    Runs: git log -1 --format=%H
    Returns the latest commit hash (40 hex chars).
    """
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        capture_output=True,
        text=True,
        check=True,
    )
    commit_hash = result.stdout.strip()
    if len(commit_hash) != 40:
        raise ValueError(f"Unexpected commit hash length: {commit_hash}")
    return commit_hash


# -------------------------------
# Main flow
# -------------------------------
def main():
    # 1. Get latest commit hash
    commit_hash = get_latest_commit_hash()

    # 2. Load keys
    student_private = load_student_private_key()
    instructor_public = load_instructor_public_key()

    # 3. Sign commit hash (RSA-PSS-SHA256)
    signature = sign_message(commit_hash, student_private)

    # 4. Encrypt signature with instructor's public key (RSA-OAEP-SHA256)
    encrypted_signature = encrypt_with_public_key(signature, instructor_public)

    # 5. Base64 encode (single line)
    encrypted_signature_b64 = base64.b64encode(encrypted_signature).decode("ascii")

    # 6. Print results
    print("Commit Hash:")
    print(commit_hash)
    print("\nEncrypted Signature (Base64):")
    print(encrypted_signature_b64)


if __name__ == "__main__":
    main()
