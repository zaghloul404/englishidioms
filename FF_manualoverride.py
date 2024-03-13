import json

from Z_module import CompactJSONEncoder


def manual_override(dictionary_entry):
    """Manually override entries in phrases.json that do not follow expected patterns
    note: if manual_override() is going to retun more than one entry per input,
    you should include both dictionary_entry["range"] and dictionary_entry["phrase"] in the if
    statement to avoid memory leackage (infinite loop)
    """
    if dictionary_entry["range"] == [41035, 41037]:

        new_entries = [
            {
                "range": dictionary_entry["range"],
                "phrase": "It’s a jungle out there.",
                "phrase_html": "<p><strong>It’s a jungle out there.</strong></p>",
                "definition": "The real world is severe.; It’s hard to get by in everyday life. _ A: Gee, people are so rude in this town. B: Yup, it’s a jungle out there.",
                "definition_html": "<p>The real world is severe.; It’s hard to get by in everyday life. <br>_ <em>A: Gee, people are so rude in this town. B: Yup, it’s a jungle out there.</em></p>",
                "alt": ["constant"],
                "runs": ["it’s a jungle out there"],
                "multiple": dictionary_entry["multiple"],
                "duplicate": dictionary_entry["duplicate"],
            }
        ]

        return new_entries
    if (
        dictionary_entry["range"] == [26246, 26255]
        and dictionary_entry["phrase"] == "and for want of a horse the man was lost."
    ):
        new_entries = [
            {
                "range": dictionary_entry["range"],
                "phrase": "for want of a horse the man was lost.",
                "phrase_html": "<p><strong>for want of a horse the man was lost.</strong></p>",
                "definition": dictionary_entry["definition"],
                "definition_html": dictionary_entry["definition_html"],
                "alt": dictionary_entry["alt"],
                "runs": ["for want of a", "horse the man was lost."],
                "multiple": dictionary_entry["multiple"],
                "duplicate": dictionary_entry["duplicate"],
            }
        ]

        return new_entries

    if (
        dictionary_entry["range"] == [82671, 82681]
        and dictionary_entry["phrase"] == "*a go at someone *a stab at someone"
    ):
        new_entries = [
            {
                "range": dictionary_entry["range"],
                "phrase": "*a go at someone",
                "phrase_html": "<p><strong>*</strong>a <strong>go at </strong>someone</p>",
                "definition": dictionary_entry["definition"],
                "definition_html": dictionary_entry["definition_html"],
                "alt": ["asterisk", "article", "constant", "variable"],
                "runs": ["*", "a", "go at", "someone"],
                "multiple": dictionary_entry["multiple"],
                "duplicate": dictionary_entry["duplicate"],
            },
            {
                "range": dictionary_entry["range"],
                "phrase": "*a stab at someone",
                "phrase_html": "<p><strong>*</strong>a <strong>stab at </strong>someone </p>",
                "definition": dictionary_entry["definition"],
                "definition_html": dictionary_entry["definition_html"],
                "alt": ["asterisk", "article", "constant", "variable"],
                "runs": ["*", "a", "stab at", "someone"],
                "multiple": dictionary_entry["multiple"],
                "duplicate": dictionary_entry["duplicate"],
            },
        ]

        return new_entries

    if (
        dictionary_entry["range"] == [90790, 90794]
        and dictionary_entry["phrase"] == "*out of someone’s way; *out of the road"
    ):

        new_entries = [
            {
                "range": dictionary_entry["range"],
                "phrase": "*out of someone’s way",
                "phrase_html": "<p><strong>*out of </strong>someone’s <strong>way</p>",
                "definition": dictionary_entry["definition"],
                "definition_html": dictionary_entry["definition_html"],
                "alt": ["constant", "variable", "constant"],
                "runs": ["*out of", "someone’s", "way"],
                "multiple": dictionary_entry["multiple"],
                "duplicate": dictionary_entry["duplicate"],
            },
            {
                "range": dictionary_entry["range"],
                "phrase": "*out of the road",
                "phrase_html": "<p>*out</strong> <strong>of the road</strong></p>",
                "definition": dictionary_entry["definition"],
                "definition_html": dictionary_entry["definition_html"],
                "alt": ["constant", "constant"],
                "runs": ["*out", "of the road"],
                "multiple": dictionary_entry["multiple"],
                "duplicate": dictionary_entry["duplicate"],
            },
        ]
        return new_entries

    return []


# load the json file
with open("englishidioms/phrases.json", encoding="UTF-8") as f:
    data = json.load(f)


for index, entry in enumerate(data["dictionary"]):

    new_dicts = manual_override(entry)

    if new_dicts:

        del data["dictionary"][index]
        # Insert one or more dictionaries at the same index
        index_adjustment = (
            0  # To keep track of how much the index is adjusted after insertion
        )
        for new_dict in new_dicts:
            data["dictionary"].insert(index + index_adjustment, new_dict)
            index_adjustment += 1  # Increment index adjustment


# overwrite the file
with open("englishidioms/phrases.json", "w", encoding="UTF-8") as f:
    json.dump(data, f, indent=2, cls=CompactJSONEncoder, ensure_ascii=False)
