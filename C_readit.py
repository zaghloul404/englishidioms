""" Parse Dictionary Entries with Multiple Idiomatic Expressions

Description:
This script processes dictionary entries with multiple idiomatic expressions in 
'clean-output.docx', extracting and organizing the following data for each entry:
- phrase (string): The idiomatic expression in plain text format.
- phrase_html (string): The idiomatic expression in HTML format.
- definition (string): The definition(s) and example(s) of the idiomatic expression 
in plain text format.
- definition_html (string): The definition(s) and example(s) of the idiomatic expression 
in HTML format.
- runs (list): A list of 'runs' in the entry head.
- alt (list): A list of alternative naming for each run in the runs list, used to identify 
the type of each run. The runs and alt lists are always of the same length.

Input:
- ranges_MULT.pickle: A pickle file containing a list of tuples, where each tuple 
represents the start and end lines of dictionary entries in 'clean-output.docx'.

Output:
- phrases.json: A JSON file containing data collected from all dictionary entries.
- entry_details.pickle: A binary file containing processed details from the 'cleanup()' 
function for faster runtime on subsequent script runs.

Thought Process:
- We iterate through dictionary entries with multiple expressions in 'clean-output.docx', 
extracting the entry head and breaking it down into single expressions.
- All single expressions share the same definition(s) and example(s) within the entry.
- We package the collected data for each expression into Python dictionaries and save 
it to phrases.json.


Runtime:
- Creating phrases.json for the first time: Completed in 19 minutes.
- Note: Most of the time consumed is for processing entries through the 'cleanup()' function 
for the first time. 
The output of all the function processing gets saved to 'entry_details.pickle' so that when 
you run the script for the second time, the runtime becomes 1 minute and 52 seconds.


Usage:
Please run this script from the command line (CMD)

Example:
python C_readit.py
"""

import json
import pickle
import re

import docx
from tqdm import tqdm

from Z_module import CompactJSONEncoder, cleanup, parse_entry, runtype


def split_by_semicolon(alt, runs):
    """
    Splits elements within the given lists if a semicolon (';') is found in one of the runs and updates alt to match the new structure.

    Args:
        alt (List[str]): A list of phrase alternatives.
        runs (List[str]): A list of runs where semicolons trigger splits.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists:
            1. Updated `alt` with semicolons inserted as separators.
            2. Updated `runs` with runs split at semicolons.

    Example:
        Input:
            alt = ["constant", "constant"]
            runs = ["all over hell and half of Georgia;", "all over hell and gone; to hell and gone "]

        Output:
            alt = ['constant', ';', 'constant', ';', 'constant']
            runs = ['all over hell and half of Georgia', ';', 'all over hell and gone', ';', ' to hell and gone ']
    """

    new_alt = []
    new_runs = []

    for i, (a, r) in enumerate(zip(alt, runs)):
        if ";" in r:
            # split the run by ;
            for e in re.split("(;)", r):
                if len(e.strip()) == 0:
                    continue
                elif e == ";":
                    new_alt.append(";")
                    new_runs.append(e)
                else:
                    new_alt.append(alt[i])
                    new_runs.append(e)
        else:
            new_alt.append(alt[i])
            new_runs.append(runs[i])

    return new_alt, new_runs


def split_by_value(alt, runs, value):
    """
    Splits the provided `alt` and `runs` lists into smaller sublists based on a given `value`.

    Args:
        alt (List[str]): A list of phrase alternatives.
        runs (List[str]): A list of runs associated with the alternatives.
        value (str): The value used as a separator to split the lists.

    Returns:
        Tuple[List[List[str]], List[List[str]]]: A tuple containing two lists:
            1. `alt_result`: Sublists of alternative phrases separated by the `value`.
            2. `runs_result`: Sublists of runs associated with the separated alternative phrases.

    Example:
        Input:
            alt = ["constant", "value", "constant", "constant", "value", "constant"]
            runs = ["run1", "run2", "run3", "run4", "run5", "run6"]
            value = "value"

        Output:
            alt_result = [['constant'], ['constant', 'constant'], ['constant']]
            runs_result = [['run1'], ['run3', 'run4'], ['run6']]
    """

    alt_result = []
    runs_result = []
    temp_alt = []
    temp_runs = []

    for a, r in zip(alt, runs):
        if a.strip() == value:
            alt_result.append(temp_alt)
            runs_result.append(temp_runs)
            temp_alt = []
            temp_runs = []
        else:
            temp_alt.append(a)
            temp_runs.append(r)

    # Append the last sublists
    alt_result.append(temp_alt)
    runs_result.append(temp_runs)

    return alt_result, runs_result


# load multiple phrase entry ranges []
with open("files/ranges_MULT.pickle", "rb") as file:
    ranges_MULT = pickle.load(file)

# open up clean-output.docx
doc = docx.Document("files/clean-output.docx")
lines = doc.paragraphs

# create a json string
json_string = """
{
  "dictionary": [

  ]
}
"""

# load json to python from a string
file = json.loads(json_string)

print(
    "creating 'phrase', 'html', 'definition', 'alt', and 'runs' for multiple phrase entries"
)
# go through each entry (start, end)
for s, e in tqdm(ranges_MULT):
    # create two lists for runs/alt pairs for the entire entry
    line_alt = []
    line_runs = []

    for i in range(s, e + 1):
        runs = lines[i].runs

        for ri, run in enumerate(runs):
            line_alt.append(runtype(ri, run, "MUL"))
            line_runs.append(run.text)

    # remove all items in both lists from the 1st 'definition' and beyond - only keep the entry head
    line_alt, line_runs = cleanup(line_alt, line_runs)

    # break down line_alt & line_runs to a smaller parts that represent individual phrases
    final_alt = []
    final_runs = []
    # a- split runs by semicolon if there was any
    a1, r1 = split_by_semicolon(line_alt, line_runs)
    # b- remove semicolons if split_by_semicolon()
    a2, r2 = split_by_value(a1, r1, ";")  # each is a list of lists
    # c- break it down to a smaller alt,runs if there was 'and'
    for l1, l2 in zip(a2, r2):
        a3, r3 = split_by_value(l1, l2, "and")  # each is a list of lists
        for aa, rr in zip(a3, r3):
            final_alt.append(aa)
            final_runs.append(rr)

    # now that I know which part of the entry is the entry head, and which part is the definition/examples
    # let's create "phrase", "phrase_html", "definition_html"
    # note: a3, r3, phrase_text, phrase_html should have the same length
    phrase_text, phrase_html, entry_body_html = parse_entry(
        (s, e), len(line_runs), multiple_phrases=True, line_runs=final_runs
    )

    # add entries to json file
    for x in range(len(phrase_text)):
        data = {
            "range": [s, e],
            "phrase": phrase_text[x]
            .replace("  ", " ")
            .replace(" †", "†")
            .replace("( ", "(")
            .replace(" )", ")"),
            "phrase_html": phrase_html[x],
            "definition": re.sub("<.+?>", "", entry_body_html),
            "definition_html": entry_body_html,
            "alt": [
                item.strip().lower() for item in final_alt[x]
            ],  # strip each element from trailing/leading white space and lowercase all characters
            "runs": [item.strip().lower() for item in final_runs[x]],
            "multiple": True,  # to indicate that this was part of an entry with multiple expressions
            "duplicate": False,  # to indicate that this is an original entry in phrases.json
        }

        file["dictionary"].append(data)

# save it all to phrases.json
with open("englishidioms/src/phrases.json", "w", encoding="UTF8") as f:
    json.dump(file, f, indent=2, cls=CompactJSONEncoder, ensure_ascii=False)
