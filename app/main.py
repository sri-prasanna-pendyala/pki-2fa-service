from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from .crypto_utils import decrypt_seed, load_private_key
from .totp_utils import generate_totp_code, generate_code_with_validity, verify_totp_code

app = FastAPI()

class EncryptedSeed(BaseModel):
    encrypted_seed: str

class VerifyCode(BaseModel):
    code: str | None = None

# ----------------------------
# IMPORTANT: Correct Docker path
# ----------------------------
DATA_DIR = "/data"
SEED_FILE = os.path.join(DATA_DIR, "seed.txt")

os.makedirs(DATA_DIR, exist_ok=True)

# ===============================================================
# 1️⃣ POST /decrypt-seed
# ===============================================================
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: EncryptedSeed):

    encrypted_seed_b64 = payload.encrypted_seed

    try:
        private_key = load_private_key()
        seed_hex = decrypt_seed(encrypted_seed_b64, private_key)

        with open(SEED_FILE, "w") as f:
            f.write(seed_hex)

        os.chmod(SEED_FILE, 0o644)  # ensure readable

        return {"status": "ok"}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": "Decryption failed"}
        )

# ===============================================================
# 2️⃣ GET /generate-2fa
# ===============================================================
@app.get("/generate-2fa")
def generate_2fa():

    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        code, valid_for = generate_code_with_validity(hex_seed)

        return {
            "code": str(code),
            "valid_for": int(valid_for)
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to generate TOTP"}
        )

# ===============================================================
# 3️⃣ POST /verify-2fa
# ===============================================================
@app.post("/verify-2fa")
def verify_2fa(payload: VerifyCode):

    if payload.code is None:
        raise HTTPException(status_code=400, detail={"error": "Missing code"})

    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        is_valid = verify_totp_code(hex_seed, payload.code)

        return {"valid": bool(is_valid)}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": "Verification failed"}
        )
