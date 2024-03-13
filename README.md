I am delighted to announce the release of my first Python package, `englishidioms`. This package is a powerful tool for identifying English idioms, phrases, and phrasal verbs within sentences, with a database of 22,209 unique expressions.


**Background:** 
As part of a personal Natural Language Processing (NLP) project, I found the need for a Python package capable of recognizing idiomatic expressions within English sentences. To my surprise, I couldn't find a suitable solution, so I decided to build one from scratch.


**Installation:** 
You can easily install the package using pip:
`pip install englishidioms`

**How to use it:**
```
>>> from englishidioms import find_idioms
>>> sentence = "The plan didn't work, but I'll give you an a for effort for trying."
>>> results = find_idioms(sentence, limit=1)
>>> print(results)
[{'phrase': '*an A for effort', 'definition': 'acknowledgement for having tried to do something, even if it was not successful. (*Typically: get ~; give someone ~.) _ The plan didn’t work, but I’ll give you an A for effort for trying.'}]
```

**Arguments**

- `sentence` (str) - The English sentence you want to analyze (required).
- `limit` (int) - Maximum number of results, ordered by matching points (default: 10).
- `html` (bool) - Return phrase and definition in HTML markup to preserve original formatting from the dictionary (default: False).
- `span` (bool) - Return matching span in the sentence (default: False).
- `entry_range` bool) - Return dictionary start/end line for debugging (default: False).
- `entry_id` (bool) - Return dictionary entry ID in phrases.json for debugging (default: False).

**How it works (simplified):**

This package was developed by parsing all dictionary entries in the "McGraw-Hill Dictionary of American Idioms and Phrasal Verbs." By using Python libraries like python-docx and leveraging predefined formatting, I extracted key points from each entry. These key points include:

Constants: Fixed classes of words that form the core of the idiomatic expression.
Variables: Variable classes of words that can be broadly matched.
Optional Constants: Additional optional words or phrases within a single idiomatic expression.
Verbs: Verbs that usually precede the idiomatic phrase.


For example, consider the dictionary entry:

> \*a **(dead) ringer (for** someone **)** Fig. very closely similar  in
> appearance to someone else. (*Typically: be ~; look like ~.) _ You are
> sure a dead ringer for my brother. _ Isn’t he a ringer for Chuck?

For this entry, we identify:
- Constants: "ringer" and "for"
- Variables: "someone"
- Optional Constants: "dead"
- Verbs: "be" and "look like"

With every call to the 'find_idioms' method, a search algorithm examines these key points in 22,209 dictionary entries and matches them against the given sentence, considering grammatical variations and word order. It then returns a list of matched entries.

**Performance:**

I tested this package on 40,442 sentences from the book, and it detected the correct matching dictionary entry in 91% of cases. Additionally, the average execution time for processing a sentence is approximately 3 seconds. 

**Project Details**

This project is divided into several key steps:

**1. Getting the Data:**

