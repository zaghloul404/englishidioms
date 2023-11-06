""" Break the text in clean-output.docx into individual dictionary entries

Description:
This script goes through clean-output.docx and breaks it into individual dictionary entries,
and gets the range (start line, end line) of each entry - non-valid entries are ignored.

Example of a valid dictionary entry:
    the ABCs of something Fig. the basic facts or principles of something. _I have never mastered the ABCs of car maintenance.

non-valid entries are there to reference a previous/next entry or some other entry. e.g. "able to breathe (freely) again Go to previous."

Input:
- clean-output.docx: The input DOCX file containing data to process.

Output:
- ranges.pickle: The main output file containing ranges for all valid entries as a list of tuples.
- clean_entries.txt (optional): A text file containing valid entries.
- clean_entries.docx (optional): A DOCX file containing valid entries.
- deleted_entries.txt (optional): A text file containing non-valid entries.

Thought Process:
- we loop through the lines of the docx file, and look for the range of each entry.
- the goal here is recognize individual dictionary entries and know where each entry exists in the book.
- in other words, we should be able to tell that entry #1 goes from line 0 through 3, entry #2 goes from line 3 through 6, etc.
- the ranges will be used later to parse data from each entry.

Runtime:
- Creating ranges.pickle: Completed in 27 seconds.
- Creating deleted_entries.txt: Completed in 0 seconds (optional).
- Creating clean_entries.txt: Completed in 2 minutes and 46 seconds (optional).
- Creating clean_entries.docx: Completed in 12 minutes and 8 seconds (optional).

Usage:
Please run this script from the command line (CMD)

Example:
python A_breakitup.py
"""


import docx
import pickle
from tqdm import tqdm
from Z_module import copy_docx


def typically():
    """returns True if the beginning of the line looks like this: 'be ~; go ~; run ~; turn ~.) _ When did the'"""
    try:
        if (
            line.runs[0].bold
            and line.runs[0].font.name == "Formata-Medium"
            and line.runs[1].bold
            and line.runs[1].font.name == "Minion-Black"
            and line.runs[1].text.strip() == "~"
        ):
            return True
        elif (
            line.runs[0].bold
            and line.runs[0].font.name == "Formata-Medium"
            and line.runs[1].font.name == "Minion-Regular"
            and line.runs[1].text.strip() == ".)"
        ):
            return True
        else:
            return False
    except:
        return False


# step 1: open up the document
doc = docx.Document("files/clean-output.docx")
lines = doc.paragraphs


# step 2: determine where each entry begin and ends
"""
how to tell if this is the beginning of an entry
1: line begins with a bold text
2: line begins with 'a', 'an' 'the', and then bold text
"""
articles = [
    "a",
    "an",
    "the",
]  # all possible articles with 'Minion-Regular' font that precede a constant
runs0vairable = [
    "one’s",
    "someone",
    "someone’s",
    "something",
    "someone or something",
    "somewhere",
    "some creature’s",
    "do something",
]  # all possible variables in runs[0] with 'Formata-Condensed' font that precede a constant
beginning = (
    []
)  # every item is a line number in clean-output.docx that marks a new entry
ignore = []  # line numbers to ignore when looking for entry beginnings and endings
ranges = []  # a list of tuples (beginning line number, ending line number)

