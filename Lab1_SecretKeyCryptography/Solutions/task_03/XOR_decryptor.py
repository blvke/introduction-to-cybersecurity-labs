import itertools
from zipfile import ZipFile
import io

# Function to XOR-decrypt using a cyclic key
def xor_decrypt(data, key):
    key_length = len(key)
    return bytes([data[i] ^ key[i % key_length] for i in range(len(data))])

# Read the encrypted file
file_path = 'C:\\Users\\safiabakr\\Downloads\\Lab1-Taskfiles\\task03\\XOR.zip.crypt'  # Adjust this path if needed
with open(file_path, 'rb') as file:
    encrypted_data = file.read()

# Print the first 10 bytes of the encrypted data for verification
encrypted_bytes = encrypted_data[:10]
print("First 10 bytes of encrypted data:", encrypted_bytes.hex())

# Define known plaintext variations based on ZIP file header structure and possible versions
known_plaintext_versions = [
    bytes([0x50, 0x4B, 0x03, 0x04, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00]),  # Version 0A00
    bytes([0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00]),  # Version 1400
    bytes([0x50, 0x4B, 0x03, 0x04, 0x1E, 0x00, 0x00, 0x00, 0x00, 0x00])   # Version 1E00
]

# XOR each known plaintext version with the first 10 bytes of the encrypted data to derive key fragments
key_fragments = []
for known_plaintext in known_plaintext_versions:
    key_fragment = bytes([encrypted_bytes[i] ^ known_plaintext[i] for i in range(10)])
    key_fragments.append(key_fragment)
    print("Derived key fragment:", key_fragment.hex())  # Print each derived key fragment

# Function to brute-force the last two bytes of the key
def brute_force_full_key_search(encrypted_data, key_fragments):
    for key_fragment in key_fragments:
        for last_two_bytes in itertools.product(range(256), repeat=2):
            # Create the full 12-byte key by appending last two bytes to the 10-byte key fragment
            full_key = key_fragment + bytes(last_two_bytes)
            
            # Print the key being tried for debugging
            print("Attempting key:", full_key.hex())
            
            # Decrypt with the current key
            decrypted_data = xor_decrypt(encrypted_data, full_key)
            
            # Check if it's a valid ZIP by attempting to open it
            try:
                with ZipFile(io.BytesIO(decrypted_data)) as zip_file:
                    # Additional check by listing contents
                    if zip_file.testzip() is None or zip_file.namelist():
                        # Save successful decryption key and decrypted data path
                        decrypted_file_path = 'decrypted_XOR.zip'
                        with open(decrypted_file_path, 'wb') as temp_file:
                            temp_file.write(decrypted_data)
                        print("Decryption successful.")
                        print("Key:", full_key.hex())
                        print("Decrypted file saved as 'decrypted_XOR.zip'.")
                        return full_key, decrypted_file_path
            except Exception as e:
                # Print exception for debugging purposes
                print("Exception occurred for key:", full_key.hex(), "-", e)
                continue
    print("Decryption failed. No valid key found.")
    return None, None

# Run the brute-force search and output the result
final_key, decrypted_file_path = brute_force_full_key_search(encrypted_data, key_fragments)

# Final output
if final_key:
    print("Final Key Found:", final_key.hex())
else:
    print("No valid key was found.")
