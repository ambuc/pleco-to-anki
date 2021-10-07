import networkx as nx
import more_itertools
from absl import logging
from enum import IntEnum, auto

from src import decomposer as decomposer_lib
from src import hsk_utils as hsk_utils_lib


class Deck(IntEnum):
    UNKNOWN = auto()  # 1
    VocabV1 = auto()  # 2
    VocabV2 = auto()  # 3
    ListeningV1 = auto()  # 4
    ListeningV2 = auto()  # 5
    RadicalsV2 = auto()  # 6
    HSK_1_V1 = auto()  # 7
    HSK_2_V1 = auto()  # 8
    HSK_3_V1 = auto()  # 9
    HSK_4_V1 = auto()  # 10
    HSK_5_V1 = auto()  # 11
    HSK_6_V1 = auto()  # 12
    HSK_1_MINUS_V1 = auto()  # 13
    HSK_2_MINUS_V1 = auto()  # 14
    HSK_3_MINUS_V1 = auto()  # 15
    HSK_4_MINUS_V1 = auto()  # 16
    HSK_5_MINUS_V1 = auto()  # 17
    HSK_6_MINUS_V1 = auto()  # 18
    HSK_1_PLUS_V1 = auto()  # 19
    HSK_2_PLUS_V1 = auto()  # 20
    HSK_3_PLUS_V1 = auto()  # 21
    HSK_4_PLUS_V1 = auto()  # 22
    HSK_5_PLUS_V1 = auto()  # 23
    HSK_6_PLUS_V1 = auto()  # 24
    OTHER_V1 = auto()  # 25


class Categorizer():
    def __init__(self,
                 decomposer: decomposer_lib.Decomposer,
                 hsk_reader: hsk_utils_lib.HskReader):
        self._decomposer = decomposer
        self._hsk_reader = hsk_reader

    def sort_into_deck(self, headword) -> Deck:
        if len(headword) > 5:
            logging.info(f"Skipping {headword}, too long.")
            return Deck.OTHER_V1
        hsk_level = self._hsk_reader.GetHskLevel(headword)
        if hsk_level is not None:
            return {
                1: Deck.HSK_1_V1,
                2: Deck.HSK_2_V1,
                3: Deck.HSK_3_V1,
                4: Deck.HSK_4_V1,
                5: Deck.HSK_5_V1,
                6: Deck.HSK_6_V1,
            }.get(hsk_level, Deck.OTHER_V1)

        if len(headword) == 1:
            # If our headword is a single character,
            for deck, checkset in [
                # For every HSK tier,
                (Deck.HSK_1_MINUS_V1, self._hsk_reader.GetHskAndBelow(1)),
                (Deck.HSK_2_MINUS_V1, self._hsk_reader.GetHskAndBelow(2)),
                (Deck.HSK_3_MINUS_V1, self._hsk_reader.GetHskAndBelow(3)),
                (Deck.HSK_4_MINUS_V1, self._hsk_reader.GetHskAndBelow(4)),
                (Deck.HSK_5_MINUS_V1, self._hsk_reader.GetHskAndBelow(5)),
                (Deck.HSK_6_MINUS_V1, self._hsk_reader.GetHskAndBelow(6)),
            ]:
                if headword in set(c for w in checkset for c in w):
                    return deck

                try:
                    # If the headword is a part of any whole in our checkset up
                    # to and including HSK N
                    next(
                        nx.algorithms.simple_paths.all_simple_paths(
                            self._decomposer._graph, headword, checkset | set(
                                c for w in checkset for c in w)))
                    return deck
                except nx.NodeNotFound as e:
                    continue
                except StopIteration:
                    continue

        min_deck = Deck.OTHER_V1
        for p_seq in list(more_itertools.partitions(headword))[1:]:
            decks = list(filter(lambda d: d != Deck.OTHER_V1, [
                         self.sort_into_deck(''.join(p)) for p in p_seq]))
            if len(decks) == 0:
                continue
            min_deck = min(min_deck, max(decks))

        return {
            Deck.HSK_1_V1: Deck.HSK_1_PLUS_V1,
            Deck.HSK_2_V1: Deck.HSK_2_PLUS_V1,
            Deck.HSK_3_V1: Deck.HSK_3_PLUS_V1,
            Deck.HSK_4_V1: Deck.HSK_4_PLUS_V1,
            Deck.HSK_5_V1: Deck.HSK_5_PLUS_V1,
            Deck.HSK_6_V1: Deck.HSK_6_PLUS_V1,
            Deck.HSK_1_PLUS_V1: Deck.HSK_1_PLUS_V1,
            Deck.HSK_2_PLUS_V1: Deck.HSK_2_PLUS_V1,
            Deck.HSK_3_PLUS_V1: Deck.HSK_3_PLUS_V1,
            Deck.HSK_4_PLUS_V1: Deck.HSK_4_PLUS_V1,
            Deck.HSK_5_PLUS_V1: Deck.HSK_5_PLUS_V1,
            Deck.HSK_6_PLUS_V1: Deck.HSK_6_PLUS_V1,
            Deck.HSK_1_MINUS_V1: Deck.HSK_1_PLUS_V1,
            Deck.HSK_2_MINUS_V1: Deck.HSK_2_PLUS_V1,
            Deck.HSK_3_MINUS_V1: Deck.HSK_3_PLUS_V1,
            Deck.HSK_4_MINUS_V1: Deck.HSK_4_PLUS_V1,
            Deck.HSK_5_MINUS_V1: Deck.HSK_5_PLUS_V1,
            Deck.HSK_6_MINUS_V1: Deck.HSK_6_PLUS_V1,
        }.get(min_deck, Deck.OTHER_V1)
