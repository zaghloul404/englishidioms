"""
L_algorithm.py Idiomatic Expression Matcher

This script is designed to find idiomatic expressions within English sentences by comparing them
to a dictionary of phrases stored in 'phrases.json'.
It consists of two main functions, 'get_potential_matches()' and 'look_closer()', 
which work together to identify potential dictionary entries that match a given English sentence
and then filter and rank those potential matches to find idiomatic expression matches.

'get_potential_matches()' Function:
-------------------------------------
This function aims to efficiently narrow down the search for potential dictionary entries that match
an input English sentence. It iterates through all entries in 'phrases.json' and checks if the 
sentence contains all the "constant" elements present in a dictionary entry. 
Various strategies are employed, including considering multi-word constants, word forms, 
and lemmatization, to enhance matching capabilities.

Args:
    sentence (str): The English sentence to search for potential matches within the 
    dictionary entries.

Returns:
    list: A list of indices corresponding to potential matching entries in 'phrases.json'. 
    This function significantly reduces the number of entries to be analyzed in the subsequent 
    matching process.

'look_closer()' Function:
--------------------------
This function refines the list of potential matches obtained from 'get_potential_matches()' 
to identify idiomatic expressions in the input sentence. 
It considers exact word matches, lemmatized forms, and patterns to determine the presence of 
idiomatic expressions. 
The resulting matches are filtered and sorted based on the number of matching words and word span.

Args:
    potential_matches (list): A list of potential matches returned by the 
    'get_potential_matches()' function.
    sentence (str): The English sentence to search for idiomatic expressions.

Returns:
    list: A list of filtered and sorted idiomatic expression matches. 
    Each item in the list consists of the dictionary entry, the number of matching words, 
    and the matched word span.

Note:
The script includes other auxiliary functions such as 'get_match_span()' and 'is_it_sorted()'
for various calculations and checks.

Example Usage:
--------------
Given an input sentence and dictionary:
```python
sentence = "The children were accustomed to eating late in the evening."
potential_matches = get_potential_matches(sentence)
idiomatic_matches = look_closer(potential_matches, sentence)
print(idiomatic_matches)
"""

import itertools
import json
import os
import pprint
import re

import nltk
from nltk.stem.wordnet import WordNetLemmatizer

# Determine the package-relative path to phrases.json
package_dir = os.path.dirname(__file__)
json_path = os.path.join(package_dir, "phrases.json")

# Load the JSON file
with open(json_path, "r", encoding="UTF-8") as file:
    data = json.load(file)

# manually point nltk to my top level nltk_data folder that includes wordnet
# https://www.nltk.org/data.html
nltk_data_dir = os.path.join(package_dir, "nltk_data")
nltk.data.path.append(nltk_data_dir)


def get_match_span(tuple_list):
    """
    Extract the first and last numbers from a list of tuples.

    This function takes a list of tuples and returns a tuple containing the first and last
    numbers from the combined list of elements in the tuples.

    Args:
    tuple_list (list of tuple): A list of tuples, where each tuple represents a pair of numbers.

    Returns:
    tuple: A tuple containing the first and last numbers from the list of tuples.

    Example:
    Input:
    tuple_list = [(3, 8), (12, 18), (25, 30)]

    Expected Output:
    Resulting Span: (3, 30)
    """

    flat_list = [item for pair in tuple_list for item in pair]

    return flat_list[0], flat_list[-1]


def is_it_sorted(tuple_list):
    """
    Check if the integers in a list of tuples are sorted in ascending order.

    This function takes a list of tuples and checks whether all the integer values within the list,
    when combined, are sorted in ascending order.
    It returns True if the integers are sorted, and False otherwise.

    Args:
    tuple_list (list of tuple): A list of tuples, where each tuple contains integer values.

    Returns:
    bool: True if the integers are sorted in ascending order, False otherwise.

    Example:
    Input:
    tuple_list = [(2, 4), (6, 9), (11, 13)]

    Expected Output:
    Result: True
    """
    flat_list = [item for pair in tuple_list for item in pair]

    if sorted(flat_list) == flat_list:
        return True

    return False


def longest(l):
    """
    Find the length of the longest list in a nested list structure.

    This function takes a nested list as an argument and returns the length of the longest list
    contained within it. It recursively explores the structure to identify the maximum length.

    Args:
    l (list): A nested list structure.

    Returns:
    int: The length of the longest list found within the nested structure.

    Example:
    Input:
    l = [1, [2, 3], [4, 5, [6, 7, 8]], [9, 10]]

    Expected Output:
    Result: 4

    Source:
    Original solution on Stack Overflow:
    https://stackoverflow.com/questions/30902558/finding-length-of-the-longest-list-in-an-irregular-list-of-lists
    """
    if not isinstance(l, list):
        return 0
    return max(
        [len(l)]
        + [len(subl) for subl in l if isinstance(subl, list)]
        + [longest(subl) for subl in l]
    )


