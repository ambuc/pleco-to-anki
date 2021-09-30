import defn_extractor

import unittest


class MatchNumbersTest(unittest.TestCase):
    def test(self):
        input = "1 foo 2 bar 3 baz"
        self.assertEqual(defn_extractor.match_numbers(input),
                         "<ol><li>foo </li><li>bar </li><li>baz</li></ol>")


class MakeDefnHtml(unittest.TestCase):
    def test_make_defn_html(self):
        for input, expected_output in [
            ("1 foo 2 bar 3 baz",
             "<ol><li>foo </li><li>bar </li><li>baz</li></ol>"),
            ("foo bar baz",
             "foo bar baz"),
        ]:
            actual_output = defn_extractor.make_defn_html(input)
            self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
