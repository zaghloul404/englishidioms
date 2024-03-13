"""Extract Examples from 'phrases.json'

Description:
This script is designed to parse dictionary entries from phrases.json, 
extracting and saving the examples contained within each entry.

The process involves iterating through all dictionary entries.
For each entry, it picks up 'definition_html' and uses regular expressions to identify and 
extract example sentences, saving both the examples and their corresponding ranges. the script only
keeps unique ranges in order not to repeat examples that appear multiple times.
The script offers two output formats: a human-readable 'examples.txt' file and a serialized 
'examples.pickle' file.

Input:
- phrases.json

Output:
- examples.txt (optional)
- examples.pickle

Runtime:
- Generating 'examples.txt' and 'examples.pickle': Completed in 3 seconds.

Usage:
Please run this script from the command line (CMD)

Example:
python K_getexamples.py

In total, 41,512 examples were captured by this script.
"""

import json
import pickle
import re

# load the json file
with open("englishidioms/phrases.json", encoding="UTF-8") as f:
    data = json.load(f)

# a list that contain examples and their associated range
# [[[range], [examples]], [[range], [examples]], [[range], [examples]]]
er = []

processed_ranges = []

for entry in data["dictionary"]:
    if entry["range"] in processed_ranges:
        continue
    matches = [
        m
        for m in re.findall(
            r"_.+?<\/em>[ ]*<(?!em)", entry["definition_html"]
        )
        if m
    ]
    if matches:
        er.append(
            [
                entry["range"],
                [
                    re.sub(r"<[a-z\/]+?>", "", match)
                    .replace("<", "")
                    .replace("_", "")
                    .replace("  ", "")
                    .strip()
                    for match in matches
                ],
            ]
        )
        processed_ranges.append(entry["range"])


# output file #1
with open("files/examples.txt", "w", encoding="UTF-8") as f:
    for r, e in er:
        f.write(str(r))
        f.write(str(e))
        f.write("\n")

# output file #2
with open("files/examples.pickle", "wb") as file:
    pickle.dump(er, file)