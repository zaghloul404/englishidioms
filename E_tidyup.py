""" Parse Optional Constants and Correct Special Entries in phrases.json

Description:
This script iterates through all dictionary entries in phrases.json and applies the fixpairs() function to process and
parse optional constants and resolve special entries, ensuring data consistency and accuracy.

Input:
- phrases.json

Output:
- Updated phrases.json

Runtime:
- Generating the updated phrases.json: Completed in 3 seconds.

Usage:
Please run this script from the command line (CMD)

Example:
python E_tidyup.py
"""

import json
import re

from Z_module import CompactJSONEncoder


def fixpairs(line_alt, line_runs, second_run=0):
    """
    Fix and process line_alt and line_runs to handle o-constant replacements.

    This function examines the content of line_runs for o-constant patterns and adjusts line_alt
    and line_runs accordingly. It's structured into two main parts:

    1. Special cases: Address specific dictionary entries that do not adhere to general rules and
    require manual adjustments.

    2. Regular expressions (regex) part: Apply regex patterns to identify and modify o-constant
    occurrences in the provided lines. This part is designed to handle general cases
    that follow specific rules and patterns.

    Args:
        line_alt (list): A list representing the 'alt' component of the dictionary entry.
        line_runs (list): A list representing the 'runs' component of the dictionary entry.
        second_run (int, optional): An integer flag to indicate the second pass of the function.
            Default is 0.

    Returns:
        tuple: A tuple containing modified 'alt' and 'runs' lists, and potential duplicate
        'alt' and 'runs' lists if applicable, depending on the provided input and flags.

    Note:
    The function performs multiple passes on the input data, as indicated by the 'second_run' flag,
    to ensure comprehensive o-constant handling and modifications.
    """

    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #                      SPECIAL CASES
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # CASES#1
    if line_alt == ["constant"] and line_runs == [
        "You (always) give up too eas(il)y. "
    ]:
        line_alt = ["constant", "o-constant", "constant"]
        line_runs = ["You", "always", "give up too easily"]

        duplicate_line_alt = ["constant", "o-constant", "constant"]
        duplicate_line_runs = ["You", "always", "give up too easy"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs

    # CASES#2
    if line_alt == ["constant", "variable"] and line_runs == [
        "above ",
        "(doing) something ",
    ]:
        # there is an exception for "range": [118, 120]
        # it's the only entry that has an o-constant with 'Formata-Condensed' non-bold font - hence, runtype() recognize it as a variable

        line_alt = ["constant", "o-constant", "variable"]
        line_runs = ["above", "doing", "something"]

        return line_alt, line_runs, None, None

    # CASES#3
    if line_alt == ["constant"] and line_runs == ["ba(t)ch (it) "]:
        line_alt = ["constant"]
        line_runs = ["bach it"]

        duplicate_line_alt = ["constant", "o-constant"]
        duplicate_line_runs = ["batch", "it"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs

    # CASES#4
    if line_alt == ["constant"] and line_runs == [
        "Can’t say (a)s I do(, can’t say (a)s I don’t). "
    ]:
        line_alt = ["constant", "o-constant"]
        line_runs = ["Can’t say as I do", "can’t say as I don’t"]

        duplicate_line_alt = ["constant", "o-constant"]
        duplicate_line_runs = ["Can’t say I do", "can’t say I don’t"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs

    # CASES#5
    if line_alt == ["constant"] and line_runs == ["Yes indeed(y (do))! "]:
        line_alt = ["constant"]
        line_runs = ["Yes indeed"]

        duplicate_line_alt = ["constant", "o-constant"]
        duplicate_line_runs = ["Yes indeedy", "do"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs

    # CASES#6
    if line_alt == ["constant", "variable", "constant"] and line_runs == [
        "say ",
        "something ",
        "over (and over (again)) ",
    ]:
        line_alt = ["constant", "variable", "constant", "o-constant"]
        line_runs = ["say ", "something ", "over ", "and over again"]

        return line_alt, line_runs, None, None

    # CASE#7
    if line_alt == ["constant"] and line_runs == ["step in(to the breach) "]:
        line_alt = ["constant"]
        line_runs = ["step into the breach"]

        duplicate_line_alt = ["constant"]
        duplicate_line_runs = ["step in the breach"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs

    # CASE#8
    if line_alt == ["constant"] and line_runs == ["fall in(to step) "]:
        line_alt = ["constant"]
        line_runs = ["fall into step"]

        duplicate_line_alt = ["constant"]
        duplicate_line_runs = ["fall in step"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs

    # CASES#9
    if line_alt == ["constant"] and line_runs == [
        "You (always) give up too eas(il)y. "
    ]:
        line_alt = ["constant", "o-constant", "constant"]
        line_runs = ["You", "always", "give up too easily"]

        return line_alt, line_runs, None, None

    # CASES#10
    for i, (a, r) in enumerate(zip(line_alt, line_runs)):
        # this loop fixes 7 entries

        try:
            if (
                (a == "constant" and r.strip() == "(")
                and (line_alt[i + 1] == "variable" and line_runs[i + 1].strip() == "‘s")
                and (line_alt[i + 2] == "constant")
            ):
                # remove both "(" and "‘s"
                line_alt.pop(i + 1)
                line_runs.pop(i + 1)

                line_alt.pop(i)
                line_runs.pop(i)
        except:
            pass

    # CASES#11
    for i, (a, r) in enumerate(zip(line_alt, line_runs)):
        # this loop fixes the following 10 entries
        # ['can’t find ', 'one’s ', 'butt with both hands (in broad', 'daylight) ']
        # ['Close only counts in horseshoes (and hand', 'grenades). ']
        # ['couldn’t pour water out of a boot (if there was', 'instructions on the heel) ']
        # ['don’t have a pot to piss in (or a window to throw', 'it out of ) ']
        # ['East is East and West is West (and never the', 'twain shall meet). ']
        # ['The ', 'grass is always greener on the other side (of', 'the fence). ']
        # ['Ignorance (of the law) is no excuse (for breaking', 'it). ']
        # ['meaner than a junkyard dog (with fourteen sucking', 'pups) ']
        # ['Out of the mouths of babes (oft times come', 'gems). ']
        # ["If ifs and ands were pots and pans (there\u2019d be no", "work for tinkers\u2019 hands). "]

        try:
            if a == "constant" and line_alt[i + 1] == "constant":
                match_0 = re.search(r"\(([a-z ’]+)$", r)  # look for "( some text"
                match_1 = re.search(
                    r"^([a-z ’]+)\)[. ]*", line_runs[i + 1]
                )  # look for "some text)"

                if match_0 and match_1:
                    tmp_constant = re.sub(r"\([a-z ’]+$", "", r, count=1)
                    tmp_o_constant = match_0.group(1) + " " + match_1.group(1)

                    # delete old constants
                    line_alt.pop(i + 1)
                    line_runs.pop(i + 1)

                    line_alt.pop(i)
                    line_runs.pop(i)

                    # insert new valuse
                    line_alt.insert(i, "constant")
                    line_runs.insert(i, tmp_constant)

                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, tmp_o_constant)
        except:
            pass

    # CASES#12
    # range [31413, 31417] - because "great minds run in the same gutters" is mentioned within the entry
    if line_alt == ["constant"] and line_runs == ["great minds think alike."]:
        line_alt = ["constant"]
        line_runs = ["great minds think alike"]

        duplicate_line_alt = ["constant"]
        duplicate_line_runs = ["great minds run in the same gutters"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs

    # CASE 13
    # Fixing the following ranges - able to / can
    # [47, 53]
    if line_alt == ["constant", "constant"] and line_runs == [
        "able to breathe",
        "(freely) again 1.",
    ]:
        line_alt = ["constant", "o-constant", "constant"]
        line_runs = ["able to breathe", "freely", "again"]

        duplicate_line_alt = ["constant", "o-constant", "constant"]
        duplicate_line_runs = ["can breathe", "freely", "again"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs

    # [73, 78]
    if line_alt == ["constant"] and line_runs == ["able to fog a mirror"]:
        line_alt = ["constant"]
        line_runs = ["able to fog a mirror"]

        duplicate_line_alt = ["constant"]
        duplicate_line_runs = ["can fog a mirror"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs
    # [79, 81]
    if line_alt == ["constant", "variable"] and line_runs == [
        "able to make",
        "an event",
    ]:
        line_alt = ["constant", "variable"]
        line_runs = ["able to make", "an event"]

        duplicate_line_alt = ["constant", "variable"]
        duplicate_line_runs = ["can make", "an event"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs
    # [82, 85]
    if line_alt == ["constant"] and line_runs == ["able to take a joke"]:
        line_alt = ["constant"]
        line_runs = ["able to take a joke"]

        duplicate_line_alt = ["constant"]
        duplicate_line_runs = ["can take a joke"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs
    # [86, 90]
    if line_alt == ["constant"] and line_runs == ["able to take just so much"]:
        line_alt = ["constant"]
        line_runs = ["able to take just so much"]

        duplicate_line_alt = ["constant"]
        duplicate_line_runs = ["can take just so much"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs
    if line_alt == ["constant", "constant"] and line_runs == [
        "able to take only so",
        "much",
    ]:
        line_alt = ["constant"]
        line_runs = ["able to take only so much"]

        duplicate_line_alt = ["constant"]
        duplicate_line_runs = ["can take only so much"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs
    # CASE 14
    if line_alt == ["constant"] and line_runs == ["with all the fixin(g)s"]:
        line_alt = ["constant"]
        line_runs = ["with all the fixings"]

        duplicate_line_alt = ["constant"]
        duplicate_line_runs = ["with all the fixin’s"]

        return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs

    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #                      END OF SPECIAL CASES
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #                      REGEX PART
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # am I going to create a duplicate for this entry?
    create_duplicate = False

    # i for iteration, a for alternative, r for runs
    for i, (a, r) in enumerate(zip(line_alt, line_runs)):
        if a == "constant":
            # the order of these matches is important, also using if elif is important here
            # i don't want matches to overlap and give bad output
            # match3 will always overlap with match2

            # A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z

            match_g = re.search(r"\(y\)", r)  # look for "(y)" - 4 match

            match_h = re.search(
                r"off\s\(\(of\s\)", r
            )  # look for "off ((of )" - 19 match

            match_i = re.search(r"off\s\(of\s\)", r)  # look for "off (of )" - 10 match

            match_j = re.search(r"\(,\s(.+)\)", r)  # look for "(, " - 20 match

            match_k = re.search(
                r"\(s\)", r
            )  # remove '(s)', get_word_forms() always provides a plural form of the word - no need to take '(s)' into consideration and create a duplicate

            match_l = re.search(r"\(on\(to\)", r)  # look for "(on(to)" - 4 match

            match_m = re.search(r"on\(to\)", r)  # look for "on(to)" - 27 match

            match_n = re.search(r"\(\(up\)on\s", r)  # look for "((up)on " - 4 match

            match_o = re.search(r"\(up\)on", r)  # look for "(up)on" - 132 match

            match_p = re.search(r"\(to\(ward\)\s", r)  # look for "(to(ward) " - 1 match

            match_q = re.search(r"to\(ward\)\s", r)  # look for "to(ward) " - 6 matches

            match_r = re.search(r"\(\(in\)to", r)  # look for "((in)to" - 7 matches

            match_s = re.search(
                r"\(in\(to\)\s|\(in\(to\s", r
            )  # look for "(in(to "   ---- "(in(to) " 3 matches, "(in(to " 1 match

            match_t = re.search(
                r"\sin\(to\)\s|in\(to\)\s", r
            )  # look for "in(to) " or " in(to) "

            match_u = re.search(r"\sin\(to\s", r)  # look for " in(to " - 86 matches

            match_v = re.search(
                r"\((.+)\)(.+)\((.+)\)", r
            )  # look for 2 parentheses with word inside it ex: "(I've) (got) better things to do. "

            match_w = re.search(
                r"\((.+)\)", r
            )  # look for parentheses with word inside it ex: (you)

            match_x = re.search(
                r"(\w+)\)\s*(\w+)\s*\((\w+)", r
            )  # look for 'way) out (of' or 'way) in(to'

            match_y = re.search(
                r"\((\w+)$|\((\w+\s+\w+)$|\((\w+)\s$|\((\w+\s+\w+)\s$", r
            )  # look for a single parentheses at the end ex: (you or (as a

            match_z = re.search(
                r"([a-z ]+)\)[a-z ]+", r
            )  # look for a single parentheses ex: "fur) the wrong way"

            # A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z

            if match_g:
                # fix the following 4 entries
                # (1189, 1192)
                # (18447, 18450)
                # (22271, 22274)
                # (50310, 50312)

                # create a duplicate entry:
                create_duplicate = True

                duplicate_line_alt = list(line_alt)
                duplicate_line_runs = list(line_runs)

                # remove "(y)" from the 1st entry
                line_runs[i] = r.replace("(y)", "")
                # replace "(y)" with "y" in the 2nd entry
                duplicate_line_runs[i] = r.replace("(y)", "y")

            elif match_h:
                # print("match_h")

                if r.strip() == "off ((of )" or r.strip().endswith("off ((of )"):
                    # remove " ((of )" from the constant
                    line_runs[i] = r.replace("off ((of )", "")

                    # add two new 'o-constant'

                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, "of")

                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, "off")

                elif r.strip().startswith("off ((of )"):
                    # this conditions only matches once in range [34967, 34971]

                    # remove the whole item
                    line_alt.pop(i)
                    line_runs.pop(i)

                    # add three items in the same postions - added in reverse to keep the order
                    line_alt.insert(i, "o-constant")
                    line_runs.insert(i, "the stage")

                    line_alt.insert(i, "o-constant")
                    line_runs.insert(i, "of")

                    line_alt.insert(i, "constant")
                    line_runs.insert(i, "off")
            elif match_i:
                # print('match_i')

                if r.strip() == "off (of )" or r.strip().endswith("off (of )"):
                    # remove " ((of )" from the constant
                    line_runs[i] = r.replace("off (of )", "")

                    # add two new 'o-constant'

                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, "of")

                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, "off")
            elif match_j:
                # print("match_j")

                # remove '(, and what's inside the parentheses)'
                line_runs[i] = re.sub(r"\(,\s.+\)", "", r, count=1)

                # add what's inside the parentheses as a 'o-constant'
                line_alt.insert(i + 1, "o-constant")
                line_runs.insert(i + 1, match_j.group(1))
            elif match_k:
                # print("match_k")

                # remove '(s)' from the constant
                line_runs[i] = r.replace("(s)", "")
            elif match_l:
                # print("match_l")

                if r.strip() == "(on(to)":
                    # remove that constant from both lists
                    line_alt.pop(i)
                    line_runs.pop(i)

                    # add two new 'o-constant'
                    line_alt.insert(i, "o-constant")
                    line_runs.insert(i, "on")

                    line_alt.insert(i, "o-constant")
                    line_runs.insert(i, "onto")
                else:
                    # remove "(on(to)" from the constant item
                    line_runs[i] = r.replace("(on(to)", "")

                    # add two new 'o-constant'
                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, "on")

                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, "onto")
            elif match_m:
                # print("match_m")

                if r.strip() == "on(to)":
                    # create a duplicate entry:
                    create_duplicate = True

                    duplicate_line_alt = list(line_alt)
                    duplicate_line_runs = list(line_runs)

                    # the 1st entry should include "in" as a constant
                    line_runs[i] = r.replace("on(to)", "on")
                    # the 2nd entry should include "into" as a constant
                    duplicate_line_runs[i] = r.replace("on(to)", "onto")
                elif r.strip().endswith("on(to)"):
                    # remove "on(to)" from the constant item
                    line_runs[i] = r.replace("on(to)", "")

                    # create a duplicate entry:
                    create_duplicate = True

                    duplicate_line_alt = list(line_alt)
                    duplicate_line_runs = list(line_runs)

                    # add two new 'constant'
                    line_alt.insert(i + 1, "constant")
                    line_runs.insert(i + 1, "on")

                    duplicate_line_alt.insert(i + 1, "constant")
                    duplicate_line_runs.insert(i + 1, "onto")
                elif "on(to)" in r.strip():
                    # create a duplicate entry:
                    create_duplicate = True

                    duplicate_line_alt = list(line_alt)
                    duplicate_line_runs = list(line_runs)

                    # the 1st entry should include "in" as a constant
                    line_runs[i] = r.replace("on(to)", "on")
                    # the 2nd entry should include "into" as a constant
                    duplicate_line_runs[i] = r.replace("on(to)", "onto")
            elif match_n:
                # print("match_n")

                # remove "((up)on " from the constant
                line_runs[i] = r.replace("((up)on ", "")

                # add two new 'o-constant'

                line_alt.insert(i + 1, "o-constant")
                line_runs.insert(i + 1, "on")

                line_alt.insert(i + 1, "o-constant")
                line_runs.insert(i + 1, "upon")
            elif match_o:
                # print("match_o")

                if r.strip() == "(up)on":
                    # create a duplicate entry:
                    create_duplicate = True

                    duplicate_line_alt = list(line_alt)
                    duplicate_line_runs = list(line_runs)

                    # the 1st entry should include "on" as a constant
                    line_runs[i] = r.replace("(up)on", "on")
                    # the 2nd entry should include "upon" as a constant
                    duplicate_line_runs[i] = r.replace("(up)on", "upon")

                elif r.strip().endswith("(up)on"):
                    # remove "(up)on" from the constant item
                    line_runs[i] = r.replace("(up)on", "")

                    # create a duplicate entry:
                    create_duplicate = True

                    duplicate_line_alt = list(line_alt)
                    duplicate_line_runs = list(line_runs)

                    # add two new 'constant'
                    line_alt.insert(i + 1, "constant")
                    line_runs.insert(i + 1, "on")

                    duplicate_line_alt.insert(i + 1, "constant")
                    duplicate_line_runs.insert(i + 1, "upon")
                elif "(up)on" in r.strip():
                    # create a duplicate entry:
                    create_duplicate = True

                    duplicate_line_alt = list(line_alt)
                    duplicate_line_runs = list(line_runs)

                    # the 1st entry should include "on" as a constant
                    line_runs[i] = r.replace("(up)on", "on")
                    # the 2nd entry should include "upon" as a constant
                    duplicate_line_runs[i] = r.replace("(up)on", "upon")
            elif match_p:
                # print("match_p")

                # remove " (to(ward) " from the constant
                line_runs[i] = r.replace(" (to(ward) ", "")

                # add two new 'o-constant'
                line_alt.insert(i + 1, "o-constant")
                line_runs.insert(i + 1, "toward")

                line_alt.insert(i + 1, "o-constant")
                line_runs.insert(i + 1, "to")
            elif match_q:
                # print("match_q")

                # create a duplicate entry:
                create_duplicate = True

                duplicate_line_alt = list(line_alt)
                duplicate_line_runs = list(line_runs)

                # the 1st entry should include "to" as a constant
                line_runs[i] = r.replace("to(ward) ", "to")
                # the 2nd entry should include "toward" as a constant
                duplicate_line_runs[i] = r.replace("to(ward) ", "toward ")
            elif match_r:
                # print("match_r")

                # remove "((in)to" from the constant
                line_runs[i] = r.replace("((in)to", "")

                # add two new 'o-constant'

                line_alt.insert(i + 1, "o-constant")
                line_runs.insert(i + 1, "to")

                line_alt.insert(i + 1, "o-constant")
                line_runs.insert(i + 1, "into")
            elif match_s:
                # print("match_s")

                if r.strip() == "(in(to" or r.strip() == ") (in(to)":
                    # remove that constant from both lists
                    line_alt.pop(i)
                    line_runs.pop(i)

                    # add two new 'o-constant'
                    line_alt.insert(i, "o-constant")
                    line_runs.insert(i, "in")

                    line_alt.insert(i, "o-constant")
                    line_runs.insert(i, "into")
                else:
                    # 1 match "range": [15746, 15750]

                    # remove " (in(to) " from the constant item
                    line_runs[i] = r.replace(" (in(to) ", "")

                    # add two new 'o-constant'
                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, "in")

                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, "into")
            elif match_t:
                # print("match_t")

                # create a duplicate entry:
                create_duplicate = True

                duplicate_line_alt = list(line_alt)
                duplicate_line_runs = list(line_runs)

                # the 1st entry should include "in" as a constant
                line_runs[i] = r.replace("in(to) ", "in ")
                # the 2nd entry should include "into" as a constant
                duplicate_line_runs[i] = r.replace("in(to) ", "into ")
            elif match_u:
                # print("match_u")

                # create a duplicate entry:
                create_duplicate = True

                duplicate_line_alt = list(line_alt)
                duplicate_line_runs = list(line_runs)

                # the 1st entry should include "in" as a constant
                line_runs[i] = r.replace("in(to ", "in ")
                # the 2nd entry should include "into" as a constant
                duplicate_line_runs[i] = r.replace("in(to ", "into ")
            elif match_v:
                # print("match_v")

                # split the string
                item_x = re.split(r"\((.+)\)(.+)\((.+)\)", r, maxsplit=1)

                # remove empty strings in item
                for index, item in enumerate(item_x):
                    if len(item.strip()) == 0 or len(item.strip()) == 1:
                        item_x.pop(index)

                # construct the new alt,runs

                # 1 remove the item from both alt, runs
                line_alt.pop(i)
                line_runs.pop(i)

                # 2 add whatever inside the parentheses as 'o-constant', and the rest as 'constant'
                # note, what's inside the two parentheses is always going to be in match.group(1) and match.group(3)

                # using reversed() to keep the order while inserting into line_alt, line_runs
                for xx in reversed(item_x):
                    if xx == match_v.group(1) or xx == match_v.group(3):
                        line_alt.insert(i, "o-constant")
                        line_runs.insert(i, xx)
                    else:
                        line_alt.insert(i, "constant")
                        line_runs.insert(i, xx)
            elif match_w:
                # print("match_w")
                # split the constant run based on the match to determine it's position
                splitted = r.split(match_w.group(0))

                if len(splitted) == 2 and len(splitted[0]) == 0:
                    # that means the () was at the beginning of the string

                    # add a o-constant to the left of the constant

                    # insert new alt in line_alt
                    line_alt.insert(i, "o-constant")

                    # instert new value in line_runs - notice using match group 1 here to get the value without the ()
                    line_runs.insert(i, match_w.group(1))

                    # edit the old value in line_runs accordingly
                    line_runs[i + 1] = r.replace(match_w.group(0), "")

                elif len(splitted) == 2 and len(splitted[1]) == 0:
                    # that means the () was at the end of the string

                    # add a o-constant to the right of the constant

                    # insert new alt in line_alt
                    line_alt.insert(i + 1, "o-constant")

                    # instert new value in line_runs - notice using match group 1 here to get the value without the ()
                    line_runs.insert(i + 1, match_w.group(1))

                    # edit the old value in line_runs accordingly
                    line_runs[i] = r.replace(match_w.group(0), "")

                elif (
                    len(splitted) == 2
                    and len(splitted[0]) != 0
                    and len(splitted[1]) != 0
                ):
                    # that means the () was in the middle of the string

                    # break the constant (1 item) into >>> constant : o-constant : constant (3 items)

                    # remove that constant from both lists
                    line_alt.pop(i)
                    line_runs.pop(i)

                    # add 3 new items

                    # 1
                    line_alt.insert(i, "constant")
                    line_runs.insert(i, splitted[0])

                    # 2
                    line_alt.insert(i + 1, "o-constant")
                    line_runs.insert(i + 1, match_w.group(1))

                    # 3
                    line_alt.insert(i + 2, "constant")
                    line_runs.insert(i + 2, splitted[1])
            elif match_x:
                # print("match_x")

                # break the constant (1 item) into >>> o-constant : constant : o-constant (3 items)

                # remove that constant from both lists
                line_alt.pop(i)
                line_runs.pop(i)

                # add 3 new items

                # 1
                line_alt.insert(i, "o-constant")
                line_runs.insert(i, match_x.group(1))

                # 2
                line_alt.insert(i + 1, "constant")
                line_runs.insert(i + 1, match_x.group(2))

                # 3
                line_alt.insert(i + 2, "o-constant")
                line_runs.insert(i + 2, match_x.group(3))
            elif match_y:
                # print("match_y")

                # add a o-constant to the right of the constant

                # insert new alt in line_alt
                line_alt.insert(i + 1, "o-constant")

                # 4 regex groups, check which one has value
                for g in range(1, 5):
                    if match_y.group(g) != None:
                        group_value = match_y.group(g)
                        # #print(group_value)
                        break

                # instert new value in line_runs - notice using match group here to get the value without the ()
                line_runs.insert(i + 1, group_value)

                # edit the old value in line_runs accordingly
                line_runs[i] = r.replace(f"({group_value}", "")
            elif match_z:
                # print("match_z")

                # remove the constant
                line_alt.pop(i)
                line_runs.pop(i)

                split_r = r.split(")")

                # add a new 'o-constant'
                line_alt.insert(i, "o-constant")
                line_runs.insert(i, split_r[0])
                # add a new 'constant'
                line_alt.insert(i + 1, "constant")
                line_runs.insert(i + 1, split_r[1])

    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #                     END OF REGEX PART
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # remove "example" from entries - if they exist
    for i, (a, r) in enumerate(zip(line_alt, line_runs)):
        if a == "example":
            line_alt.pop(i)
            line_runs.pop(i)

    if second_run == 0:
        if create_duplicate:
            return line_alt, line_runs, duplicate_line_alt, duplicate_line_runs
        else:
            return line_alt, line_runs, None, None
    elif second_run == 1:
        return line_alt, line_runs, None, None


# open phrases.json
with open("englishidioms/phrases.json", encoding="UTF-8") as f:
    data = json.load(f)

# create a json string
json_string = """
{
  "dictionary": [

  ]
}
"""

# load json to python from a string - this file will contain all entries in phrases.json after being subjected to fixpairs()
file = json.loads(json_string)

for entry in data["dictionary"]:
    s = entry["range"][0]  # line number where the entry begins in clean-output.docx
    e = entry["range"][1]  # line number where the entry ends in clean-output.docx

    # run fixpairs() 3 times against each entry - fix both alt & runs lists and add 'o-constant's

    # 1st time
    (
        tmp_a_clean_alt,
        tmp_a_clean_runs,
        tmp_a_duplicate_alt,
        tmp_a_duplicate_runs,
    ) = fixpairs(entry["alt"], entry["runs"])

    # 2nd time
    if tmp_a_duplicate_alt is not None and tmp_a_duplicate_runs is not None:
        tmp_clean_alt, tmp_clean_runs, ignore0, ignore1 = fixpairs(
            tmp_a_clean_alt, tmp_a_clean_runs
        )

        # i'm passing tmp_duplicate_alt, tmp_duplicate_runs as the main arguments to do any sort of modification needed on the duplicate entries
        tmp_duplicate_alt, tmp_duplicate_runs, ignore2, ignore3 = fixpairs(
            tmp_a_duplicate_alt, tmp_a_duplicate_runs, 1
        )
    else:
        tmp_clean_alt, tmp_clean_runs, ignore0, ignore1 = fixpairs(
            tmp_a_clean_alt, tmp_a_clean_runs
        )

    # 3rd time
    if tmp_a_duplicate_alt is not None and tmp_a_duplicate_runs is not None:
        clean_alt, clean_runs, ignore4, ignore5 = fixpairs(
            tmp_clean_alt, tmp_clean_runs
        )

        # i'm passing tmp_duplicate_alt, tmp_duplicate_runs as the main arguments to do any sort of modification needed on the duplicate entries
        duplicate_alt, duplicate_runs, ignore6, ignore7 = fixpairs(
            tmp_duplicate_alt, tmp_duplicate_runs, 1
        )
    else:
        clean_alt, clean_runs, ignore4, ignore5 = fixpairs(
            tmp_clean_alt, tmp_clean_runs
        )

    # add range,clean_alt,clean_runs,duplicate_alt, duplicate_runs as it is to {data} dictionary, it would be saved later to phrases.json

    if tmp_a_duplicate_alt is not None and tmp_a_duplicate_runs is not None:
        data0 = {
            "range": [s, e],
            "phrase": entry["phrase"],
            "phrase_html": entry["phrase_html"],
            "definition": entry["definition"],
            "definition_html": entry["definition_html"],
            "alt": clean_alt,
            "runs": clean_runs,
            "multiple": entry["multiple"],
            "duplicate": False,
        }

        data1 = {
            "range": [s, e],
            "phrase": entry["phrase"],
            "phrase_html": entry["phrase_html"],
            "definition": entry["definition"],
            "definition_html": entry["definition_html"],
            "alt": duplicate_alt,
            "runs": duplicate_runs,
            "multiple": entry["multiple"],
            "duplicate": True,
        }

        file["dictionary"].append(data0)
        file["dictionary"].append(data1)

    else:
        data = {
            "range": [s, e],
            "phrase": entry["phrase"],
            "phrase_html": entry["phrase_html"],
            "definition": entry["definition"],
            "definition_html": entry["definition_html"],
            "alt": clean_alt,
            "runs": clean_runs,
            "multiple": entry["multiple"],
            "duplicate": False,
        }

        file["dictionary"].append(data)

# overwrite the file
with open("englishidioms/phrases.json", "w", encoding="UTF8") as f:
    json.dump(file, f, indent=2, cls=CompactJSONEncoder, ensure_ascii=False)
