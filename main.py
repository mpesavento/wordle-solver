import argparse
import os
import sys
import re


from dictionary_tools import read_word_list_txt

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")

VOWELS = list("aeiou")


def get_input_escapable(prompt: str=None) -> str:
    """
    Get user input, checking for Keyboard interrupt and exiting if found
    :param prompt: str, prompt to print before input request
    :return: str
    """
    if prompt:
        print(prompt)
    try:
        result = input()
    except KeyboardInterrupt:
        print("Quitting app (ctrl-c)")
        sys.exit(1)
    return result


def find_first_guess(words):
    # first attempt: what word has the most vowels in it?
    word_dict = {}
    for w in words:
        word_dict[w] = {}
        vowel_ct = {ltr: w.count(ltr) for ltr in VOWELS}
        word_dict[w]["vowel_ct"] = vowel_ct
        word_dict[w]["unique_vowel_ct"] = sum([c > 0 for c in vowel_ct.values()])

    # find the word with the most unique vowels
    max_vowel = 0
    best_starter = []
    for w, v in word_dict.items():
        if v["unique_vowel_ct"] > max_vowel:
            max_vowel = v["unique_vowel_ct"]
    best_starters = [w for w, v in word_dict.items() if v["unique_vowel_ct"] == max_vowel]
    print("best starter words (vowel-based):")
    print(best_starters)
    return best_starters


def check_excluded_letters(words, exclude):
    match_str = f"[^{exclude.lower()}]"
    exclude_matcher = re.compile(match_str)
    matches = [exclude_matcher.findall(w) for w in words]
    word_matches = [w for w, match in zip(words, matches) if len(match) == 5]
    return word_matches


def check_positioned_letters(words, positioned_letters):
    """Check the wordlist to see which words have a letter in the target position"""
    positioned_matcher = re.compile(positioned_letters.lower())
    matches = [positioned_matcher.findall(w) for w in words]
    word_matches = [m[0] for m in matches if len(m) > 0]
    return word_matches


def check_unpositioned_letters(words, unpositioned_letters):
    # This is a bit harder. Write a regex to exclude the target letters in a given position, AND include them elsewhere
    # first find all words that do not have letters in the given positions
    match_str = re.sub(r"(\w)", r"[^\g<1>]", unpositioned_letters)
    not_there_matcher = re.compile(match_str)
    matches = [not_there_matcher.findall(w) for w in words]
    word_matches = [w for w, match in zip(words, matches) if len(match) != 0]

    # then only keep the words that has ALL the unpositioned letters
    find_letters = unpositioned_letters.replace(".", "").lower()
    has_letters_matcher = re.compile("|".join(find_letters))
    matches = [has_letters_matcher.findall(w) for w in words]  # word_matches
    has_letters_matches = [w for w, match in zip(words, matches) if len(match) == len(find_letters)]

    final_matches = list(set(word_matches).intersection(set(has_letters_matches)))

    return final_matches



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Display all words always")
    args = parser.parse_args()
    is_verbose = args.verbose

    words = read_word_list_txt("words_alpha_5.txt")

    print("########################")
    print("   Wordle guesstimator")

    first_guess = find_first_guess(words)
    print()
    result = None

    loop_check = True
    iter_ctr = 1
    while loop_check:
        print(f"*** Wordle Checker [iter {iter_ctr}]***")
        iter_ctr += 1

        excluded_letters = get_input_escapable("What letters are excluded?")
        if not excluded_letters:
            words_excludeltr = words
        else:
            words_excludeltr = check_excluded_letters(words, excluded_letters)
            print(f"Found {len(words_excludeltr)}/{len(words)}")
            if is_verbose:
                print(words_excludeltr)

        positioned_letters = get_input_escapable("What letters are known in position? (enter dot as placeholder, eg '.A.ER')")
        if not positioned_letters:
            words_positionchr = words_excludeltr
        elif len(positioned_letters) != 5:
            print(f"Bad length, got '{positioned_letters}'")
            continue
        else:
            words_positionchr = check_positioned_letters(words_excludeltr, positioned_letters)
            print(f"Found {len(words_positionchr)}/{len(words_excludeltr)}:")
            print(words_positionchr)

        # NOTE: listing the word like this will not be able to use prior history of incorrect positions
        # TODO: figure out how to add history
        unpositioned_letters = get_input_escapable("What letters are known and NOT in position? (enter as '.OR..'")
        if not unpositioned_letters:
            words_knownltrs = words_positionchr
        elif len(unpositioned_letters) != 5:
            print(f"Bad length, got '{unpositioned_letters}'")
            continue
        else:
            words_knownltrs = check_unpositioned_letters(words_positionchr, unpositioned_letters)
            print(f"Found {len(words_knownltrs)}/{len(words_positionchr)}:")
            print(words_knownltrs)

        # update the result
        result = words_knownltrs
        print(f"Found {len(result)} word hits")
        if len(result)/len(words) < 0.2:
            print(result)

        # loop until we have one or fewer words in the list
        if len(result) <= 1:
            loop_check = False

    if len(result) == 0:
        print("No known solutions, you messed up somewhere in your letter entering. Or bad dictionary.")
    elif len(result) == 1:
        print(f">>> {result.upper()}")
    else:
        print("How'd you get here?")


if __name__ == "__main__":
    main()

