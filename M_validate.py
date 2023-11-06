""" Script for Validating the Search Algorithm

Description:
This script is designed to validate the functionality of the `get_potential_matches()` and `look_closer()` functions in 'L_algorithm.py' by testing them against a large dataset of examples.
The purpose is to verify if the results obtained from the search algorithm correctly match the expected dictionary range for each example.
This validation process is critical for ensuring the accuracy and reliability of the search algorithm.

The script works as follows:

1. It loads a pre-parsed list of examples, where each example includes its expected dictionary range and the associated English sentence.
2. The script processes each example in parallel, using multiprocessing to speed up the execution time.
3. For each example, it calls the `get_potential_matches()` function to find potential dictionary entries and then uses `look_closer()` to refine the matches.
4. It checks if the correct dictionary range for the example exists in the results obtained from the search algorithm. If the range is found, the example is considered a successful match.
5. The results for each example, including the example itself, the expected range, the obtained results, the count of matches, and whether it's a successful match, are recorded.
6. The final output is saved to a pickle file, which will serve as input for 'N_report.py'. This report generation script will further analyze the data and present it in a human-readable format to demonstrate the accuracy of the search algorithm.

Input:
- examples.pickle

Output:
- validation_data.pickle

Runtime:
The runtime for the validation process, when executed on a single CPU core, is estimated to be around 30 hours

Usage:
Please run this script from the command line (CMD)

Example:
python M_validate.py
"""


import pickle
import itertools
from L_algorithm import get_potential_matches, look_closer
from tqdm import tqdm
import datetime
from multiprocessing import Pool


def process_example(example):
    """
    Process an example for validation.

    Given an example containing a known dictionary range and an English sentence, this function performs the following tasks:

    1. Executes the search algorithm by calling `get_potential_matches()` and `look_closer()` functions to identify potential dictionary entries and refined idiomatic expression matches.
    2. Compares the known dictionary range with the ranges obtained from the search results.
    3. Records the validation results, indicating whether the known range correctly matches the search results.

    Args:
        example (list): A list containing the known dictionary range and an English sentence example.

    Returns:
        results (list): A list of dictionaries, each containing information about the validation result for a specific example.
    """
    example_range = example[0]

    results = []

    for ex in example[1]:
        # run the example against the search algorithm
        potential_matches = get_potential_matches(ex)
        lc = look_closer(potential_matches, ex)
        matches = list(
            k for k, _ in itertools.groupby([item[0]["range"] for item in lc[:10]])
        )

        if example_range in matches:
            results.append(
                {
                    "example": ex,
                    "example_range": example_range,
                    "results": matches,
                    "results_count": len(matches),
                    "match": True,
                    "match_index": matches.index(example_range) + 1,
                }
            )
        else:
            results.append(
                {
                    "example": ex,
                    "example_range": example_range,
                    "results": matches,
                    "results_count": len(matches),
                    "match": False,
                }
            )

    return results


if __name__ == "__main__":
    # Load up all the examples - a list of lists
    # [[[0, 3], ['The plan didn’t work, but I’ll give you an A for effort for trying.']], [[6, 11], ['This is our cafeteria. Abandon hope, all ye who enter here!']], ... ]
    with open("files/examples.pickle", "rb") as file:
        examples = pickle.load(file)

    output = []

    # Set the number of processes to the desired number of threads (3 in this case)
    num_processes = 3

    with Pool(num_processes) as pool:
        # Map the processing function to each example in parallel
        results = list(tqdm(pool.imap(process_example, examples), total=len(examples)))

        # Collect the results from all processes
        for res in results:
            output.extend(res)

    # Generate a timestamp
    date_time = datetime.datetime.now()

    # Save the output to a pickle file for 'N_report.py'
    with open(
        f'validation_data_{date_time.strftime("%d_%m_%Y_%H_%M")}.pickle', "wb"
    ) as file:
        pickle.dump(output, file)
