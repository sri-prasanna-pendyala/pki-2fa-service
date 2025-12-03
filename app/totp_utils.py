import base64
import pyotp
import time


def hex_to_base32(hex_seed: str) -> str:
    """Convert 64-character hex seed to Base32 string."""
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code using:
    - SHA-1
    - 30-second period
    - 6 digits
    """
    # 1. Convert hex → base32
    base32_seed = hex_to_base32(hex_seed)

    # 2. Create TOTP object (SHA-1, 30s, 6 digits)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)

    # 3. Generate code (for current time)
    code = totp.now()

    return code


def generate_code_with_validity(hex_seed: str):
    """
    Returns:
        - TOTP code
        - Seconds remaining before it expires (0 to 29)
    """
    code = generate_totp_code(hex_seed)
    now = int(time.time())
    valid_for = 30 - (now % 30)
    return code, valid_for


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code, accepting ±1 time period (±30 seconds).
    """
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)

    # valid_window=1 allows one period before and after
    return totp.verify(code, valid_window=valid_window)
