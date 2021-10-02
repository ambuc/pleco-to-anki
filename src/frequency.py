import csv
from typing import Dict, Text


class Frequencies():
    def __init__(self, path_to_frequencies_csv: Text):
        self._frequencies_dict = {}
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
                self._frequencies_dict[char] = float(percentage)

    def get_frequency(self, character) -> float:
        s = [self._frequencies_dict.get(c, 99999999) for c in character]
        return sum(s) / len(s)
