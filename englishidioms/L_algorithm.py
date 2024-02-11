"""
L_algorithm.py Idiomatic Expression Matcher

This script is designed to find idiomatic expressions within English sentences by comparing them to a dictionary of phrases stored in 'phrases.json'.
It consists of two main functions, 'get_potential_matches()' and 'look_closer()', which work together to identify potential dictionary entries that match a given English sentence and then filter and rank those potential matches to find idiomatic expression matches.

'get_potential_matches()' Function:
-------------------------------------
This function aims to efficiently narrow down the search for potential dictionary entries that match an input English sentence. It iterates through all entries in 'phrases.json' and checks if the sentence contains all the "constant" elements present in a dictionary entry. Various strategies are employed, including considering multi-word constants, word forms, and lemmatization, to enhance matching capabilities.

Args:
    sentence (str): The English sentence to search for potential matches within the dictionary entries.

Returns:
    list: A list of indices corresponding to potential matching entries in 'phrases.json'. This function significantly reduces the number of entries to be analyzed in the subsequent matching process.

'look_closer()' Function:
--------------------------
This function refines the list of potential matches obtained from 'get_potential_matches()' to identify idiomatic expressions in the input sentence. It considers exact word matches, lemmatized forms, and patterns to determine the presence of idiomatic expressions. The resulting matches are filtered and sorted based on the number of matching words and word span.

Args:
    potential_matches (list): A list of potential matches returned by the 'get_potential_matches()' function.
    sentence (str): The English sentence to search for idiomatic expressions.

Returns:
    list: A list of filtered and sorted idiomatic expression matches. Each item in the list consists of the dictionary entry, the number of matching words, and the matched word span.

Note:
The script includes other auxiliary functions such as 'get_match_span()' and 'is_it_sorted()' for various calculations and checks.

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
import re

import nltk
from nltk.stem.wordnet import WordNetLemmatizer

# Determine the package-relative path to phrases.json
package_dir = os.path.dirname(__file__)
json_path = os.path.join(package_dir, "phrases.json")

# Load the JSON file
with open(json_path, "r", encoding="UTF-8") as file:
    data = json.load(file)

# manually point nltk to my top level nltk_data folder that includes wordnet - https://www.nltk.org/data.html
nltk_data_dir = os.path.join(os.path.dirname(__file__), "nltk_data")
nltk.data.path.append(nltk_data_dir)


def get_match_span(tuple_list):
    """
    Extract the first and last numbers from a list of tuples.

    This function takes a list of tuples and returns a tuple containing the first and last numbers from the combined list of elements in the tuples.

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

    This function takes a list of tuples and checks whether all the integer values within the list, when combined, are sorted in ascending order. It returns True if the integers are sorted, and False otherwise.

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
    else:
        return False


