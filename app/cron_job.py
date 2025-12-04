#!/usr/bin/env python3

import os
from datetime import datetime, timezone

from .totp_utils import generate_totp_code

# NOTE:
# Inside Docker, the seed file will be at /data/seed.txt
# For local testing, you can temporarily change this to "data/seed.txt"
SEED_FILE = "/data/seed.txt"


def main():
    # 1. Read seed file
    if not os.path.exists(SEED_FILE):
        print("ERROR: seed file not found", flush=True)
        return

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        # 2. Generate TOTP code
        code = generate_totp_code(hex_seed)

        # 3. UTC timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # 4. Output log line (cron will append this to the log file)
        print(f"{timestamp} - 2FA Code: {code}", flush=True)

    except Exception as e:
        print(f"ERROR: {str(e)}", flush=True)


if __name__ == "__main__":
    main()
