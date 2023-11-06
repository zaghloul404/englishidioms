""" Separate single phrase entries from multiple phrase entries

Description:
This script goes through ranges.pickle and determines if each dictionary entry contains a single or multiple idiomatic expressions.

Example of a dictionary entry with a single expression:
    abandon oneself to something to yield to the comforts or
    delights of something. _ The children abandoned themselves
    to the delights of the warm summer day.

Example of a dictionary entry with multiple expressions:
    able to do something blindfolded and able to do something
    standing on one’s head Fig. able to do something
    very easily, possibly without even looking. (Able to can be
    replaced with can.) _ Bill boasted that he could pass his
    driver’s test blindfolded.

Input:
- ranges.pickle: This pickle file contains a list of tuples, where each tuple consists of two integers representing the start and end lines of dictionary entries in 'clean-output.docx'.

Output:
- ranges_SNGL.pickle: Ranges for entries with single expressions (list of tuples).
- ranges_MULT.pickle: Ranges for entries with multiple expressions (list of tuples).
- single_phrase_entries.txt (optional): Entries with single expressions (text file).
- single_phrase_entries.docx (optional): Entries with single expressions in DOCX format for better readability.
- multiple_phrase_entries.txt (optional): Entries with multiple expressions (text file).
- multiple_phrase_entries.docx (optional): Entries with multiple expressions in DOCX format for better readability.

Thought Process:
- A dictionary entry consists of three core parts: entry head, definition, and example, each with unique font formatting.
- We differentiate between single and multiple idiomatic expressions based on characteristics of the entry head.
- To analyze each entry in 'clean-output.docx', we break it down into 'runs' and use the 'runtype()' function to identify each part.
- This approach helps us identify the entry head.
- If the entry head includes 'and' in 'Minion-Regular' font with a text size of 7, it indicates multiple expressions.
- If the entry head contains a semicolon ';', it also suggests the presence of multiple expressions.



Runtime:
- Creating ranges_SNGL.pickle and ranges_MULT.pickle: Completed in 19 seconds.
- Creating single_phrase_entries.txt: Completed in 2 minutes and 17 seconds (optional).
- Creating single_phrase_entries.docx: Completed in 9 minutes and 45 seconds (optional).
- Creating multiple_phrase_entries.txt: Completed 5 seconds (optional).
- Creating multiple_phrase_entries.docx: Completed 27 seconds (optional).

Usage:
Please run this script from the command line (CMD)

Example:
python B_breakitup.py
"""

import docx
import pickle
from tqdm import tqdm
from Z_module import runtype, cleanup, copy_docx


# load [ranges]
with open("files/ranges.pickle", "rb") as file:
    ranges = pickle.load(file)

# open up clean-output.docx
doc = docx.Document("files/clean-output.docx")
lines = doc.paragraphs

ranges_SNGL = []  # a list of ranges - entries with single phrase
ranges_MULT = []  # a list of ranges - entries with multiple phrases

# go through each entry (start, end) and determine if it has a single phrase or multiple phrases
for s, e in tqdm(ranges):
    multiple_phrases = False

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

    for a, r in zip(line_alt, line_runs):
        if (a == "and") or (a == "variable" and r.strip().endswith(";")):
            multiple_phrases = True

    if multiple_phrases:
        # 2421 multiple phrase entries
        ranges_MULT.append((s, e))
    else:
        ranges_SNGL.append((s, e))


# Output File #1
# pickle ranges_SNGL
with open("files/ranges_SNGL.pickle", "wb") as file:
    pickle.dump(ranges_SNGL, file)

# Output File #2
# pickle ranges_MULT
with open("files/ranges_MULT.pickle", "wb") as file:
    pickle.dump(ranges_MULT, file)

# Output File #3 (optional) - uncomment lines 110-122
# save single phrase entries to a text file
# print("creating single_phrase_entries.txt")
# text_file_1 = str()
# for s, e in tqdm(ranges_SNGL):
#     # add range
#     text_file_1 = text_file_1 + "\n" + f"[{s}, {e}]"
#     # add entry lines from clean-output.docx
#     for i in range(s, e + 1):
#         text_file_1 = text_file_1 + "\n" + lines[i].text
#     # add a line break after each entry
#     text_file_1 = text_file_1 + "\n" + "*" * 50
# # write string to desk
# with open("files/single_phrase_entries.txt", "w") as myfile:
#     myfile.write(text_file_1)

# Output File #4 (optional) - uncomment line 126
# save single phrase entries to a docx file - for better readability
# copy_docx(ranges_SNGL, "single_phrase_entries")

# Output File #5 (optional) - uncomment lines 130-142
# save multiple phrase entries to a text file
# print("creating multiple_phrase_entries.txt")
# text_file_2 = str()
# for s, e in tqdm(ranges_MULT):
#     # add range
#     text_file_2 = text_file_2 + "\n" + f"[{s}, {e}]"
#     # add entry lines from clean-output.docx
#     for i in range(s, e + 1):
#         text_file_2 = text_file_2 + "\n" + lines[i].text
#     # add a line break after each entry
#     text_file_2 = text_file_2 + "\n" + "*" * 50
# # write string to desk
# with open("files/multiple_phrase_entries.txt", "w") as myfile:
#     myfile.write(text_file_2)

# Output File #6 (optional) - uncomment line 146
# save multiple phrase entries to a docx file - for better readability
# copy_docx(ranges_MULT, "multiple_phrase_entries")