for line_number, line in enumerate(lines):
    # ignore empty lines
    if len(line.text) == 0:
        continue

    # keep in mind: if there is a single empty line on the docx document, it would miss up the code and return a IndexError: list index out of range
    #               because of 'lines[line_number -1].runs[-1]' part as the empty line won't have any runs

    if (
        # ignore the line if it begins with a constant, and the previous line ends with a variable
        not (
            line.runs[0].bold
            and line.runs[0].font.name == "Formata-Medium"
            and lines[line_number - 1].runs[-1].font.name == "Formata-Condensed"
            and lines[line_number - 1].runs[-1].font.size.pt == float("9.0")
        )
        and
        # ignore the line if the previous line ends with 'Usually' | this picks up entries with a long phrase
        (not lines[line_number - 1].runs[-1].text.strip().endswith("Usually"))
        and
        # ignore the line if the previous line ends with a constant | this picks up entries with a long phrase
        (
            not (
                lines[line_number - 1].runs[-1].bold
                and lines[line_number - 1].runs[-1].font.name == "Formata-Medium"
            )
        )
        and
        # ignore the line if the previous line ends with ';'
        (not lines[line_number - 1].text.endswith(";"))
        and
        # ignore the line if the previous line had '*Typically:' and this line has '~;'
        not ("*Typically:" in lines[line_number - 1].text and "~;" in line.text)
        and
        # ignore lines in [ignore]
        (line_number not in ignore)
        and
        # sometimes the beginning of the line is just an example. example numbers come in bold fond. ignore those lines
        (
            line.runs[0].text.strip()
            not in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
        )
        and
        # ignore the line if it begins like this: ''be ~; go ~; run ~; turn ~.) _ When did the''
        (not typically())
        and (
            # if the 1st run in the line is bold and has 'Formata-Medium' then it's probably a beginning of a phrase
            (line.runs[0].bold and line.runs[0].font.name == "Formata-Medium")
            or
            # if the 1st run is 'a','an', or 'the' and the 2nd run is bold
            (
                (line.runs[0].text.strip().lower() in articles)
                and line.runs[0].font.name == "Minion-Regular"
                and line.runs[1].bold
                and line.runs[1].font.name == "Formata-Medium"
            )
            or
            # if the 1st run is in runs0vairable and the 2nd run is bold (and the 2nd run does not start with ')' )
            (
                line.runs[0].text.strip().lower() in runs0vairable
                and line.runs[0].font.name == "Formata-Condensed"
                and line.runs[1].bold
                and line.runs[1].font.name == "Formata-Medium"
                and (not line.runs[1].text.startswith(")"))
            )
            or
            # I'm throwing this if statement for a single entry 'the someone or something from hell'
            (
                line.runs[0].text.strip() == "the"
                and line.runs[0].font.name == "Minion-Regular"
                and line.runs[1].text.strip() == "someone or something"
                and line.runs[1].font.name == "Formata-Condensed"
                and line.runs[2].bold
                and line.runs[2].font.name == "Formata-Medium"
                and line.runs[2].text.strip() == "from hell"
            )
        )
    ):
        beginning.append(line_number)

        # let take a closer look at the current line - break it down into runs
        # In the context of the Python-docx library, "runs" refer to a sequence of characters within a paragraph in a Microsoft Word document that share the same set of character-level formatting properties.
        # Runs are used to represent portions of text with consistent formatting, such as font style, size, color, and other character-level attributes.
        runs = line.runs
        for run in runs:
            # sometimes an entry could contain two phrases, and there is an 'and' separating them. this could lead to the next line having it's 1st run as bold.
            # in this case the next line should not be considered as a new entry, but rather a continuation of the same entry

            if (
                run.text.strip() == "and"
                and run.font.name == "Minion-Regular"
                and int(run.font.size.pt) == 7
            ):
                # ignore next line
                ignore.append(line_number + 1)


# create ranges for each entry
for i, v in enumerate(beginning[:-1]):
    # NOTE: the final entry in the document won't be included, because there is no next beginning, and we can't calculate range this way
    start = v
    end = beginning[i + 1] - 1
    ranges.append((start, end))


# step 3: remove non-valid entries from [ranges]
ranges_to_delete = [
    (41058, 41059),
    (47646, 47648),
]  # a list that includes ranges to delete from [ranges]


