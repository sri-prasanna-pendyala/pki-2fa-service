from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from .crypto_utils import decrypt_seed, load_private_key
from .totp_utils import generate_totp_code, generate_code_with_validity, verify_totp_code

app = FastAPI()

# ----------------------------
# Models
# ----------------------------

class EncryptedSeed(BaseModel):
    encrypted_seed: str

class VerifyCode(BaseModel):
    code: str | None = None


# ----------------------------
# File paths (simulate Docker paths)
# ----------------------------
DATA_DIR = "data"          # local folder (will become /data inside Docker)
SEED_FILE = os.path.join(DATA_DIR, "seed.txt")

os.makedirs(DATA_DIR, exist_ok=True)   # ensure folder exists



# ===============================================================
# 1️⃣ POST /decrypt-seed
# ===============================================================
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: EncryptedSeed):

    encrypted_seed_b64 = payload.encrypted_seed

    try:
        private_key = load_private_key()
        seed_hex = decrypt_seed(encrypted_seed_b64, private_key)

        # Save hex seed to /data/seed.txt
        with open(SEED_FILE, "w") as f:
            f.write(seed_hex)

        return {"status": "ok"}

    except Exception as e:
        # Do NOT leak internal errors
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
        raise HTTPException(
            status_code=500,
            detail={"error": "Seed not decrypted yet"}
        )

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        code, valid_for = generate_code_with_validity(hex_seed)

        return {
            "code": code,
            "valid_for": valid_for
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

    # Missing code → 400 error
    if payload.code is None:
        raise HTTPException(
            status_code=400,
            detail={"error": "Missing code"}
        )

    if not os.path.exists(SEED_FILE):
        raise HTTPException(
            status_code=500,
            detail={"error": "Seed not decrypted yet"}
        )

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        is_valid = verify_totp_code(hex_seed, payload.code)

        return {"valid": is_valid}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"error": "Verification failed"}
        )
