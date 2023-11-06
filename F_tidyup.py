""" Clean up the 'alt' and 'runs' Lists in phrases.json

Description:
This script cleans up dictionary entries loaded from 'phrases.json', by processing the 'alt' and 'runs' lists for each entry. It applies a series of data-cleaning steps to ensure consistent and accurate information.

Input:
- phrases.json

Output:
- Updated phrases.json

Runtime:
- Generating the updated phrases.json: Completed in 2 seconds.

Usage:
Please run this script from the command line (CMD)

Example:
python F_tidyup.py
"""


import json
import re
from Z_module import CompactJSONEncoder


def cleanup(line_alt, line_runs):
    """
    Clean up the 'alt' and 'runs' data of a dictionary entry.

    Args:
        line_alt (list): A list of alternative naming for each run in the entry.
        line_runs (list): A list of 'runs' in the entry head.

    Returns:
        tuple: A tuple containing two lists:
        - line_alt (list): The cleaned 'alt' data.
        - line_runs (list): The cleaned 'runs' data.
    """
    # 1- remove special characters in runs
    # i for iteration, a for alternative, r for runs
    for i, (a, r) in enumerate(zip(line_alt, line_runs)):
        line_runs[i] = re.sub(r"[()1.,!?]", "", r).strip()

    # 2- remove empty strings & dagger items
    pop_index = []
    for i, (a, r) in enumerate(zip(line_alt, line_runs)):
        if len(r.strip()) == 0 or a == "dagger":
            pop_index.append(i)

    # Note that you need to delete them in reverse order so that you don't throw off the subsequent indexes.
    for x in sorted(pop_index, reverse=True):
        del line_alt[x]
        del line_runs[x]

    # 3- for 12 entries, alt[0] = "constant" and runs[0] = "*" example: [2147, 2153]
    # this happens as a result for the asterisk '*' coming at the start of the constant run and then followed by an o-constant

    # Note: the last or statement is for [634, 642], the asterisk comes at the end of a variable (and has the same format)
    # split_by_semicolon() makes the split after semicolon and adds alt "variable" to run "*"
    if line_runs[0] == "*" and (line_alt[0] == "constant" or line_alt[0] == "variable"):
        line_alt[0] = "asterisk"

    # 4- fix an asterisk '*' at the very end of entry head in [10119, 10122]
    if line_runs[-1] == "with*":
        line_runs[-1] = "with"

    return line_alt, line_runs


# load the json file
with open("englishidioms/src/phrases.json", encoding="UTF-8") as f:
    data = json.load(f)

for entry in data["dictionary"]:
    clean_alt, clean_runs = cleanup(entry["alt"], entry["runs"])

    # an empty dict as a placeholder for updated entry details
    new_dict = dict()

    # add all values to new_dict
    new_dict["range"] = entry["range"]
    new_dict["phrase"] = entry["phrase"]
    new_dict["phrase_html"] = entry["phrase_html"]
    new_dict["definition"] = entry["definition"]
    new_dict["definition_html"] = entry["definition_html"]
    new_dict["alt"] = clean_alt
    new_dict["runs"] = clean_runs
    new_dict["multiple"] = entry["multiple"]
    new_dict["duplicate"] = entry["duplicate"]

    # clear all items from {entry}
    entry.clear()
    # update entry with values in new_dict - get the correct order I want
    entry.update(new_dict)


# overwrite the file
with open("englishidioms/src/phrases.json", "w", encoding="UTF-8") as f:
    json.dump(data, f, indent=2, cls=CompactJSONEncoder, ensure_ascii=False)
