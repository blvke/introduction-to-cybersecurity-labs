Writeup

Task Overview

The objective of this homework was to find two distinct keys, `k1` and `k2`, such that when applied to the same ciphertext yielded two different plaintexts after decryption. An idea here was to basically test whether it was possible to "collide" two keys for a single ciphertext using an encryption technique that could handle this.

Approach

For this, I decided upon an XOR-based approach. XOR's rather simple, actually, and it does have this nice property-if you XOR the ciphertext with one key, you can produce a certain type of plaintext. If you then XOR with another key, you get an utterly different plaintext from that same ciphertext. That made it a perfect fit for what I was trying to do.

Steps I Took

1. Loaded the Files: I have read the ciphertext (`cipher.crypt`), and two plaintext files (`plaintext1.txt`, `plaintext2.txt`). In this case, the plaintext files had extra newlines, so I made sure to strip those out for a clean match.
2. Truncated the Ciphertext: Since the ciphertext was a byte longer than each plaintext, I truncated it to the length of the plaintexts. This way, every byte in the truncated ciphertext will be aligned with a byte in each plaintext.
3. Computed the Keys:
- I XORed each byte in the truncated ciphertext with the appropriate byte in `plaintext1.txt`. This yielded `k1`, the key which would decrypt to the first plaintext.
   - I repeated this with `plaintext2.txt` to get `k2`, the key which decrypts to the second plaintext.

Results

After running the script, I tested that each key decrypted the ciphertext correctly:
Using `k1`, the ciphertext decrypted to "The world of cryptography is beautiful!"
Using `k2`, the ciphertext decrypted to "Actually encrypting things is overrated."

Deliverables

The deliverables for this task are:
1. Keys: `k1.key` and `k2.key` files contain the binary data for each key.
2. Script: I included a Python script (`cipher_keys.py`) that replicates the steps to produce the keys.
3. This Writeup: I summarized the approach and steps to keep things clear.

Conclusion

 This exercise was interesting to manipulate the XOR to create a "collision" in decryption results. XOR encryption is simple but powerful for that kind of demonstration.