# every iteration is an entry
for s, e in ranges:
    if s == e:
        # that means the entry is a single line
        runs = lines[s].runs
        for run in runs:
            if (
                "Go to" in run.text.strip()
                and run.font.name == "Minion-Regular"
                and run.font.size.pt == float("8.5")
            ):
                # 1838 matches
                ranges_to_delete.append((s, e))

        # also ignore any lines that have any of the following in them
        d = [
            "See the entries beginning with",
            "See also the entries beginning with",
            "See previous.",
            "See also entries at",
            "See The game is up.",
        ]

        if any(item.lower() in lines[s].text.lower() for item in d):
            ranges_to_delete.append((s, e))

    else:
        # check the 1st two lines of the entry for 'Go to'
        for i in range(s, s + 2):
            runs = lines[i].runs

            for run in runs:
                if (
                    "1." not in lines[i].text
                    and "Go to" in run.text.strip()
                    and run.font.name == "Minion-Regular"
                    and run.font.size.pt == float("8.5")
                ):
                    # 785 matches
                    ranges_to_delete.append((s, e))

        # check one more time for those entries where the 1st line ends with 'Go' and the 2nd line begins with 'to'
        if (
            lines[s].runs[-1].text.strip().endswith("Go")
            and lines[s].runs[-1].font.name == "Minion-Regular"
            and lines[s].runs[-1].font.size.pt == float("8.5")
        ) and (
            "to" in lines[s + 1].runs[0].text.strip()
            and lines[s + 1].runs[0].font.name == "Minion-Regular"
            and lines[s + 1].runs[0].font.size.pt == float("8.5")
        ):
            # 22 matches
            ranges_to_delete.append((s, e))

        # delete entries that contain "See the expressions"
        for i in range(s, s + 2):
            runs = lines[i].runs
            for run in runs:
                if (
                    "See the expressions" in run.text.strip()
                    and run.font.name == "Minion-Regular"
                    and run.font.size.pt == float("8.5")
                ):
                    # 3 matches
                    ranges_to_delete.append((s, e))

# remove ranges in [ranges_to_delete] from [ranges]
clean_ranges = [item for item in ranges if item not in ranges_to_delete]

# step 4: some entries don't fit any of the rules above, and needs to be merged manually.
to_merge = [
    [(17857, 17857), (17858, 17861)],
    [(55963, 55965), (55966, 55974)],
    [(82682, 82683), (82684, 82688)],
    [(39577, 39578), (39579, 39581)],
    [(39214, 39215), (39216, 39217)],
    [(31413, 31417), (31418, 31421)],
]

# merge and add new ranges to []
for llist in to_merge:
    # get index of 1st tuple in the ranges list
    x = clean_ranges.index(llist[0])

    # merge two tuples
    start = llist[0][0]
    end = llist[1][1]

    new_range = (start, end)

    # add new range to clean_ranges
    clean_ranges.insert(x + 2, new_range)

# delete old ones
indexes_to_delete = []  # old unmerged ranges that I want to delete
for llist in to_merge:
    # get index of 1st tuple in the ranges list
    x = clean_ranges.index(llist[0])
    # delete both indexes
    indexes_to_delete.append(x)
    indexes_to_delete.append(x + 1)

# deleting them in reverse order so that I don't throw off the subsequent indexes.
for indx in sorted(indexes_to_delete, reverse=True):
    del clean_ranges[indx]


# Output File #1 - main
with open("files/ranges.pickle", "wb") as file:
    pickle.dump(clean_ranges, file)


# Output File #2 (optional) - uncomment lines 329-340
# save ranges_to_delete to a txt file to make sure only bad entries were eliminated
# text_file_1 = str()
# for s, e in ranges_to_delete:
#     # add range
#     text_file_1 = text_file_1 + "\n" + f"[{s}, {e}]"
#     # add entry lines from clean-output.docx
#     for i in range(s, e + 1):
#         text_file_1 = text_file_1 + "\n" + lines[i].text
#     # add a line break after each entry
#     text_file_1 = text_file_1 + "\n" + "*" * 50
# # write string to desk
# with open("files/deleted_entries.txt", "w") as myfile:
#     myfile.write(text_file_1)


# Output File #3 (optional) - uncomment lines 346-358
# save clean_ranges to a text file
# Note: writing the whole file to a string variable and calling write() once is 16x faster than calling write() 3 times in every iteration
# print("creating clean_entries.txt")
# text_file_2 = str()
# for s, e in tqdm(clean_ranges):
#     # add range
#     text_file_2 = text_file_2 + "\n" + f"[{s}, {e}]"
#     # add entry lines from clean-output.docx
#     for i in range(s, e + 1):
#         text_file_2 = text_file_2 + "\n" + lines[i].text
#     # add a line break after each entry
#     text_file_2 = text_file_2 + "\n" + "*" * 50
# # write string to desk
# with open("files/clean_entries.txt", "w") as myfile:
#     myfile.write(text_file_2)


# Output File #4 (optional) - uncomment line # 364
# save clean_ranges to a docx file - for better readability
# copy_docx(clean_ranges, "clean_entries")
