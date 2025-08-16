import random
import string
from collections import Counter
from ngram_score import ngram_score  # Ensure this module is available

def init_key(ciphertext):
    """Initialize a substitution key based on frequency analysis of the ciphertext."""
    # Common letter frequency order in English
    english_freq = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
    
    # Calculate frequency of each letter in the ciphertext
    cipher_freq = Counter(ciphertext)
    sorted_ciphertext_letters = [item[0] for item in cipher_freq.most_common() if item[0].isalpha()]
    
    # Map the most common letters in ciphertext to those in English frequency order
    initial_key = {}
    for c_letter, e_letter in zip(sorted_ciphertext_letters, english_freq):
        initial_key[c_letter] = e_letter
    
    # Fill remaining letters with unused ones in English order
    remaining_letters = set(string.ascii_uppercase) - set(initial_key.values())
    for letter in string.ascii_uppercase:
        if letter not in initial_key:
            initial_key[letter] = remaining_letters.pop()
    
    # Convert initial key to a string for easier manipulation
    return ''.join([initial_key[char] for char in string.ascii_uppercase])

def derive_key(key):
    """Generate a new key by randomly swapping two letters in the current key."""
    key_list = list(key)
    i, j = random.sample(range(len(key_list)), 2)
    key_list[i], key_list[j] = key_list[j], key_list[i]
    return ''.join(key_list)

def decrypt(ciphertext, key):
    """Decrypt ciphertext using the given substitution key."""
    translation_table = str.maketrans(string.ascii_uppercase, key)
    return ciphertext.translate(translation_table)

def hill_climb(ciphertext, init_key, max_iterations=10000):
    """Perform hill-climbing algorithm to break the monoalphabetic cipher."""
    # Initialize n-gram scoring function
    ngram_scorer = ngram_score('english_quadgrams.txt')  # Change to your file name
    best_key = init_key
    best_score = ngram_scorer.score(decrypt(ciphertext, best_key))
    
    for _ in range(max_iterations):
        # Generate a new key by applying a random swap (transposition)
        new_key = derive_key(best_key)
        decrypted_text = decrypt(ciphertext, new_key)
        new_score = ngram_scorer.score(decrypted_text)
        
        # If new key improves score, adopt it as the best key
        if new_score > best_score:
            best_key = new_key
            best_score = new_score
            print(f"New best score: {best_score}, Key: {best_key}")
    
    return best_key, decrypt(ciphertext, best_key)

def main():
    # Read the ciphertext from Subst.txt
    with open("Subst.txt", "r") as f:
        ciphertext = f.read().replace('\n', '')  # Removing newlines for smooth processing
    
    # Generate initial key using frequency analysis
    initial_key = init_key(ciphertext)
    print(f"Initial key: {initial_key}")
    
    # Perform hill climbing to find the optimal substitution key
    best_key, plaintext = hill_climb(ciphertext, initial_key)
    
    # Write the plaintext and best key to files
    with open("Plain.txt", "w") as f:
        f.write(plaintext)
    with open("subst.key", "w") as f:
        f.write(best_key)

    print("Decryption complete. Plaintext and key saved as Plain.txt and subst.key.")

if __name__ == "__main__":
    main()