def max_words_between(sentence, words, spans):
    """Find the maximum number of words between adjacent pairs of words in a sentence.

    Args:
        sentence (str): The input sentence.
        words (list of str): List of words in the sentence.
        spans (list of tuple): List of tuples representing spans of each word in the sentence.

    Returns:
        int: The maximum number of words between adjacent pairs of words.

    Example:
        >>> sentence = "This is a sample sentence."
        >>> words = ["This", "is", "a", "sentence."]
        >>> spans = [(0, 4), (5, 7), (8, 9), (17, 26)]
        >>> max_words_between(sentence, words, spans)
        1
    """
    # Initialize max_words to zero
    max_words = 0

    # Iterate through pairs of adjacent words
    for i in range(len(words) - 1):
        word1 = words[i]
        word2 = words[i + 1]

        # Get the span of each word
        span1 = spans[i]
        span2 = spans[i + 1]

        # Calculate the number of words between the two spans
        words_between = len(sentence[span1[1] + 1 : span2[0]].split())

        # Update max_words if necessary
        if words_between > max_words:
            max_words = words_between

    return max_words


def generate_combinations_with_constants(input_list):
    """
    Generate all possible combinations for items in a list where some items have variants/options
    and some are constants.

    Args:
        input_list (list): A list containing items. Some items may be lists representing
        variants/options, while others are constants.

    Returns:
        list: A list containing all possible combinations of items, with constants fixed in
        their respective positions.

    Example:
        >>> input_list = [["a1", "a2", "a3", "a4"], "b", ["c1", "c2", "c3"], "d", ["e1", "e2"]]
        >>> generate_combinations_with_constants(input_list)
        [('a1', 'b', 'c1', 'd', 'e1'),
        ('a1', 'b', 'c1', 'd', 'e2'),
        ('a1', 'b', 'c2', 'd', 'e1'),
        ('a1', 'b', 'c2', 'd', 'e2'),
        ('a1', 'b', 'c3', 'd', 'e1'),
        ('a1', 'b', 'c3', 'd', 'e2'),
        ('a2', 'b', 'c1', 'd', 'e1'),
        ('a2', 'b', 'c1', 'd', 'e2'),
        ('a2', 'b', 'c2', 'd', 'e1'),
        ('a2', 'b', 'c2', 'd', 'e2'),
        ('a2', 'b', 'c3', 'd', 'e1'),
        ('a2', 'b', 'c3', 'd', 'e2'),
        ('a3', 'b', 'c1', 'd', 'e1'),
        ('a3', 'b', 'c1', 'd', 'e2'),
        ('a3', 'b', 'c2', 'd', 'e1'),
        ('a3', 'b', 'c2', 'd', 'e2'),
        ('a3', 'b', 'c3', 'd', 'e1'),
        ('a3', 'b', 'c3', 'd', 'e2'),
        ('a4', 'b', 'c1', 'd', 'e1'),
        ('a4', 'b', 'c1', 'd', 'e2'),
        ('a4', 'b', 'c2', 'd', 'e1'),
        ('a4', 'b', 'c2', 'd', 'e2'),
        ('a4', 'b', 'c3', 'd', 'e1'),
        ('a4', 'b', 'c3', 'd', 'e2')]

    note: words as well in case the input_list included only constants
    >>> input_list = ["a1", "a2", "a3", "a4", "b"]
    >>> generate_combinations_with_constants(input_list)
    [('a1', 'a2', 'a3', 'a4', 'b')]
    """
    # Extract variant items and constant items
    variant_items = [item for item in input_list if isinstance(item, list)]
    constant_items = [item for item in input_list if not isinstance(item, list)]

    # Generate all possible combinations for variant items
    variant_combinations = itertools.product(*variant_items)

    # Combine variant combinations with constant items
    result = []
    for variant_combination in variant_combinations:
        combined = []
        variant_index = 0
        for item in input_list:
            if isinstance(item, list):
                combined.append(variant_combination[variant_index])
                variant_index += 1
            else:
                combined.append(item)
        result.append(tuple(combined))

    return result


