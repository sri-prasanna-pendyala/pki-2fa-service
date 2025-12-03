import json
import requests

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def request_seed(student_id: str, github_repo_url: str):

    # Read the PEM exactly as it is (NO replacing newlines)
    with open("student_public.pem", "r") as f:
        public_key_pem = f.read().strip()   # remove trailing blank line

    # Do NOT convert newlines manually!
    # Let requests (JSON serializer) escape them properly.

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem
    }

    print("Sending request to instructor...")

    response = requests.post(API_URL, json=payload, timeout=30)

    print("Status code:", response.status_code)
    print("Response:", response.text)

    if response.status_code != 200:
        return

    result = response.json()

    if "encrypted_seed" in result:
        with open("encrypted_seed.txt", "w") as f:
            f.write(result["encrypted_seed"])
        print("Encrypted seed saved!")
    else:
        print("No encrypted_seed in response.")

if __name__ == "__main__":
    STUDENT_ID = "24A95A0502"
    REPO_URL = "https://github.com/sri-prasanna-pendyala/pki-2fa-service.git"

    request_seed(STUDENT_ID, REPO_URL)
