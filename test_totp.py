from totp_utils import generate_totp_code, generate_code_with_validity, verify_totp_code

# Read your decrypted seed from file
with open("seed.txt") as f:
    hex_seed = f.read().strip()

print("Seed:", hex_seed)

# Generate code
code, valid_for = generate_code_with_validity(hex_seed)
print("TOTP Code:", code)
print("Valid for:", valid_for, "seconds")

# Verify it
print("Verify:", verify_totp_code(hex_seed, code))
