r""" Script for Validating the Search Algorithm

Description:
This script is designed to validate the functionality of the `get_potential_matches()` and 
`look_closer()` functions in 'L_algorithm.py' by testing them against a large dataset of examples.
The purpose is to verify if the results obtained from the search algorithm correctly match the 
expected dictionary range for each example.
This validation process is critical for ensuring the accuracy and reliability of the search algorithm.

The script works as follows:

1. It loads a pre-parsed list of examples, where each example includes its expected dictionary
   range and the associated English sentence.
2. The script processes each example in parallel, using multiprocessing to speed up execution time.
3. For each example, it calls the `get_potential_matches()` function to find potential dictionary
   entries and then uses `look_closer()` to refine the matches.
4. It checks if the correct dictionary range for the example exists in the results obtained 
   from the search algorithm. If the range is found, the example is considered a successful match.
5. The results for each example, including the example itself, the expected range, 
   the obtained results, the count of matches, and whether it's a successful match, are recorded.
6. The final output is saved to a pickle file, which will serve as input for 'N_report.py'. 
   This report generation script will further analyze the data and present it in a 
   human-readable format to demonstrate the accuracy of the search algorithm.

Note: my macbook air struggles to go through the 18395 entries in one go in order to create a 
validation. so i've broken down the task into 19 smaller pieces. i use run_validation.sh to start 
a new validation and validation_progress.pickle to keep track of the progress. we every new 
validation, you need to delete validation_progress.pickle.


Input:
- examples.pickle

Output:
- validation_data.pickle
- validation_progress.pickle

Runtime:
The runtime for the validation process, when executed on a single CPU core, 
is estimated to be around 30 hours. (10 hours on MacBook Air utilizing 8 cores 
and running the validation throught run_validation.sh)

Usage:
Please run this script from the command line (CMD)

Example:
python M_validate.py

Validation history:
- validation_data_29_06_2023_21_55
    is the first validation i ran, it contained all entries in phrases.json - nothing chopped off.
    after running it, i decided to remove the 318 most frequently occurring incorrect entries 
    from 'phrases.json' and ran another validation
- validation_data_03_07_2023_14_14
- validation_data_26_02_2024_5_42
    ran this validation after updating the algorithm and switching from using record 
    to combinations - no entries were removed.
- validation_data_28_02_2024_9_01
    made a minor change to regrex in algorithm changed \b to \W to include words that ends 
    with an apostrophe
- validation_data_01_03_2024_8_20
    reason:
    that previous change made some problems appear that weren't there before, so i needed to
    update the regex and span in look_closer() function. 
    results:
    slightly better than validation_data_26_02_2024_5_42. 
    only one percent increase in algorithm accuracy.
- validation_data_12_03_2024_02_09
    reason:
    i've added the python module A_splitrandom into the workflow and it addes 265 new entries to
    phrases.json. i've also changes how examples get parsed in K_getexamples - so more 
    examples/entries.
    results:
    accuracy is still at 91%
- validation_data_13_03_2024
    reason:
    i've decreased the distance factor calculated by max_words_between() in L_algorithm down to 2
    (3 was the original number) to see how that would affect the accuracy of the results
    results:
    acurracy went down to 88%, with no segnificant improvement in any aspect, so i'm reverting the 
    distance back to 3
"""

import datetime
import itertools
import os
import pickle
import sys
from multiprocessing import Pool

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from tqdm import tqdm

from englishidioms.L_algorithm import get_potential_matches, look_closer

# manually point nltk to my top level nltk_data folder that includes wordnet
# https://www.nltk.org/data.html
nltk_data_dir = os.path.join(os.path.dirname(__file__), "englishidioms", "nltk_data")
nltk.data.path.append(nltk_data_dir)


def process_example(example):
    """
    Process an example for validation.

    Given an example containing a known dictionary range and an English sentence,
    this function performs the following tasks:

    1. Executes the search algorithm by calling `get_potential_matches()` and `look_closer()`
       functions to identify potential dictionary entries and refined idiomatic expression matches.
    2. Compares the known dictionary range with the ranges obtained from the search results.
    3. Records the validation results, indicating whether the known range correctly matches
    the search results.

    Args:
        example (list): A list containing the known dictionary range and an English sentence example
        e.g. [[[0, 3], ['The plan didn’t work, but I’ll give you an A for effort for trying.']]

    Returns:
        results (list): A list of dictionaries, each containing information about the validation
        result for a specific example.
    """
    example_range = example[0]

    results = []

    for ex in example[1]:
        # run the example against the search algorithm
        # Tokenize the sentence into words
        words = nltk.word_tokenize(ex.lower())

        # Tag the words with their respective parts of speech
        pos_tags = nltk.pos_tag(words)

        # Lemmatize each word based on its POS tag
        sentence_lemma = [
            (
                WordNetLemmatizer().lemmatize(word, pos[0].lower())
                if pos[0].lower() in ["a", "n", "v"]
                else WordNetLemmatizer().lemmatize(word)
            )
            for word, pos in pos_tags
        ]

        potential_matches = get_potential_matches(ex.lower(), sentence_lemma)
        lc = look_closer(potential_matches, ex.lower(), sentence_lemma)

        matches = list(
            k for k, _ in itertools.groupby([item[0]["range"] for item in lc[:10]])
        )

        results.append(
            {
                "example": ex,
                "example_range": example_range,
                "results": matches,
                "results_count": len(matches),
                "match": example_range in matches,  # True or False
                "match_index": (
                    matches.index(example_range) + 1
                    if example_range in matches
                    else "NA"
                ),
            }
        )

    return results


if __name__ == "__main__":
    # Load up all the examples - a list of lists
    # [[[0, 3], ['The plan didn’t work, but I’ll give you an A for effort for trying.']]
    with open("files/examples.pickle", "rb") as file:
        examples = pickle.load(file)

    # macbook air struggles to go through the 18395 entries in one go
    # breaking the task into smaller parts
    num_parts = 18
    part_length = len(examples) // num_parts
    parts = [
        examples[i : i + part_length] for i in range(0, len(examples), part_length)
    ]

    # Generate a timestamp & file name
    date_time = datetime.datetime.now()
    file_name = f'validation_data_{date_time.strftime("%d_%m_%Y")}'
    # file_name = "validation_data_13_03_2024"

    if os.path.exists(f"files/{file_name}.pickle"):
        with open(f"files/{file_name}.pickle", "rb") as file:
            output = pickle.load(file)
    else:
        output = []

    if os.path.exists("files/validation_progress.pickle"):
        with open("files/validation_progress.pickle", "rb") as file:
            validation_progress = pickle.load(file)
    else:
        validation_progress = 0

    if validation_progress > len(parts) - 1:
        sys.exit(f"All {len(parts)} parts have been processed.")

    print(f"Part {validation_progress + 1} out of {len(parts)}")
    # Set the number of processes to the desired number of threads
    num_processes = 8

    with Pool(num_processes) as pool:
        # Map the processing function to each example in parallel
        results = list(
            tqdm(
                pool.imap(process_example, parts[validation_progress]),
                total=len(parts[validation_progress]),
            )
        )

        # Collect the results from all processes
        for res in results:
            output.extend(res)

    # Save the output to a pickle file for 'N_report.py'
    with open(f"files/{file_name}.pickle", "wb") as file:
        pickle.dump(output, file)
    # updated progress and save it to 'validation_progress.pickle'
    validation_progress += 1
    with open("files/validation_progress.pickle", "wb") as file:
        pickle.dump(validation_progress, file)

    print(f"Part {validation_progress} completed.")
