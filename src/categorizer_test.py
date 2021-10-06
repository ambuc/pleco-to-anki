import networkx as nx
from decomposer import Decomposer
from src import categorizer as categorizer_lib
from src.categorizer import Deck

from unittest.mock import MagicMock, call
from absl.testing import absltest


class CategorizerTest(absltest.TestCase):

    def test_hsk_level_verbatim(self):
        decomposer = MagicMock()
        hsk_reader = MagicMock()
        for lvl, deck in [
            (1, Deck.HSK_1_V1),
            (2, Deck.HSK_2_V1),
            (3, Deck.HSK_3_V1),
            (4, Deck.HSK_4_V1),
            (5, Deck.HSK_5_V1),
            (6, Deck.HSK_6_V1),
        ]:
            hsk_reader.GetHskLevel.side_effect = lambda hw: lvl if hw == "foo" else None
            c = categorizer_lib.Categorizer(decomposer, hsk_reader)
            self.assertEqual(c.sort_into_deck("foo"), deck)
            decomposer.assert_not_called()

    def test_hsk_level_minus(self):
        decomposer = MagicMock()
        decomposer = MagicMock()
        decomposer._graph = nx.DiGraph()  # add_edge(part, whole)
        # c + l = d
        # v + v = w
        decomposer._graph.add_edges_from([("c", "d"), ("l", "d"), ("v", "w")])

        hsk_reader = MagicMock()
        hsk_reader.GetHskLevel.side_effect = lambda hw: {
            "d": 1, "ww": 1}.get(hw, None)
        hsk_reader.GetHskAndBelow.side_effect = lambda lvl: {
            1: set(["d", "ww"])}.get(lvl, set())

        c = categorizer_lib.Categorizer(decomposer, hsk_reader)
        self.assertEqual(c.sort_into_deck("ww"), Deck.HSK_1_V1)
        self.assertEqual(c.sort_into_deck("d"), Deck.HSK_1_V1)
        self.assertEqual(c.sort_into_deck("c"), Deck.HSK_1_MINUS_V1)
        self.assertEqual(c.sort_into_deck("l"), Deck.HSK_1_MINUS_V1)
        # parts of things in hsk1 and parts of them are all hsk1-
        self.assertEqual(c.sort_into_deck("w"), Deck.HSK_1_MINUS_V1)
        self.assertEqual(c.sort_into_deck("v"), Deck.HSK_1_MINUS_V1)

        self.assertEqual(c.sort_into_deck("x"), Deck.OTHER_V1)

    def test_hsk_level_missing(self):
        decomposer = MagicMock()
        hsk_reader = MagicMock()
        hsk_reader.GetHskLevel.return_value = None
        c = categorizer_lib.Categorizer(decomposer, hsk_reader)
        self.assertEqual(c.sort_into_deck("foo"),
                         Deck.OTHER_V1)
        decomposer.assert_not_called()

    def test_hsk_each_part_also_absent(self):
        decomposer = MagicMock()
        hsk_reader = MagicMock()
        hsk_reader.GetHskLevel.return_value = None
        c = categorizer_lib.Categorizer(decomposer, hsk_reader)
        self.assertEqual(c.sort_into_deck(
            "ab"), Deck.OTHER_V1)
        decomposer.assert_not_called()

    def test_hsk_one_part_absent(self):
        decomposer = MagicMock()
        hsk_reader = MagicMock()
        for lvl, deck in [
            (1, Deck.HSK_1_PLUS_V1),
            (2, Deck.HSK_2_PLUS_V1),
            (3, Deck.HSK_3_PLUS_V1),
            (4, Deck.HSK_4_PLUS_V1),
            (5, Deck.HSK_5_PLUS_V1),
            (6, Deck.HSK_6_PLUS_V1),
        ]:
            hsk_reader.GetHskLevel.side_effect = lambda hw: lvl if hw == "a" else None
            c = categorizer_lib.Categorizer(decomposer, hsk_reader)
            self.assertEqual(c.sort_into_deck(
                "ab"), deck)
            decomposer.assert_not_called()

    def test_hsk_two_parts_present_equal(self):
        decomposer = MagicMock()
        hsk_reader = MagicMock()
        for lvl, deck in [
            (1, Deck.HSK_1_V1),
            (2, Deck.HSK_2_V1),
            (3, Deck.HSK_3_V1),
            (4, Deck.HSK_4_V1),
            (5, Deck.HSK_5_V1),
            (6, Deck.HSK_6_V1),
        ]:
            hsk_reader.GetHskLevel.return_value = lvl
            c = categorizer_lib.Categorizer(decomposer, hsk_reader)
            self.assertEqual(c.sort_into_deck("ab"), deck)
            decomposer.assert_not_called()

    def test_hsk_two_parts_present_unequal(self):
        decomposer = MagicMock()
        hsk_reader = MagicMock()
        for lvl1, lvl2, deck in [
            (2, 1, Deck.HSK_2_PLUS_V1),
            (3, 1, Deck.HSK_3_PLUS_V1),
            (4, 1, Deck.HSK_4_PLUS_V1),
            (5, 1, Deck.HSK_5_PLUS_V1),
            (6, 1, Deck.HSK_6_PLUS_V1),
        ]:
            hsk_reader.GetHskLevel.side_effect = lambda hw: {
                "a": lvl1, "b": lvl2}.get(hw, None)
            c = categorizer_lib.Categorizer(decomposer, hsk_reader)
            self.assertEqual(c.sort_into_deck("ab"), deck)
            decomposer.assert_not_called()

    def test_hsk_one_minus(self):
        hsk_reader = MagicMock()
        hsk_reader.GetHskAndBelow.side_effect = lambda lvl: {
            1: set("ad")}.get(lvl, set())
        hsk_reader.GetHskLevel.side_effect = lambda hw: {"ad": 1}.get(hw, None)
        # in this world, c + l = d (get it?)
        decomposer = MagicMock()
        decomposer._graph = nx.DiGraph()  # add_edge(part, whole)
        decomposer._graph.add_edges_from([("c", "d"), ("l", "d")])

        c = categorizer_lib.Categorizer(decomposer, hsk_reader)

        self.assertEqual(c.sort_into_deck("ad"), Deck.HSK_1_V1)
        # substrings
        self.assertEqual(c.sort_into_deck("a"), Deck.HSK_1_MINUS_V1)
        self.assertEqual(c.sort_into_deck("d"), Deck.HSK_1_MINUS_V1)
        # parts of 'd'
        self.assertEqual(c.sort_into_deck("c"), Deck.HSK_1_MINUS_V1)
        self.assertEqual(c.sort_into_deck("l"), Deck.HSK_1_MINUS_V1)
        # absent
        self.assertEqual(c.sort_into_deck("cl"), Deck.OTHER_V1)
        self.assertEqual(c.sort_into_deck("x"), Deck.OTHER_V1)

    def test_hsk_minus_regression(self):
        # imagine a world where 'ab' is hsk1, 'a' and 'b' are hsk3 and hsk4, but
        # 'c' is hsk2. we want 'abc' to be hsk2+, obviously. but is it obvious
        # to a computer?
        hsk_reader = MagicMock()
        hsk_reader.GetHskLevel.side_effect = lambda hw: {
            "ab": 1, "a": 3, "b": 4, "c": 2}.get(hw, None)
        decomposer = MagicMock()

        c = categorizer_lib.Categorizer(decomposer, hsk_reader)

        self.assertEqual(c.sort_into_deck("ab"), Deck.HSK_1_V1)
        self.assertEqual(c.sort_into_deck("a"), Deck.HSK_3_V1)
        self.assertEqual(c.sort_into_deck("b"), Deck.HSK_4_V1)
        self.assertEqual(c.sort_into_deck("c"), Deck.HSK_2_V1)
        self.assertEqual(c.sort_into_deck("abc"), Deck.HSK_2_PLUS_V1)

    def test_verbatim_first(self):
        # c + l = d, d is hsk1, c is hsk4, l is None
        hsk_reader = MagicMock()
        hsk_reader.GetHskLevel.side_effect = lambda hw: {
            "d": 1, "c": 4}.get(hw, None)
        hsk_reader.GetHskAndBelow.side_effect = lambda lvl: {
            1: set("d"), 4: set(['c', 'd']), }.get(lvl, set())
        decomposer = MagicMock()
        decomposer._graph = nx.DiGraph()  # add_edge(part, whole)
        decomposer._graph.add_edges_from([("c", "d"), ("l", "d")])

        c = categorizer_lib.Categorizer(decomposer, hsk_reader)

        self.assertEqual(c.sort_into_deck("d"), Deck.HSK_1_V1)
        self.assertEqual(c.sort_into_deck("c"), Deck.HSK_4_V1)
        self.assertEqual(c.sort_into_deck("l"), Deck.HSK_1_MINUS_V1)


if __name__ == "__main__":
    absltest.main()
