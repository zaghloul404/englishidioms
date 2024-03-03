"""Generate Word Forms for Dictionary Entries

Description:
This script processes dictionary entries from 'phrases.json' and generates word forms
for each word in the 'runs' lists, except for 'variable' words.
It utilizes the 'word_forms' Python package to generate all possible forms of English 
words and saves these forms back into 'phrases.json'.
The generated word forms enable accurate word identification and tense considerations 
for idiomatic expressions searches, while optimizing the execution time for search 
functions in 'L_algorithm.py'.
Having word forms available in phrases.json while using search functions in 
'L_algorithm.py' cuts off 10 seconds from the execution time of 'L_algorithm.py', 
as opposed to calling the get_word_forms function on the fly with every run to 'L_algorithm.py'.

In addition, this script assigns a unique id number to each entry in 'phrases.json', 
providing a distinct identifier for each entry, as the 'range' may not be unique.

Input:
- phrases.json

Output:
- Updated phrases.json

Runtime:
- Generating the updated phrases.json: Completed in 27 seconds.

Usage:
Please run this script from the command line (CMD)

Example:
python J_getwordforms.py
"""

import json
import os

import nltk
from word_forms.word_forms import get_word_forms

from Z_module import CompactJSONEncoder

# manually point nltk to local nltk_data folder that includes wordnet - required for get_word_forms
current_dir = os.path.dirname(__file__)
nltk_data_dir = os.path.join(current_dir, "englishidioms", "nltk_data")
nltk.data.path.append(nltk_data_dir)


def get_forms(word):
    """
    Get Word Forms for a Given Word

    This function takes an English word as input and utilizes the 'word_forms' package to generate
    various forms and tenses of the word.
    It returns these word forms as a list, ensuring that the original word is included in the list,
    even if no additional word forms are available.

    Args:
    - word (str): The English word for which to generate word forms.

    Returns:
    list of str: A list containing various forms and tenses of the input word.

    Example:
    word = 'politics'
    get_forms(word)  # Returns ['politics', 'political', 'politicians', 'politically', 'politician']
    """

    x = get_word_forms(word)

    forms = [word for word_type, word_list in x.items() for word in word_list]

    forms = list(set(forms))

    if word not in forms:
        forms.append(word)

    return forms


# load the dictionary json file
with open("englishidioms/phrases.json", encoding="UTF-8") as f:
    data = json.load(f)

for id_number, entry in enumerate(data["dictionary"]):
    # list of lists - len(word_forms) equals to len(entry["runs"])
    # & len() of each list is equal to word count for each run
    word_forms = []

    for a, r in zip(entry["alt"], entry["runs"]):
        if a != "variable":
            run_words = r.split()

            run_forms = [get_forms(w) for w in run_words]

            word_forms.append(run_forms)

        elif a == "variable":
            word_forms.append("NA")

    # an empty dict as a placeholder for updated entry details
    new_dict = dict()

    # add all values to new_dict
    new_dict["id"] = id_number  # add a unique id number to each entry
    new_dict["range"] = entry["range"]
    new_dict["phrase"] = entry["phrase"]
    new_dict["phrase_html"] = entry["phrase_html"]
    new_dict["definition"] = entry["definition"]
    new_dict["definition_html"] = entry["definition_html"]
    new_dict["alt"] = entry["alt"]
    new_dict["runs"] = entry["runs"]
    new_dict["patterns"] = entry["patterns"]
    new_dict["word_forms"] = word_forms
    new_dict["multiple"] = entry["multiple"]
    new_dict["duplicate"] = entry["duplicate"]

    # clear all items from {entry}
    entry.clear()
    # update entry with values in new_dict - get the correct order i want
    entry.update(new_dict)

# overwrite the file
with open("englishidioms/phrases.json", "w", encoding="UTF-8") as f:
    json.dump(data, f, indent=2, cls=CompactJSONEncoder, ensure_ascii=False)