def get_potential_matches(sentence, sentence_lemma):
    """
    Find potential dictionary entries that match a given English sentence.

    This function takes a given 'sentence' as input and examines it against all entries
    in 'phrases.json'.
    Its primary purpose is to expedite the search process by filtering potential matches
    before performing more detailed analysis.
    The function iterates through the entries and checks if all 'constant' elements in an entry
    exist in the sentence.
    If all 'constant' elements match, the entry is considered a potential match and is added
    to the result.

    Args:
    sentence (str): The English sentence to search for potential matches within the
    dictionary entries.

    Returns:
    list: A list of indices corresponding to potential matching entries in 'phrases.json.'

    Example:
    Input:
    sentence = "The children were accustomed to eating late in the evening."

    Expected Output:
    [21, 22, 1263, ...] # A list of entry indices representing potential matches.

    Note:
    This function significantly reduces the number of entries that need to be analyzed in the
    subsequent matching process, making the search more efficient and improving the overall
    performance of the search process.
    The function employs various strategies, such as considering multi-word constants,
    word forms, and lemmatization to enhance its matching capabilities, ensuring accurate
    identification of potential matches.
    """

    potential_matches = []

    for entry in data["dictionary"]:
        # let's see if all the constant in the current entry exist in the sentence

        # a- how many constants are there in the entry?
        constant_count = entry["alt"].count("constant")

        # b- does all those constants exist in the sentence?
        constant_match_count = 0

        for a, r, wf in zip(entry["alt"], entry["runs"], entry["word_forms"]):
            if a == "constant":
                # does that constant exist in the sentence
                if r in sentence:
                    constant_match_count += 1

                elif len(r.split()) == 1:  # a single word constant
                    # let's see if any of the word forms of the constant exist in the sentence
                    p = re.compile(rf"\b({'|'.join(wf[0])})\b", re.IGNORECASE)

                    m = p.search(sentence)

                    if m is not None:
                        constant_match_count += 1
                    else:
                        # does any of the words from the word form list exist
                        # in the lemmatized sentence?
                        if any(w in wf[0] for w in sentence_lemma):
                            constant_match_count += 1

                elif len(r.split()) > 1:  # a multiple word constant
                    # break down the constant to words and see if all those words
                    # (or their forms) exist in the sentence

                    word_match_count = 0

                    for c, w in enumerate(r.split()):
                        if w in sentence:
                            word_match_count += 1
                        else:
                            # let's see if any of the word forms exist in the sentence
                            p = re.compile(rf"\b({'|'.join(wf[c])})\b", re.IGNORECASE)

                            m = p.search(sentence)

                            if m is not None:
                                word_match_count += 1
                            else:
                                if any(w in wf[c] for w in sentence_lemma):
                                    word_match_count += 1

                    if word_match_count == len(r.split()):
                        constant_match_count += 1

        if constant_count == constant_match_count:
            # that means we have a potential match, add this entry to [potential_matches]

            potential_matches.append(data["dictionary"].index(entry))

    return potential_matches


