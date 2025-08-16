# cipher_keys.py

def load_file(file_path):
    """Reads a file and returns its contents as bytes."""
    with open(file_path, 'rb') as f:
        return f.read()

def xor_key(ciphertext, plaintext):
    """Calculates the XOR key needed to transform the ciphertext into the plaintext."""
    return bytes([ciphertext[i] ^ plaintext[i] for i in range(len(plaintext))])

def main():
    # File paths
    ciphertext_path = './cipher.crypt'
    plaintext1_path = './plaintext1.txt'
    plaintext2_path = './plaintext2.txt'
    k1_output_path = './k1.key'
    k2_output_path = './k2.key'

    # Load data from files
    ciphertext = load_file(ciphertext_path)
    plaintext1 = load_file(plaintext1_path).strip()  # Remove any newline characters
    plaintext2 = load_file(plaintext2_path).strip()  # Same for plaintext2

    # Match ciphertext length to plaintext length
    ciphertext_truncated = ciphertext[:len(plaintext1)]

    # XOR to find the keys
    k1 = xor_key(ciphertext_truncated, plaintext1)
    k2 = xor_key(ciphertext_truncated, plaintext2)

    # Save the keys to files
    with open(k1_output_path, 'wb') as f:
        f.write(k1)
    with open(k2_output_path, 'wb') as f:
        f.write(k2)

    print(f"Keys saved as '{k1_output_path}' and '{k2_output_path}'.")

if __name__ == "__main__":
    main()
