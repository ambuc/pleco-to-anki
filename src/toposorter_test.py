from src import toposorter as toposorter_lib

from unittest.mock import MagicMock, call

from typing import cast
from absl.testing import absltest
import networkx as nx
from absl import logging


class ToposorterTest(absltest.TestCase):

    def test_empty(self):
        decomposer = MagicMock()

        ts = toposorter_lib.Toposorter(decomposer, [])
        self.assertEqual(ts.get_sorted(), [])

        decomposer.decompose.assert_not_called()

    def test_one_card_no_decompositions(self):
        decomposer = MagicMock()
        decomposer.decompose.return_value({"我", ValueError("")})

        ts = toposorter_lib.Toposorter(decomposer, [MagicMock(_headword="我")])
        self.assertEqual(ts.get_sorted(), ["我"])

        decomposer.decompose.assert_called_once_with("我")

    def test_one_card_one_decomposition_components_absent(self):
        # but the contents of that decomposition are _not_ in the original
        # cardslist, so they don't appear in get_sorted.
        decomposer = MagicMock()
        decomposer.decompose.return_value(
            {
                "你", MagicMock(decomposition="⿰亻尔"),
            })

        cardslist = [MagicMock(_headword="你")]
        ts = toposorter_lib.Toposorter(decomposer, cardslist)
        self.assertEqual(ts.get_sorted(), ["你"])

        decomposer.decompose.assert_called_once_with("你")

    def test_one_card_one_decomposition_components_present(self):
        decomposer = MagicMock()

        def _sef(*args):
            if args[0] == "你":
                return MagicMock(decomposition="⿰亻尔")
            return ValueError("")
        decomposer.decompose.side_effect = _sef

        cardslist = [
            MagicMock(_headword="你"),
            MagicMock(_headword="亻"),
            MagicMock(_headword="尔"),
        ]
        ts = toposorter_lib.Toposorter(decomposer, cardslist)
        self.assertEqual(ts.get_sorted(), ["亻", "尔", "你"])

        decomposer.decompose.assert_has_calls(
            [
                call("你"), call("亻"), call("尔"), call("亻"), call("尔"),
            ]
        )

    def test_many_decompositions(self):
        decomposer = MagicMock()

        def _sef(*args):
            if args[0] == "你":
                return MagicMock(decomposition="⿰亻尔")
            if args[0] == "他":
                return MagicMock(decomposition="⿰亻也")
            return ValueError("")
        decomposer.decompose.side_effect = _sef

        cardslist = [
            MagicMock(_headword="也"),
            MagicMock(_headword="亻"),
            MagicMock(_headword="他"),
            MagicMock(_headword="你"),
            MagicMock(_headword="尔"),
        ]
        ts = toposorter_lib.Toposorter(decomposer, cardslist)
        self.assertEqual(ts.get_sorted(), ["也", "亻", "他", "尔", "你", ])

        decomposer.decompose.assert_has_calls([
            call("也"),
            call("亻"),
            call("他"),
            call("亻"),
            call("也"),
            call("你"),
            call("亻"),
            call("尔"),
            call("尔"),
        ])

    def test_one_card_one_decomposition_injected_lexiographic_order(self):
        decomposer = MagicMock()

        def _sef(*args):
            if args[0] == "你":
                return MagicMock(decomposition="⿰亻尔")
            return ValueError("")
        decomposer.decompose.side_effect = _sef

        cardslist = [
            MagicMock(_headword="你"),
            MagicMock(_headword="亻"),
            MagicMock(_headword="尔"),
        ]
        ts = toposorter_lib.Toposorter(decomposer, cardslist)

        def _freq(c):
            if c == "亻":
                return 1.1
            if c == "尔":
                return 2.2

        self.assertEqual(ts.get_sorted(key=_freq), ["亻", "尔", "你"])

        def _freq_other(c):
            if c == "亻":
                return 2.2
            if c == "尔":
                return 1.1

        self.assertEqual(ts.get_sorted(key=_freq_other), ["尔", "亻", "你"])

        decomposer.decompose.assert_has_calls(
            [
                call("你"), call("亻"), call("尔"), call("亻"), call("尔"),
            ]
        )


if __name__ == "__main__":
    absltest.main()