We start by obtaining the source material from the "McGraw-Hill Dictionary of American Idioms and Phrasal Verbs." You can access a copy of this resource in PDF format [here](https://www.sausd.us/cms/lib/CA01000471/Centricity/domain/1835/dictionaries/Dictionary_of_American_Idioms_.pdf). 

Next, we convert the PDF into a more usable format, a docx document called 'clean-output.docx.' We reformat it from a two-column layout to a single-column text. Please note that the technical details of this conversion process are not discussed in this documentation.

**2. Preparing the Data:**

We go through a series of twelve steps to process and refine the data from 'clean-output.docx' and save it in 'phrases.json.' Each step is managed by a specific Python module:

- A_breakitup.py: Break the text in clean-output.docx into individual dictionary entries
- A_splitrandom.py: **[New Module]** parse and split dictionary entries with random and unpatterned variations.
- B_breakitup.py: Separate single phrase entries from multiple phrase entries
- C_readit.py: Parse Dictionary Entries with Multiple Idiomatic Expressions
- D_readit.py: Parse Dictionary Entries with single Idiomatic Expression
- E_tidyup.py: Parse Optional Constants and Correct Special Entries in phrases.json
- F_tidyup.py: Clean up the 'alt' and 'runs' Lists in phrases.json
- FF_manualoverride.py: Manually override entries in phrases.json that do not follow expected patterns
- G_asterisk.py: Parse Verbs Associated with the Asterisk in Dictionary Entries
- H_hyphenated_words.py: Create Duplicates for Entries with Hyphenated Words
- I_getpatterns.py: Generate Search Patterns for Idiomatic Expressions
- J_getwordforms.py: Generate Word Forms for Dictionary Entries
- K_getexamples.py: Extract Examples from 'clean-output.docx'

It's important to run these modules in the specified order to create the final version of 'phrases.json,' which is the comprehensive database for data from 'clean-output.docx.' On Windows CMD, you can run them sequentially using this command:

    python A_breakitup.py && python A_splitrandom.py && python B_breakitup.py && python C_readit.py && python D_readit.py && python E_tidyup.py && python F_tidyup.py && python FF_manualoverride.py && python G_asterisk.py && python H_hyphenated_words.py && python I_getpatterns.py && python J_getwordforms.py && python K_getexamples.py

**3. Core Functionality:**

The heart of the project is the 'L_algorithm.py' module. It utilizes 'phrases.json' to match idiomatic expressions with English sentences. This module is crucial for the package, enabling the identification of idioms, phrases, and phrasal verbs in sentences.

The heart of the project is the 'L_algorithm.py' module, which is located in the 'englishidioms' directory. It utilizes 'phrases.json' to match idiomatic expressions with English sentences. Keeping 'L_algorithm.py' and 'phrases.json' in the 'englishidioms' directory serves a dual purpose:

- Reduced Package Size: By isolating these core components, we make the package smaller in terms of disk space. This means that users only need to install the essential components, making the package more lightweight and efficient.

- Minimized Dependencies: The 'L_algorithm.py' and 'phrases.json' combination requires fewer external dependencies compared to the entire package. This simplifies the installation process for end-users, reducing the need to install additional libraries and requirements that may not be necessary for their specific usage.

The 'englishidioms' directory also includes three necessary NLTK resources needed in order to run 'L_algorithm.py'

1. punkt: This resource is a tokenizer model. It's used for tokenization, which is the process of splitting text into individual words or punctuation marks. The nltk.word_tokenize() function, relies on this tokenizer model to split sentences into words.
2. averaged_perceptron_tagger: This resource is a part-of-speech (POS) tagger model. It's used to assign POS tags to each word in a sentence. The nltk.pos_tag() function, utilizes this tagger model to tag words with their respective POS.
3. wordnet: WordNet is a lexical database of English. It's used for the WordNetLemmatizer() class from NLTK's WordNet module to lemmatize words. The lemmatization process involves reducing words to their base or dictionary form (known as lemma).

By adopting this streamlined approach, we ensure that users can quickly and easily access the core functionality of the package without any unnecessary overhead.

**4. Checking and Testing:**

To ensure data quality and the effectiveness of the search algorithm in 'L_algorithm.py,' we use three additional modules:

- M_validate.py: Script for Validating the Search Algorithm
- N_report.py: Generate Reports for Validation Data
- O_chopoff.py: Optimization Experiment Script

Please note that for end-users looking to use the package, only 'L_algorithm.py' and 'phrases.json' are needed. The other modules are primarily for data processing and validation during development.

**How to Contribute:**

The entire project is open source and available on GitHub. Feel free to explore the code, make improvements, and contribute to its development.

# Disclaimer and Usage Note

**Disclaimer:** This Python package is designed to provide users with access to a collection of idioms and phrasal verbs as they appear in the "McGraw-Hill Dictionary of American Idioms and Phrasal Verbs." Please note that this package is not endorsed or authorized by The McGraw-Hill Companies, Inc., the copyright holder of the dictionary.

**Copyright Notice:** The "McGraw-Hill Dictionary of American Idioms and Phrasal Verbs" is copyrighted material, and its use is subject to the copyright terms established by The McGraw-Hill Companies, Inc. This package relies on content derived from a personal copy of the book.

**Intended Use:** This Python package is intended for educational and research purposes only, and for personal, non-commercial use. It is not intended for commercial applications.

**User Responsibility:** By using this Python package, you acknowledge that you must comply with copyright laws and the terms of use outlined in the original work. You are permitted to use this package for personal, non-commercial purposes only. Any commercial application or distribution of this package's output may require the prior written consent of the publisher, The McGraw-Hill Companies, Inc. It is strongly encouraged that users who intend to use this package on a regular basis consider purchasing their own personal copy of the "McGraw-Hill Dictionary of American Idioms and Phrasal Verbs" to support the authors and adhere to copyright laws.

**Support the Author:** If you intend to use the content of this package for commercial purposes, I strongly recommend that you obtain the necessary permissions and licenses from The McGraw-Hill Companies, Inc. To access the full range of idioms and phrasal verbs, consider purchasing your own personal copy of the "McGraw-Hill Dictionary of American Idioms and Phrasal Verbs."

**Liability:** The creators and maintainers of this Python package shall not be held responsible for any infringement of copyright or misuse of the package. Users are responsible for adhering to all legal and copyright requirements when using this package.

I encourage ethical and lawful usage of this package, respecting the rights of copyright holders and authors. Please use it responsibly.
