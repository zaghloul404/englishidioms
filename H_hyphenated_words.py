""" Create Duplicates for Entries with Hyphenated Words

Description:
This script processes entries from 'phrases.json', specifically focusing on entries with hyphenated words.
It checks each entry for hyphenated words and creates a duplicate entry with hyphens replaced by spaces.

Input:
- phrases.json

Output:
- Updated phrases.json

Runtime:
- Generating the updated phrases.json: Completed in 3 seconds.

Usage:
Please run this script from the command line (CMD)

Example:
python H_hyphenated_words.py

This script will affect or alter 273 entries in 'phrases.json'.
"""

import json

from Z_module import CompactJSONEncoder

# load the json file
with open("englishidioms/phrases.json", encoding="UTF-8") as f:
    data = json.load(f)

# create a json string
json_string = """
{
  "dictionary": [

  ]
}
"""

# load json to python from a string - use file as a placeholder for all entries
file = json.loads(json_string)

for entry in data["dictionary"]:
    hyphenated_words = False
    for a, r in zip(entry["alt"], entry["runs"]):
        if a != "variable" and "-" in r:
            hyphenated_words = True

    if hyphenated_words:
        # a- save the entry without any changes
        data0 = {
            "range": entry["range"],
            "phrase": entry["phrase"],
            "phrase_html": entry["phrase_html"],
            "definition": entry["definition"],
            "definition_html": entry["definition_html"],
            "alt": entry["alt"],
            "runs": entry["runs"],
            "multiple": entry["multiple"],
            "duplicate": entry["duplicate"],
        }

        file["dictionary"].append(data0)

        # b- create a duplicate entry
        new_data = {
            "range": entry["range"],
            "phrase": entry["phrase"],
            "phrase_html": entry["phrase_html"],
            "definition": entry["definition"],
            "definition_html": entry["definition_html"],
            "alt": entry["alt"],
            "runs": [rr.replace("-", " ") for rr in entry["runs"]],
            "multiple": entry["multiple"],
            "duplicate": True,
        }

        file["dictionary"].append(new_data)

    else:
        # save the entry without any changes
        data1 = {
            "range": entry["range"],
            "phrase": entry["phrase"],
            "phrase_html": entry["phrase_html"],
            "definition": entry["definition"],
            "definition_html": entry["definition_html"],
            "alt": entry["alt"],
            "runs": entry["runs"],
            "multiple": entry["multiple"],
            "duplicate": entry["duplicate"],
        }

        file["dictionary"].append(data1)


# overwrite the file
with open("englishidioms/phrases.json", "w", encoding="UTF-8") as f:
    json.dump(file, f, indent=2, cls=CompactJSONEncoder, ensure_ascii=False)
