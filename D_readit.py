""" Parse Dictionary Entries with single Idiomatic Expression

Description:
This script processes dictionary entries with single idiomatic expression in 'clean-output.docx', extracting and organizing the following data for each entry:
- phrase (string): The idiomatic expression in plain text format.
- phrase_html (string): The idiomatic expression in HTML format.
- definition (string): The definition(s) and example(s) of the idiomatic expression in plain text format.
- definition_html (string): The definition(s) and example(s) of the idiomatic expression in HTML format.
- runs (list): A list of 'runs' in the entry head.
- alt (list): A list of alternative naming for each run in the runs list, used to identify the type of each run. The runs and alt lists are always of the same length.

Input:
- ranges_SNGL.pickle: A pickle file containing a list of tuples, where each tuple represents the start and end lines of dictionary entries in 'clean-output.docx'.

Output:
- phrases.json: A JSON file containing data collected from all dictionary entries.

Thought Process:
- We iterate through dictionary entries with single expression in 'clean-output.docx'.
- We package the collected data for each entry into Python dictionaries and save them to phrases.json.

Runtime:
- Creating phrases.json: Completed in 14 minutes and 50 seconds.

Usage:
Please run this script from the command line (CMD)

Example:
python D_readit.py
"""

import re
import docx
import pickle
import json
from tqdm import tqdm
from Z_module import CompactJSONEncoder, runtype, cleanup, parse_entry

# load single phrase entry ranges []
with open("files/ranges_SNGL.pickle", "rb") as file:
    ranges_SNGL = pickle.load(file)

# open up clean-output.docx
doc = docx.Document("files/clean-output.docx")
lines = doc.paragraphs

# open phrases.json
with open("englishidioms/src/phrases.json", encoding="UTF8") as f:
    file = json.load(f)

print(
    "creating 'phrase', 'html', 'definition', 'alt', and 'runs' for single phrase entries"
)
# go through each entry (start, end)
for s, e in tqdm(ranges_SNGL):
    # create two lists for runs/alt pairs for each entry
    line_alt = []
    line_runs = []

    for i in range(s, e + 1):
        runs = lines[i].runs

        for ri, run in enumerate(runs):
            line_alt.append(runtype(ri, run))
            line_runs.append(run.text)

    # remove all items in both lists from the 1st 'definition' and beyond - only keep the entry head
    line_alt, line_runs = cleanup(line_alt, line_runs)

    # now that I know which part of the entry is the entry head, and which part is the definition/examples
    # let's create "phrase", "html", "definition" and save it to phrases.json
    phrase_text, phrase_html, entry_body_html = parse_entry((s, e), len(line_runs))

    # add entry to phrases.json
    data = {
        "range": [s, e],
        "phrase": phrase_text,
        "phrase_html": phrase_html,
        "definition": re.sub("<.+?>", "", entry_body_html),
        "definition_html": entry_body_html,
        "alt": [
            item.strip().lower() for item in line_alt
        ],  # strip each element from trailing/leading white space and lowercase all characters
        "runs": [item.strip().lower() for item in line_runs],
        "multiple": False,
        "duplicate": False,
    }

    file["dictionary"].append(data)

# save file
with open("englishidioms/src/phrases.json", "w", encoding="UTF8") as f:
    json.dump(file, f, indent=2, cls=CompactJSONEncoder, ensure_ascii=False)