def longest(l):
    """
    Find the length of the longest list in a nested list structure.

    This function takes a nested list as an argument and returns the length of the longest list contained within it. It recursively explores the structure to identify the maximum length.

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


def get_potential_matches(sentence):
    """
    Find potential dictionary entries that match a given English sentence.

    This function takes a given 'sentence' as input and examines it against all entries in 'phrases.json'.
    Its primary purpose is to expedite the search process by filtering potential matches before performing more detailed analysis.
    The function iterates through the entries and checks if all 'constant' elements in an entry exist in the sentence.
    If all 'constant' elements match, the entry is considered a potential match and is added to the result.

    Args:
    sentence (str): The English sentence to search for potential matches within the dictionary entries.

    Returns:
    list: A list of indices corresponding to potential matching entries in 'phrases.json.'

    Example:
    Input:
    sentence = "The children were accustomed to eating late in the evening."

    Expected Output:
    [21, 22, 1263, ...] # A list of entry indices representing potential matches.

    Note:
    This function significantly reduces the number of entries that need to be analyzed in the subsequent matching process, making the search more efficient and improving the overall performance of the search process.
    The function employs various strategies, such as considering multi-word constants, word forms, and lemmatization to enhance its matching capabilities, ensuring accurate identification of potential matches.
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
                        # let's take another look
                        # let's generate a lemma for each word in the sentence, and see if any of those words exist in the word forms list
                        sentence_lemma = [
                            WordNetLemmatizer().lemmatize(word, "v")
                            for word in sentence.split()
                        ]

                        if any(w in wf[0] for w in sentence_lemma):
                            constant_match_count += 1

                elif len(r.split()) > 1:  # a multiple word constant
                    # break down the constant to words and see if all those words (or their forms) exist in the sentence

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
                                sentence_lemma = [
                                    WordNetLemmatizer().lemmatize(word, "v")
                                    for word in sentence.split()
                                ]

                                if any(w in wf[c] for w in sentence_lemma):
                                    word_match_count += 1

                    if word_match_count == len(r.split()):
                        constant_match_count += 1

        if constant_count == constant_match_count:
            # that means we have a potential match, add this entry to [potential_matches]

            potential_matches.append(data["dictionary"].index(entry))

    return potential_matches


