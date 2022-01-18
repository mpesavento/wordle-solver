import os

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")

TARGET_LEN = 5  # target number of characters in selected words


def read_word_list_txt(filename):
    """Read all words in txt file, delimited by newline"""
    with open(os.path.join(DATA_DIR, filename), "r") as f:
        words = f.read().splitlines()  # includes '\n' char
    return words


def load_full_dictionary():
    """Load the full dictionary"""
    return read_word_list_txt("words_alpha.txt")


def filter_word_lengths(word_list, target_length=TARGET_LEN):
    return list(filter(lambda w: len(w) == target_length, word_list))


def write_filtered_list():
    all_words = load_full_dictionary()
    filtered_words = filter_word_lengths(all_words, TARGET_LEN)
    with open(os.path.join(DATA_DIR, f"words_alpha_{TARGET_LEN}.txt"), "w") as f:
        f.write('\n'.join(filtered_words))



if __name__ == "__main__":
    write_filtered_list()
