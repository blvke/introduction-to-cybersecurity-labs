# xor_encrypt_with_keys.py

def load_file(file_path):
    """Reads a file and returns its contents as bytes."""
    with open(file_path, 'rb') as f:
        return f.read()

def xor_encrypt(plaintext, key):
    """Encrypts (or decrypts) plaintext using XOR with the provided key."""
    return bytes([plaintext[i] ^ key[i % len(key)] for i in range(len(plaintext))])

def main():
    # File paths
    plaintext1_path = 'plaintext1.txt'  # First plaintext file
    plaintext2_path = 'plaintext2.txt'  # Second plaintext file
    k1_path = 'k1.key'  # Key for plaintext1
    k2_path = 'k2.key'  # Key for plaintext2
    output1_path = 'ciphertext1.crypt'  # Output for ciphertext from plaintext1 with k1
    output2_path = 'ciphertext2.crypt'  # Output for ciphertext from plaintext2 with k2

    # Load plaintexts and keys
    plaintext1 = load_file(plaintext1_path).strip()
    plaintext2 = load_file(plaintext2_path).strip()
    k1 = load_file(k1_path)
    k2 = load_file(k2_path)

    # Encrypt each plaintext with its corresponding key
    ciphertext1 = xor_encrypt(plaintext1, k1)
    ciphertext2 = xor_encrypt(plaintext2, k2)

    # Save each ciphertext
    with open(output1_path, 'wb') as f:
        f.write(ciphertext1)
    with open(output2_path, 'wb') as f:
        f.write(ciphertext2)

    print(f"Ciphertext for plaintext1 saved as '{output1_path}'.")
    print(f"Ciphertext for plaintext2 saved as '{output2_path}'.")

if __name__ == "__main__":
    main()
