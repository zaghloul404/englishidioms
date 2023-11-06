"""Generate Search Patterns for Idiomatic Expressions

Description:
This script processes dictionary entries from 'phrases.json', generating search patterns for identifying idiomatic expressions in sentences. 
The patterns are constructed from the 'alt' and 'runs' lists of each entry, allowing for flexible and accurate identification of idiomatic expressions.

Input:
- phrases.json

Output:
- Updated phrases.json

Runtime:
- Generating the updated phrases.json: Completed in 4 seconds.

Usage:
Ensure you have 'phrases.json' with the dictionary entries you want to process. Run the script to add search patterns to the entries and save the updated data to 'phrases.json'.

Example:
python I_getpatterns.py
"""


import json
from Z_module import CompactJSONEncoder


def get_patterns(entry_alt, entry_runs):
    """
    Generate search patterns for identifying idiomatic expressions in sentences using dictionary entries.

    This function creates search patterns for each dictionary entry in 'phrases.json', which can be used to identify idiomatic expressions in any given sentence.
    These patterns are constructed from both the 'alt' and 'runs' lists of the entry.

    The pattern generation process involves the following steps:

    1. Starting with the 'constant': 'constant' is a mandatory part of every pattern as it represents the core of idiomatic expressions.
    2. Handling 'variable': 'variable' is ignored and not included in the patterns.
    3. Dealing with 'o-constant', 'verb', and 'article': These elements can optionally contribute to identifying idiomatic expressions in a sentence. The function calculates all possible combinations of these elements.


    Args:
    entry_alt (list of str): The 'alt' list for a given dictionary entry.
    entry_runs (list of str): The 'runs' list for a given dictionary entry.

    Returns:
    list of str: A list of all possible search patterns based on the specified rules.

    Example:
    Given the following dictionary entry:
    *a free hand (with someone or something) Fig. freedom
    to exercise complete control over something. (*Typically:
    get ~; have ~; give someone ~.) _ I didn’t get a free
    hand with the last project. _ John was in charge then, but
    he didn’t get a free hand either.

    Input:
    entry_alt = ['verb', 'verb', 'verb', 'article', 'constant', 'o-constant', 'variable']
    entry_runs = ['get', 'have', 'give', 'a', 'free hand', 'with', 'someone or something']

    Expected Output:
    patterns_list = [
        'free hand',
        'a free hand',
        'free hand with',
        'a free hand with',
        'get free hand',
        'have free hand',
        'give free hand',
        'get a free hand',
        'have a free hand',
        'give a free hand',
        'get free hand with',
        'have free hand with',
        'give free hand with',
        'get a free hand with',
        'have a free hand with',
        'give a free hand with'
    ]
    """

    def combs(items):
        """
        Generate all possible combinations of elements in a list.

        This function takes a list of elements as input and recursively computes all possible combinations of those elements. It returns a list of lists, where each inner list represents a different combination of the input elements.

        Args:
        items (list): The list of elements to generate combinations from.

        Returns:
        list of lists: A list of lists containing all possible combinations of the input elements.

        Example:
        Input:
        items = ['A', 'B', 'C']

        Expected Output:
        combinations = [[], ['A'], ['B'], ['A', 'B'], ['C'], ['A', 'C'], ['B', 'C'], ['A', 'B', 'C']]
        """
        if len(items) == 0:
            return [[]]
        cs = []
        for c in combs(items[1:]):
            cs += [c, c + [items[0]]]
        return cs

    alts = entry_alt
    runs = entry_runs

    # calculate the possible outcomes, starting with the constants
    output = [[run for alt, run in zip(alts, runs) if alt == "constant"]]

    # deal with the articles (+ o-constants)
    articles = [
        run for alt, run in zip(alts, runs) if alt == "article" or alt == "o-constant"
    ]
    # calculate all possible combinations of articles (+ o-constants)
    poss_articles = [comb for comb in combs(articles)]
    if len(poss_articles) > 1:
        new_output = output.copy()
        for out in output:
            for articles in poss_articles[1:]:
                new_output.append(out + articles)
        output = new_output

    # deal with the verbs
    verbs = [run for alt, run in zip(alts, runs) if alt == "verb"]
    if len(verbs) > 0:
        new_output = output.copy()
        for out in output:
            for verb in verbs:
                new_output.append(out + [verb])
        output = new_output

    # get the correct ordering
    final_output = []
    for out in output:
        final_output.append(" ".join([word for word in runs if word in out]))

    # remove duplicates from final_output
    patterns_list = list(dict.fromkeys(final_output))

    return patterns_list


# load the json file
with open("englishidioms/src/phrases.json", encoding="UTF-8") as f:
    data = json.load(f)


for entry in data["dictionary"]:
    # to sort the results
    new_dict = dict()

    patterns = get_patterns(entry["alt"], entry["runs"])

    # add all values to new_dict
    new_dict["range"] = entry["range"]
    new_dict["phrase"] = entry["phrase"]
    new_dict["phrase_html"] = entry["phrase_html"]
    new_dict["definition"] = entry["definition"]
    new_dict["definition_html"] = entry["definition_html"]
    new_dict["alt"] = entry["alt"]
    new_dict["runs"] = entry["runs"]
    new_dict["patterns"] = patterns
    new_dict["multiple"] = entry["multiple"]
    new_dict["duplicate"] = entry["duplicate"]

    # clear all items from {entry}
    entry.clear()
    # update entry with values in new_dict - get the correct order I want
    entry.update(new_dict)


# save all to phrases.json
with open("englishidioms/src/phrases.json", "w", encoding="UTF-8") as f:
    json.dump(data, f, indent=2, cls=CompactJSONEncoder, ensure_ascii=False)
