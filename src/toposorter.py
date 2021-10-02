import networkx as nx
from typing import List, Text, Callable

from src import card as card_lib
from src import decomposer as decomposer_lib


class Toposorter():
    def __init__(self, decomposer: decomposer_lib.Decomposer,
                 cards: List[card_lib.Card]):
        self._decomposer = decomposer
        self._G = nx.DiGraph()  # G.add_edge(part, whole)

        for card_obj in cards:
            self._add(card_obj._headword)

        # detect cycles
        try:
            nx.algorithms.cycles.find_cycle(self._G)
        except nx.NetworkXNoCycle:
            pass

    def _add(self, headword):
        if len(headword) > 1:
            # many characters
            self._G.add_node(headword)
            for w in headword:
                self._G.add_node(w)
                self._G.add_edge(w, headword)
        else:
            # one character
            self._G.add_node(headword)
            try:
                decomposition = self._decomposer.decompose(
                    headword).decomposition

                for w in decomposition:
                    if w not in decomposer_lib._VERBS and w != headword:
                        self._G.add_edge(w, headword)
                        self._add(w)
            except BaseException:
                pass

    def get_sorted(self, key: Callable[[Text], float] = None) -> List[Text]:
        return list(
            nx.algorithms.dag.lexicographical_topological_sort(
                self._G, key))
