""" Optimization Experiment Script

This script allows you to experiment with different removal amounts of incorrect entries 
in the 'phrases.json' file to enhance the accuracy of a search algorithm.
It provides a dynamic approach to determine the optimal balance for improved search results.

The script offers the following functionalities:
1. Experiment with Removal Amount:
- You can specify the number of incorrect entries to remove and evaluate the impact 
  on search accuracy.
- The script calculates the most frequently occurring incorrect entries and their effect on the 
  accuracy of search results based on the latest validation data.
- It provides information about the results before and after the removal of these entries, 
  including the average number of results per match.

2. Delete Incorrect Entries:
- After reviewing the impact of removal, you have the option to permanently delete the 
  specified number of most frequently occurring incorrect entries from 'phrases.json.'

Please note: After running the script for the first time, it was determined that removing 
the 318 most frequently occurring incorrect entries from 'phrases.json' resulted in a significant 
reduction in the number of results provided for search queries (approximately 47%) while 
retaining the same accuracy level.
"""


import os
import pickle
import sys
import json
from Z_module import CompactJSONEncoder


def remove_entries(entries):
    # load the json file
    with open("englishidioms/phrases.json", encoding="UTF-8") as f:
        phrases = json.load(f)

    # create a json string
    json_string = """
    {
      "dictionary": [

      ]
    }
    """

    # load json to python from a string
    file = json.loads(json_string)

    for entry in phrases["dictionary"]:
        if entry["range"] not in entries:
            file["dictionary"].append(entry)

    # overwrite the file
    with open("englishidioms/phrases.json", "w", encoding="UTF8") as f:
        json.dump(file, f, indent=2, cls=CompactJSONEncoder, ensure_ascii=False)

    # 2- remove deleted ranges from examples.pickle
    with open("files/examples.pickle", "rb") as file:
        examples = pickle.load(file)

    examples_after_edit = []
    for example in examples:
        if example[0] not in entries:
            examples_after_edit.append(example)

    # overwrite the file
    with open("files/examples.pickle", "wb") as file:
        pickle.dump(examples_after_edit, file)


def experiment(count):
    # read validation files and get the newest one
    validation_files = [f for f in os.listdir("files") if "validation_data" in f]

    # Sort the validation_files based on creation time in descending order
    validation_files.sort(
        key=lambda f: os.path.getctime(os.path.join("files", f)), reverse=True
    )

    # load up raw data
    with open(f"files/{validation_files[0]}", "rb") as file:
        raw_data = pickle.load(file)

    # count correct matches
    correct_match_count = 0
    for d in raw_data:
        if d["match"]:
            correct_match_count += 1

    # count results given for correct matches
    total_results_count = 0
    for d in raw_data:
        if d["match"]:
            total_results_count = total_results_count + d["results_count"]

    # let's find out the most repeated bad entries
    bad_results = []
    for d in raw_data:
        if d["match"]:
            results_copy = list(d["results"])
            del results_copy[d["match_index"] - 1]
            bad_results.extend(results_copy)

    xx = [tuple(x) for x in bad_results]  # convert the lists in bad_results to tuples

    bad_results_count = dict()
    for r in xx:
        bad_results_count[r] = bad_results_count.get(r, 0) + 1

    lst = []
    for key, val in bad_results_count.items():
        newtup = (val, key)
        lst.append(newtup)

    lst = sorted(lst, reverse=True)

    slst = list(lst[:count])  # sliced copy of lst

    bcount = 0  # how many times the top 'count' items of bad_results were mentioned
    for val, key in slst:
        # print(key, val)
        bcount = bcount + val

    report_str = (
        "\n\n"
        f"According to {validation_files[0]},\n\n"
        f"The {count} most frequently occurring incorrect entries were suggested {format(bcount, ',d')} times.\n\n"
        f"If these entries were removed from phrases.json, \n\n"
        "Before: \n"
        f"      Results given for correct matches: {format(total_results_count, ',d')} (avg. {round(total_results_count / correct_match_count)} result/match)\n\n"
        "After: \n"
        f"      Results given for correct matches: {format(total_results_count - bcount, ',d')} ({int((1-((total_results_count - bcount) / total_results_count)) * 100)}% drop) "
        f"(avg. {round((total_results_count - bcount) / correct_match_count)} result/match)."
        + "\n\n"
    )

    return report_str, slst


print(
    "\nExperiment with different removal amounts of incorrect entries in phrases.json to find the optimal balance."
)

while True:
    amount = input(
        "How many entries would you like to remove to improve search accuracy? "
    )
    if amount.isdecimal():
        calculate = experiment(int(amount))
        print(calculate[0])
        print(
            "What would you like to do:\n"
            f"1) Delete the {amount} most frequently occurring incorrect entries from phrases.json\n"
            "2) Experiment some more"
        )
        while True:
            decide = input("Select an option [1-2,q(quit)]: ")
            if decide == "q":
                sys.exit()
            elif decide == "2":
                break
            elif decide == "1":
                delete = input(
                    "Deleting the entries is irreversible, type delete to confirm: "
                )
                if delete == "delete":
                    remove_entries(calculate[1])
