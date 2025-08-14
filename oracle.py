import hashlib

class HashMapper:
    def __init__(self, table_size=100):
        """
        Initialize the hash mapper with a fixed table size.
        - table_size: The size of the hash table (should be larger than expected number of words to minimize collisions).
        """
        self.table_size = table_size
        self.table = [None] * table_size  # Stores words at their probed indices
        self.word_to_index = {}  # Dict for word -> index
        self.index_to_word = {}  # Dict for index -> word

    def _compute_hash(self, word):
        """Compute initial hash index for the word using SHA-256."""
        sha_digest = hashlib.sha256(word.encode('utf-8')).hexdigest()
        int_hash = int(sha_digest, 16)
        return int_hash % self.table_size

    def _compute_step(self, word):
        """Compute a probing step derived from the SHA-256 hash (for double hashing-like behavior)."""
        sha_digest = hashlib.sha256(word.encode('utf-8')).hexdigest()
        int_hash = int(sha_digest, 16)
        # Derive step from higher bits; ensure it's between 1 and table_size-1
        step = 1 + (int_hash // self.table_size) % (self.table_size - 1)
        return step

    def insert(self, word):
        """
        Insert a word into the hash table using linear probing.
        If the word already exists, do nothing.
        """
        if word in self.word_to_index:
            return  # Already inserted
        index = self._compute_hash(word)
        original_index = index
        probe = 0
        while self.table[index] is not None:
            probe += 1
            index = (original_index + probe) % self.table_size
            if probe >= self.table_size:
                raise ValueError("Hash table is full! Increase table_size.")
        # Insert the word at the probed index
        self.table[index] = word
        self.word_to_index[word] = index
        self.index_to_word[index] = word

    def get_index(self, word):
        """Retrieve the index for a given word."""
        return self.word_to_index.get(word, None)

    def get_word(self, index):
        """Retrieve the word for a given index."""
        return self.index_to_word.get(index, None)

    def insert_words(self, words):
        """Convenience method to insert a list of words."""
        for word in words:
            self.insert(word)

# Example usage
if __name__ == "__main__":
    # Create a HashMapper with a table size (adjusted to 9999 per request)
    mapper = HashMapper(table_size=9999)
    # Input first: Get words from user input
    user_input = input("Enter your input text or words (space-separated for multiple): ")
    user_words = user_input.split()
    mapper.insert_words(user_words)
    print(f"Inserted {len(user_words)} words from input.")
    # Then, get words from a text file (limited to first 99999 characters; assumes "test.txt" exists locally)
    with open("test.txt", 'r') as f:
        sample_text = f.read()[:99999]
    text_words = sample_text.split()
    mapper.insert_words(text_words)
    print(f"Inserted {len(text_words)} words from text (duplicates ignored).")
    # Customized print: For each user input word, find and print a different word via hash-derived probing
    print("\nDifferent words from input via hash:")
    for word in user_words:
        if word not in mapper.word_to_index:
            print(f"'{word}' not in mapper (skipped).")
            continue
        hash_index = mapper._compute_hash(word)
        step = mapper._compute_step(word)
        probe_index = (hash_index + step) % mapper.table_size
        start_probe = probe_index
        found = False
        while True:
            if mapper.table[probe_index] is not None and mapper.table[probe_index] != word:
                print(f"For '{word}' (hash {hash_index}, step {step}), encrypted word: '{mapper.table[probe_index]}' (at index {probe_index})")
                found = True
                break
            probe_index = (probe_index + step) % mapper.table_size
            if probe_index == start_probe:
                break  # Full cycle; no different word found
        if not found:
            print(f"No different word found for '{word}' (table may be sparse or isolated).")
