import csv
from typing import Dict, Text


def make_frequencies_dict(path_to_frequencies_csv: Text) -> Dict[Text, float]:
    """Returns dict from char to float; lower is more common."""
    frequencies_dict = {}
    with open(path_to_frequencies_csv) as f:
        reader = csv.reader(f)
        # idx, char, count, percentage
        # ['1', '的', '123456', '1.23456']
        for row in reader:
            if len(row) != 4:
                raise ValueError(
                    f"Encountered a row in path_to_frequencies_csv "
                    "{path_to_frequencies_csv} which should have had "
                    "four columns, but did not: '{row}'.")
            _idx, char, _count, percentage = row
            frequencies_dict[char] = float(percentage)
    return frequencies_dict


def get_frequency(dict, character) -> float:
    s = [ dict.get(c, 99999999) for c in character ]
    return sum(s) / len(s)
