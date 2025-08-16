from Crypto.Cipher import AES
import struct
import math

def calculate_entropy(data):
    """Calculate Shannon entropy of a data sequence"""
    if not data:
        return 0
    entropy = 0
    for x in set(data):
        p_x = data.count(x) / len(data)
        entropy -= p_x * math.log2(p_x)
    return entropy

def brute_force_aes(filename):
    # Read encrypted file
    with open(filename, 'rb') as f:
        ciphertext = f.read()
    
    iv = ciphertext[:16]  # Assuming IV is the first 16 bytes
    encrypted_data = ciphertext[16:]  # Rest is the encrypted content
    
    # Variables to store best key and plaintext based on entropy
    best_entropy = float('inf')
    best_plaintext = None
    best_key = None

    # Try all 16-bit keys (0x0000 to 0xFFFF)
    for key_candidate in range(0x10000):
        # Convert to a 128-bit key with padding: 0x0000 + 0's
        key = struct.pack(">H", key_candidate) + b'\x00' * 14
        
        # AES decryption with CBC mode
        cipher = AES.new(key, AES.MODE_CBC, iv)
        try:
            decrypted_data = cipher.decrypt(encrypted_data)
            
            # Check entropy
            entropy = calculate_entropy(decrypted_data)
            if entropy < best_entropy:
                best_entropy = entropy
                best_plaintext = decrypted_data
                best_key = key
        except ValueError:
            # AES decryption failed (in case padding is incorrect)
            continue

    # Write best decryption output
    if best_plaintext and best_key:
        with open("Subst.txt", "wb") as f:
            f.write(best_plaintext)
        
        with open("aes.key", "w") as f:
            f.write(best_key.hex())

        print("Decryption successful!")
        print("AES key found:", best_key.hex())
    else:
        print("No valid key found.")

# Run the brute-force attack
brute_force_aes("Subst-Rijndael.crypt")
