import zipfile

def xor_decrypt(encrypted_data, xor_key):
    # Extend the XOR key to match the length of the encrypted data
    extended_xor_key = (xor_key * ((len(encrypted_data) // len(xor_key)) + 1))[:len(encrypted_data)]

    # Decrypt the entire data using the XOR key
    decrypted_data = bytearray()
    for i in range(len(encrypted_data)):
        decrypted_byte = encrypted_data[i] ^ extended_xor_key[i]
        decrypted_data.append(decrypted_byte)

    return decrypted_data

def recover_xor_key(encrypted_data):
    # XOR the last 4 bytes of the encrypted file with the end of central directory signature `PK\x05\x06`
    end_of_central_dir_signature = b'\x50\x4b\x05\x06'
    xor_result_end_of_central_dir = [encrypted_data[-4 + i] ^ end_of_central_dir_signature[i] for i in range(len(end_of_central_dir_signature))]
    
    # First 8 bytes (from earlier steps) of the XOR key
    first_8_bytes = [0xa6, 0x28, 0x99, 0x30, 0xbe, 0xaf, 0xb0, 0xfe]
    
    # Combine the first 8 bytes and the last 4 bytes of the XOR key
    full_xor_key = first_8_bytes + xor_result_end_of_central_dir

    return full_xor_key

def main():
    # Load the encrypted ZIP file
    encrypted_file_path = "./XOR.zip.crypt"
    with open(encrypted_file_path, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()

    # Recover the XOR key
    xor_key = recover_xor_key(encrypted_data)

    # Decrypt the file
    decrypted_data = xor_decrypt(encrypted_data, xor_key)

    # Save the decrypted data to a new file
    decrypted_file_path = "./decrypted_XOR_final.zip"
    with open(decrypted_file_path, "wb") as decrypted_file:
        decrypted_file.write(decrypted_data)

    print(f"Decryption successful! The decrypted file is saved as {decrypted_file_path}")

if __name__ == "__main__":
    main()
