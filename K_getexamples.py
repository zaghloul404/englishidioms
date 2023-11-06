"""Extract Examples from 'clean-output.docx'

Description:
This script is designed to parse dictionary entries from the 'clean-output.docx' document, extracting and saving the examples contained within each entry.
It takes 'ranges.pickle' and 'clean-output.docx' as input and generates 'examples.txt' (optional) and 'examples.pickle' as output.

The process involves iterating through all dictionary entries as defined by the provided entry ranges in 'ranges.pickle'.
For each entry, it gathers the associated text from the document and uses regular expressions to identify and extract example sentences, saving both the examples and their corresponding ranges.
The script offers two output formats: a human-readable 'examples.txt' file and a serialized 'examples.pickle' file.

Input:
- ranges.pickle
- clean-output.docx

Output:
- examples.txt (optional)
- examples.pickle

Runtime:
- Generating 'examples.txt' and 'examples.pickle': Completed in 3 seconds.

Usage:
Please run this script from the command line (CMD)

Example:
python K_getexamples.py

In total, 41,259 examples were captured by this script.
"""

import docx, pickle, re


doc = docx.Document("files/clean-output.docx")
lines = doc.paragraphs

with open("files/ranges.pickle", "rb") as file:
    ranges = pickle.load(file)

er = (
    []
)  # a list that contain examples and their associated range [[[range], [examples]], [[range], [examples]], [[range], [examples]]]

for s, e in ranges:
    entry_text = str()
    for i in range(s, e + 1):
        entry_text = entry_text + lines[i].text + " "

    match = re.findall(
        r"_[a-zA-Z’,!?.\-—:()“” ]+|_[a-zA-Z’,!?.\-—:()“”$ ]+[0-9]+(?!\.)[a-zA-Z’,!?.\-—:()“” ]+",
        entry_text,
    )

    if match:
        er.append([[s, e], [m.replace("_", "").strip() for m in match]])


# output file #1
with open("files/examples.txt", "w", encoding="UTF-8") as f:
    for r, e in er:
        f.write(str(r))
        f.write(str(e))
        f.write("\n")

# output file #2
with open("files/examples.pickle", "wb") as file:
    pickle.dump(er, file)