def look_closer(potential_matches, sentence):
    """
    Filters potential matches and provides a list of idiomatic expression matches in a given English sentence.

    This function refines a list of potential matches obtained from the `get_potential_matches()` function by examining various factors, including exact word matches, lemmatized forms, and patterns, to determine the presence of idiomatic expressions in the input sentence. The workflow consists of the following steps:

    1. It considers all "article," "verb," "o-constant," and "constant" elements in each potential match and searches for their exact word, lemmatized form, or any form in the input sentence.
    2. It generates patterns from the findings and compares these patterns to those in the dictionary entry.
    3. It checks that all word matches in the sentence appear in the same order as in the dictionary entry.
    4. It ensures that matching words are not too far apart in the sentence, with a maximum allowed distance of 3 words between matched words to avoid incorrect matches in long sentences.
    5. The function returns all matches sorted in descending order, with the entry that has the highest number of matching words listed first.

    Args:
    potential_matches (list): A list of potential matches returned by the get_potential_matches() function.
    sentence (str): The English sentence to search for idiomatic expressions.

    Returns:
    list: A list of filtered and sorted idiomatic expression matches, with each item consisting of the dictionary entry, the number of matching words, and the matched word span.

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
    # 1: using try,except in 'for index, (match, span) in enumerate(zip(m,s)):' to avoid the following Traceback "indexError: list index out of range"
    #   this is a rare situation, when there are more words/matches in a sentence that the number of dictionaries in [record]

    # 2: [refined_matches] always has fewer matches than potential_matches, but the problem is that there are lots of entries in phrases.json that can
    #   be triggered by a single word in a sentence - for example: the word "want" will always trigger range (84897,84900)
    #   to narrow down results a bit more, i'm organizing matches in [refined_matches] in descending order.
    #   i'll put entries with the highest number of matches 1st - hopefully i can always pick up a match from the 1st 3 suggestions

    # here is a list of entries to examine
    dictionary = []
    for item in potential_matches:
        dictionary.append(data["dictionary"][item])

    # pprint(dictionary)

    # record = [[{'i': 0, 'match': [], 'span': [], 'distance': 0}, {'i': 0, 'match': [], 'span': [], 'distance': 0}], [{'i': 1, 'match': ['back'], 'span': [(37, 41), 'distance': 0]}, {'i': 1, 'match': [], 'span': [], 'distance': 0}]]
    # [record] & [dictionary] are always of the same length

    record = []  # list of dict()

    # loop through all potential_matches in [dictionary]
    for i in range(len(dictionary)):
        record.insert(i, [])
        for _ in range(longest(dictionary[i]["word_forms"]) + 2):
            record[i].append({"i": i, "match": [], "span": [], "distance": 0})

        for a, r, wf in zip(
            dictionary[i]["alt"], dictionary[i]["runs"], dictionary[i]["word_forms"]
        ):
            if (
                a in ["article", "verb", "o-constant", "constant"]
                and len(r.split()) == 1
            ):
                p = re.compile(rf"\b({'|'.join(wf[0])})\b", re.IGNORECASE)

                m = p.findall(
                    sentence
                )  # returns a list of all matches, or empty list in case of no match

                s = [
                    m.span() for m in p.finditer(sentence)
                ]  # returns a list of all m.span, or empty list in case of no match

                # update the record
                if len(m) == 1 and len(s) == 1:
                    for ddict in record[i]:
                        ddict["match"].append(r)
                        ddict["span"].append(s[0])
                elif len(m) > 1 and len(s) > 1:
                    for index, (match, span) in enumerate(zip(m, s)):
                        try:
                            # ['the', 	'blind', 	'leading', 	'the', 		'blind']
                            # multiple matches with different spans can throw off the algorithm
                            # in case the match&span were added already, try adding the same match but with a different span
                            if (
                                r in record[i][index]["match"]
                                and span in record[i][index]["span"]
                            ):
                                for i_match, i_span in zip(m, s):
                                    if match == i_match and span != i_span:
                                        record[i][index]["match"].append(r)
                                        record[i][index]["span"].append(i_span)
                            else:
                                record[i][index]["match"].append(r)
                                record[i][index]["span"].append(span)

                        except:
                            pass
                else:
                    # let's generate a lemma for each word in the sentence, and see if any of those words exist in the word forms list
                    sentence_lemma = [
                        WordNetLemmatizer().lemmatize(word, "v")
                        for word in sentence.split()
                    ]
                    sentence_lemma_string = " ".join(sentence_lemma)

                    p = re.compile(rf"\b({'|'.join(wf[0])})\b", re.IGNORECASE)
                    m = p.findall(sentence_lemma_string)
                    s = [m.span() for m in p.finditer(sentence_lemma_string)]

                    # add the values to the dictionary inside record
                    if len(m) == 1 and len(s) == 1:
                        for ddict in record[i]:
                            ddict["match"].append(r)
                            ddict["span"].append(s[0])
                    elif len(m) > 1 and len(s) > 1:
                        for index, (match, span) in enumerate(zip(m, s)):
                            try:
                                # record[i][index]['match'].append(r)
                                # record[i][index]['span'].append(span)

                                if (
                                    r in record[i][index]["match"]
                                    and span in record[i][index]["span"]
                                ):
                                    for i_match, i_span in zip(m, s):
                                        if match == i_match and span != i_span:
                                            record[i][index]["match"].append(r)
                                            record[i][index]["span"].append(i_span)
                                else:
                                    record[i][index]["match"].append(r)
                                    record[i][index]["span"].append(span)
                            except:
                                pass

            elif (
                a in ["article", "verb", "o-constant", "constant"]
                and len(r.split()) > 1
            ):
                for c, w in enumerate(r.split()):
                    p = re.compile(rf"\b({'|'.join(wf[c])})\b", re.IGNORECASE)

                    m = p.findall(sentence)

                    s = [m.span() for m in p.finditer(sentence)]

                    # add the values to the dictionary inside record
                    if len(m) == 1 and len(s) == 1:
                        for ddict in record[i]:
                            ddict["match"].append(w)
                            ddict["span"].append(s[0])
                    elif len(m) > 1 and len(s) > 1:
                        for index, (match, span) in enumerate(zip(m, s)):
                            try:
                                # record[i][index]['match'].append(w)
                                # record[i][index]['span'].append(span)

                                if (
                                    w in record[i][index]["match"]
                                    and span in record[i][index]["span"]
                                ):
                                    for i_match, i_span in zip(m, s):
                                        if match == i_match and span != i_span:
                                            record[i][index]["match"].append(w)
                                            record[i][index]["span"].append(i_span)
                                else:
                                    record[i][index]["match"].append(w)
                                    record[i][index]["span"].append(span)
                            except:
                                pass
                    else:
                        # let's generate a lemma for each word in the sentance, and see if any of those words exist in the word forms list
                        sentence_lemma = [
                            WordNetLemmatizer().lemmatize(word, "v")
                            for word in sentence.split()
                        ]
                        sentence_lemma_string = " ".join(sentence_lemma)

                        p = re.compile(rf"\b({'|'.join(wf[c])})\b", re.IGNORECASE)
                        m = p.findall(sentence_lemma_string)
                        s = [m.span() for m in p.finditer(sentence_lemma_string)]

                        # add the values to the dictionary inside record
                        if len(m) == 1 and len(s) == 1:
                            for ddict in record[i]:
                                ddict["match"].append(w)
                                ddict["span"].append(s[0])
                        elif len(m) > 1 and len(s) > 1:
                            for index, (match, span) in enumerate(zip(m, s)):
                                try:
                                    # record[i][index]['match'].append(w)
                                    # record[i][index]['span'].append(span)

                                    if (
                                        w in record[i][index]["match"]
                                        and span in record[i][index]["span"]
                                    ):
                                        for i_match, i_span in zip(m, s):
                                            if match == i_match and span != i_span:
                                                record[i][index]["match"].append(w)
                                                record[i][index]["span"].append(i_span)
                                    else:
                                        record[i][index]["match"].append(w)
                                        record[i][index]["span"].append(span)
                                except:
                                    pass

    # calculate the distance (how many words are there) between each word in [match]
    # I'm going to set the maximum distance to 3 to avoid picking up bad suggestions in long sentences - as long sentences are more prone to produce bad matches
    for r in record:
        for ddict in r:
            if len(ddict["match"]) == 0 or len(ddict["match"]) == 1:
                ddict["distance"] = 0
                continue

            distance = []

            for i, (m, s) in enumerate(zip(ddict["match"], ddict["span"])):
                if len(ddict["match"]) == i + 1:
                    break  # final iteration

                in_between_span = sentence[s[-1] : ddict["span"][i + 1][0]]
                distance.append(len(in_between_span.strip().split()))

            ddict["distance"] = (
                0
                if max(distance) == 0
                else (
                    max(distance)
                    if max(distance) > 3
                    else sum(distance) / len(distance)
                )
            )

    # pprint(record)

    # loop through the dictionaries in [record], and see if we have a matching pattern and span is sorted
    matches = []
    for i in range(len(dictionary)):
        for r in record[i]:
            if (
                len(r["match"]) != 0
                and len(r["span"]) != 0
                and (" ".join(r["match"]) in dictionary[i]["patterns"])
                and is_it_sorted(r["span"])
                and r["distance"] <= 3.0
            ):
                # matches.append((dictionary[i], len(r['match'])))
                matches.append(
                    (dictionary[i], len(r["match"]), get_match_span(r["span"]))
                )

                # print(get_match_span(r['span']))

                break  # in order not to add duplicates to [matches]

    # print(len(matches))
    # pprint(matches)

    # now, lets sort matches in descending order, highest number of matches 1st.
    # https://stackoverflow.com/questions/10695139/sort-a-list-of-tuples-by-2nd-item-integer-value
    sorted_refined_matches = sorted(matches, key=lambda x: x[1], reverse=True)

    # pprint(sorted_refined_matches)

    return sorted_refined_matches


def find_idioms(
    sentence, limit=10, html=False, span=False, entry_range=False, entry_id=False
):
    potential_matches = get_potential_matches(sentence)
    lc = look_closer(potential_matches, sentence)

    matches = list(
        k for k, _ in itertools.groupby([(item[0], item[2]) for item in lc[:limit]])
    )

    output = list()
    for m in matches:
        tmp = dict()
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
