from src import decomposer

from typing import cast
from absl.testing import absltest
import networkx as nx

# Only create this once. It is expensive.
DECOMPOSER_ = decomposer.Decomposer()


class GraphTest(absltest.TestCase):
    def test_graph(self):
        g = nx.DiGraph()
        g.add_edge(1, 2, p="1 to 2")
        g.add_edge(1, 3, p="1 to 3")
        g.add_edge(2, 4, p="2 to 4")
        g.add_edge(4, 5, p="4 to 5")
        self.assertDictEqual(
            {
                2: "1 to 2",
                3: "1 to 3",
                4: "1 to 2, 2 to 4",
                5: "1 to 2, 2 to 4, 4 to 5",
            },
            decomposer._build_paths(g,
                                    node=1,
                                    data_lookup=lambda m: m["p"],
                                    accumulator=lambda a, b: b + ", " + a))


class DecomposerTest(absltest.TestCase):
    def test_construct_and_query(self):
        char = "你"
        sequence_default = "⿰亻尔"

        seq = decomposer.IdeographicSequence(char, sequence_default)

        DECOMPOSER_.insert(seq)

        self.assertTrue(DECOMPOSER_.contains(char))
        self.assertEqual(DECOMPOSER_.decompose(char), seq)

    def test_get_component(self):
        # At all shapes and sizes.
        self.assertContainsSubset(["你", "您", "妳", "弥", "猕", "㟜", "㳽"],
                                  DECOMPOSER_.get_component("尔"))

    def test_parse_one_line(self):
        # NB: This line is tab-separated.
        line = ("U+4EE4\t令\t^⿱⿵𠆢丶龴$(G)\t^⿱⿵𠆢一龴$(HTV)\t" "^⿱⿵𠆢一𰆊$(JK)")

        maybe_ling = decomposer._parse(line)
        self.assertIsNotNone(maybe_ling)

        ling = cast(
            decomposer.IdeographicSequence,
            maybe_ling)
        self.assertEqual(ling.character, "令")
        self.assertEqual(ling.decomposition, "⿱⿵𠆢丶龴")

    def test_thirdparty_database_contains(self):
        # Assert that the decomposer knows about some characters.
        self.assertTrue(DECOMPOSER_.contains("他"))
        self.assertTrue(DECOMPOSER_.contains("你"))
        self.assertTrue(DECOMPOSER_.contains("我"))
        # And that it didn't scoop up any garbage.
        self.assertFalse(DECOMPOSER_.contains("A"))
        self.assertFalse(DECOMPOSER_.contains(" "))
        self.assertFalse(DECOMPOSER_.contains("."))

    def test_thirdparty_database_decomposes(self):
        # Test some assorted decompositions.
        self.assertEqual(
            DECOMPOSER_.decompose("你").decomposition, "⿰亻尔")

    # There are some characters we cannot decompose! Maybe ids.txt has a ? in
    # it.
    def test_thirdparty_database_cannot_decompose(self):
        with self.assertRaises(ValueError) as _:
            print(DECOMPOSER_.decompose("a"))


if __name__ == "__main__":
    absltest.main()