def look_closer(potential_matches, sentence, sentence_lemma):
    """
    Filters potential matches and provides a list of idiomatic expression matches
    in a given English sentence.

    This function refines a list of potential matches obtained from the `get_potential_matches()`
    function by examining various factors, including exact word matches, lemmatized forms,
    and patterns, to determine the presence of idiomatic expressions in the input sentence.
    The workflow consists of the following steps:

    1. It considers all "article," "verb," "o-constant," and "constant" elements in each potential
       match and searches for their exact word, lemmatized form, or any form in the input sentence.
    2. It generates patterns from the findings and compares these patterns to those in the
       dictionary entry.
    3. It checks that all word matches in the sentence appear in the same order as in the
       dictionary entry.
    4. It ensures that matching words are not too far apart in the sentence, with a maximum allowed
       distance of 3 words between matched words to avoid incorrect matches in long sentences.
    5. The function returns all matches sorted in descending order, with the entry that has the
       highest number of matching words listed first.

    Args:
    potential_matches (list): A list of potential matches returned by get_potential_matches().
    sentence (str): The English sentence to search for idiomatic expressions.

    Returns:
    list: A list of filtered and sorted idiomatic expression matches, with each item consisting
    of the dictionary entry, the number of matching words, and the matched word span.

    Example:
    Given a list of potential matches and an input sentence:
    potential_matches = [0, 2, 4]  # Indices of potential matches in 'phrases.json'
    sentence = "The children were accustomed to eating late in the evening."

    The function returns a list of filtered matches, such as:
    [
        (matching_entry_1, 3, [(13, 31)]),
        (matching_entry_2, 1, [(32, 38)]),
        # ...
    ]
    """
    # Notes:
    # [refined_matches] always has fewer matches than potential_matches,
    # but the problem is that there are lots of entries in phrases.json that can
    # be triggered by a single word in a sentence - for example: the word "want" will always
    # trigger range (84897,84900)
    # to narrow down results a bit more, i'm organizing matches in [refined_matches]
    # in descending order.
    # i'll put entries with the highest number of matches 1st
    # - hopefully i can always pick up a match from the 1st 3 suggestions

    # here is a list of entries to examine
    dictionary = []
    for item in potential_matches:
        dictionary.append(data["dictionary"][item])

    matches = []

    # loop through all potential_matches in [dictionary]
    for d in dictionary:

        record = []

        for a, r, wf in zip(d["alt"], d["runs"], d["word_forms"]):
            if (
                a in ["article", "verb", "o-constant", "constant"]
                and len(r.split()) == 1
            ):
                p = re.compile(rf"\b({'|'.join(wf[0])})\b", re.IGNORECASE)

                match = p.findall(
                    sentence
                )  # returns a list of all matches, or empty list in case of no match

                span = [
                    m.span() for m in p.finditer(sentence)
                ]  # returns a list of all m.span, or empty list in case of no match

                # update the record
                if len(match) > 1 and len(span) > 1:
                    record.append([(r, s) for m, s in zip(match, span)])
                elif match and span:
                    record.append((r, span[0]))
                else:
                    # let's see if any word forms exist in the lemmatized sentence
                    sentence_lemma_string = " ".join(sentence_lemma)

                    p = re.compile(rf"\b({'|'.join(wf[0])})\b", re.IGNORECASE)
                    match = p.findall(sentence_lemma_string)
                    span = [m.span() for m in p.finditer(sentence_lemma_string)]

                    # update the record
                    if len(match) > 1 and len(span) > 1:
                        record.append([(r, s) for m, s in zip(match, span)])
                    elif match and span:
                        record.append((r, span[0]))

            elif (
                a in ["article", "verb", "o-constant", "constant"]
                and len(r.split()) > 1
            ):
                for c, w in enumerate(r.split()):
                    p = re.compile(rf"\b({'|'.join(wf[c])})\b", re.IGNORECASE)

                    match = p.findall(sentence)

                    span = [m.span() for m in p.finditer(sentence)]

                    # add the values to the dictionary inside record
                    if len(match) > 1 and len(span) > 1:
                        record.append([(w, s) for m, s in zip(match, span)])
                    elif match and span:
                        record.append((w, span[0]))
                    else:
                        sentence_lemma_string = " ".join(sentence_lemma)

                        p = re.compile(rf"\b({'|'.join(wf[c])})\b", re.IGNORECASE)
                        match = p.findall(sentence_lemma_string)
                        span = [m.span() for m in p.finditer(sentence_lemma_string)]

                        # update the record
                        if len(match) > 1 and len(span) > 1:
                            record.append([(w, s) for m, s in zip(match, span)])
                        elif match and span:
                            record.append((w, span[0]))

        combinations = generate_combinations_with_constants(record)

        for combo in combinations:
            words = [tupl[0] for tupl in combo]
            spans = [tupl[1] for tupl in combo]

            # lets check if we have a match
            if (
                words
                and spans
                and " ".join(words) in d["patterns"]
                and is_it_sorted(spans)
                and max_words_between(sentence, words, spans) <= 3
            ):
                matches.append((d, len(words), get_match_span(spans)))
                break

    # now, lets sort matches in descending order, highest number of matches 1st.
    # https://stackoverflow.com/questions/10695139/sort-a-list-of-tuples-by-2nd-item-integer-value
    sorted_refined_matches = sorted(matches, key=lambda x: x[1], reverse=True)

    return sorted_refined_matches


def find_idioms(
    sentence, limit=10, html=False, span=False, entry_range=False, entry_id=False
):

    # Tokenize the sentence into words
    words = nltk.word_tokenize(sentence.lower())

    # Tag the words with their respective parts of speech
    pos_tags = nltk.pos_tag(words)
    # sample output: [('You', 'PRP'), ('omitted', 'VBD'), ('Carol', 'NNP'),
    # ('from', 'IN'), ('the', 'DT'), ('list', 'NN'), ('.', '.')]

    # Lemmatize each word based on its POS tag
    sentence_lemma = [
        (
            WordNetLemmatizer().lemmatize(word, pos[0].lower())
            if pos[0].lower() in ["a", "n", "v"]
            else WordNetLemmatizer().lemmatize(word)
        )
        for word, pos in pos_tags
    ]

    potential_matches = get_potential_matches(sentence.lower(), sentence_lemma)
    lc = look_closer(potential_matches, sentence.lower(), sentence_lemma)

    matches = list(
        k for k, _ in itertools.groupby([(item[0], item[2]) for item in lc[:limit]])
    )

    output = []
    for m in matches:
        tmp = {}
        if html:
            tmp.update(
                {
                    "phrase_html": m[0]["phrase_html"],
                    "definition_html": m[0]["definition_html"],
                }
            )
        else:
            tmp.update({"phrase": m[0]["phrase"], "definition": m[0]["definition"]})
        if span:
            tmp.update({"span": m[1]})
        if entry_range:
            tmp.update({"entry_range": m[0]["range"]})
        if entry_id:
            tmp.update({"entry_id": m[0]["id"]})

        output.append(tmp)

    return output


if __name__ == "__main__":
    pass
