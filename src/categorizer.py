import networkx as nx
import more_itertools
from absl import logging
from enum import IntEnum, auto

from src import decomposer as decomposer_lib
from src import hsk_utils as hsk_utils_lib


class Deck(IntEnum):
    UNKNOWN = auto()
    VocabV1 = auto()
    VocabV2 = auto()
    ListeningV1 = auto()
    ListeningV2 = auto()
    RadicalsV2 = auto()
    HSK_1_V1 = auto()
    HSK_2_V1 = auto()
    HSK_3_V1 = auto()
    HSK_4_V1 = auto()
    HSK_5_V1 = auto()
    HSK_6_V1 = auto()
    HSK_1_MINUS_V1 = auto()
    HSK_2_MINUS_V1 = auto()
    HSK_3_MINUS_V1 = auto()
    HSK_4_MINUS_V1 = auto()
    HSK_5_MINUS_V1 = auto()
    HSK_6_MINUS_V1 = auto()
    HSK_1_PLUS_V1 = auto()
    HSK_2_PLUS_V1 = auto()
    HSK_3_PLUS_V1 = auto()
    HSK_4_PLUS_V1 = auto()
    HSK_5_PLUS_V1 = auto()
    HSK_6_PLUS_V1 = auto()
    OTHER_V1 = auto()


class Categorizer():
    def __init__(self,
                 decomposer: decomposer_lib.Decomposer,
                 hsk_reader: hsk_utils_lib.HskReader):
        self._decomposer = decomposer
        self._hsk_reader = hsk_reader

    def sort_into_deck(self, headword) -> Deck:
        hsk_level = self._hsk_reader.GetHskLevel(headword)
        if hsk_level is not None:
            deck = [Deck.HSK_1_V1, Deck.HSK_2_V1,
                    Deck.HSK_3_V1, Deck.HSK_4_V1,
                    Deck.HSK_5_V1, Deck.HSK_6_V1,
                    ][hsk_level - 1]
            return deck

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
                    # next(nx.algorithms.simple_paths.all_simple_paths( self._decomposer._graph, headword, checkset))
                    return deck
                except nx.NodeNotFound as e:
                    # logging.error(str(e))
                    continue
                except StopIteration:
                    continue

        for p_seq in list(more_itertools.partitions(headword))[1:]:
            decks = list(filter(lambda d: d != Deck.OTHER_V1, [
                         self.sort_into_deck(''.join(p)) for p in p_seq]))
            if len(decks) == 0:
                return Deck.OTHER_V1
            deck = max(decks)
            if deck == Deck.HSK_1_V1:
                return Deck.HSK_1_PLUS_V1
            elif deck == Deck.HSK_2_V1:
                return Deck.HSK_2_PLUS_V1
            elif deck == Deck.HSK_3_V1:
                return Deck.HSK_3_PLUS_V1
            elif deck == Deck.HSK_4_V1:
                return Deck.HSK_4_PLUS_V1
            elif deck == Deck.HSK_5_V1:
                return Deck.HSK_5_PLUS_V1
            elif deck == Deck.HSK_6_V1:
                return Deck.HSK_6_PLUS_V1

        return Deck.OTHER_V1
