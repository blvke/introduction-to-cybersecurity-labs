Write-Up for XOR Encrypted ZIP File Decryption
Overview
This task involved decrypting a file (XOR.zip.crypt) that was XOR-encrypted with a 96-bit key. The encrypted file was structured as a ZIP archive, so we utilized known-plaintext characteristics of ZIP file headers to derive portions of the encryption key. We then brute-forced the remaining unknown bytes to fully decrypt the file.

Approach
Step 1: Known-Plaintext Analysis of ZIP File Structure
ZIP files have a standardized header structure, allowing us to use a known-plaintext attack. Specifically, the first four bytes of a ZIP file are a fixed signature (0x50 0x4B 0x03 0x04), identifying the file type. Following this signature, ZIP headers typically contain a "version needed to extract" field, which may vary based on the archive's creation.

Given this structure, we considered three potential values for the "version needed to extract" field:

0A00 –  version 1.
1400 –  version 2.
1E00 –  version 3.
The subsequent four bytes are generally 0000 0000, which represent flags and compression settings in uncompressed files. With these assumptions, we created three possible 10-byte known plaintext sequences for the header:

plaintext
Option 1: 50 4B 03 04 0A 00 00 00 00 00
Option 2: 50 4B 03 04 14 00 00 00 00 00
Option 3: 50 4B 03 04 1E 00 00 00 00 00
Step 2: Deriving Initial Key Fragments
To derive possible key fragments, we XORed the first 10 bytes of the encrypted file with each of the three known plaintext sequences. This XOR operation yielded three potential 10-byte key fragments, each corresponding to one of the plaintext variations.

Below is the code used to calculate the key fragments:

python

# XOR each known plaintext version with the first 10 bytes of the encrypted data to derive key fragments
encrypted_bytes = encrypted_data[:10]  # First 10 bytes of encrypted data
key_fragments = []
for known_plaintext in known_plaintext_versions:
    key_fragment = bytes([encrypted_bytes[i] ^ known_plaintext[i] for i in range(10)])
    key_fragments.append(key_fragment)
    print("Derived key fragment:", key_fragment.hex())  # Print each derived key fragment
Each derived key fragment was printed to confirm that the values were as expected and matched with the structure of the ZIP header.

Step 3: Brute-Forcing the Last Two Bytes
Since the XOR key was 12 bytes in total (96 bits), we still needed the last two bytes to complete the key. For each of the derived 10-byte key fragments, we performed a brute-force search on the last two bytes, iterating through all values from 00 00 to FF FF. This brute-force search generated a total of 2^16 possible key combinations.

Step 4: Validation by Checking ZIP Structure
For each generated 12-byte key candidate, we decrypted the file and checked if the decrypted data could be opened as a ZIP archive. This validation was performed by attempting to open the decrypted data as a ZIP file and listing its contents. If the data structure was valid, we saved the file and printed the successful key.

The brute-force search and validation code is shown below:

python

# Function to brute-force the last two bytes of the key
def brute_force_full_key_search(encrypted_data, key_fragments):
    for key_fragment in key_fragments:
        for last_two_bytes in itertools.product(range(256), repeat=2):
            # Create the full 12-byte key by appending last two bytes to the 10-byte key fragment
            full_key = key_fragment + bytes(last_two_bytes)
            
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
Result: Successful Key Discovery
Running the brute-force search successfully revealed the 12-byte XOR decryption key. The decrypted file was saved as decrypted_XOR.zip, which could then be opened without additional passwords.

plaintext

Final Key: a6 28 99 30 e4 e4 b1 fc 1b 63 ba d3
This process demonstrated that the known-plaintext structure of ZIP headers, combined with brute-forcing, could effectively reveal the XOR key and decrypt the file.

Conclusion
This solution illustrates how leveraging predictable file structures, like ZIP headers, can aid cryptanalysis. By combining a known-plaintext attack with an efficient brute-force search, we successfully derived the full 12-byte XOR encryption key and decrypted the file. This approach highlights the utility of known file structures in cryptanalysis and the importance of validating decryption attempts using file integrity checks.