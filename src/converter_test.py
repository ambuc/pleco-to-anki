import converter

import unittest
import tempfile


def strip_white_space(str):
    return str.replace(" ", "").replace("\t", "").replace("\n", "")


class MatchNumbersTest(unittest.TestCase):
    def test(self):
        input = "1 foo 2 bar 3 baz"
        self.assertEqual(converter.match_numbers(input),
                         "<ol><li>foo </li><li>bar </li><li>baz</li></ol>")


class MakeDefnHtml(unittest.TestCase):
    def test_make_defn_html(self):
        for input, expected_output in [
            ("1 foo 2 bar 3 baz",
             "<ol><li>foo </li><li>bar </li><li>baz</li></ol>"),
            ("foo bar baz",
             "foo bar baz"),
        ]:
            actual_output = converter.make_defn_html(input)
            self.assertEqual(expected_output, actual_output)


class ConverterTest(unittest.TestCase):

    def test(self):
        self.maxDiff = 10000
        with tempfile.TemporaryDirectory() as audio_output_dir:
            r = converter.PlecoToAnki(
                "testdata/input.xml", audio_output_dir, "testdata/frequencies.csv")
            with open("testdata/output-vocab.csv", "r") as f:
                self.assertEqual(strip_white_space(
                    r.vocab_csv), strip_white_space(f.read()))
            with open("testdata/output-listening.csv", "r") as f:
                self.assertEqual(strip_white_space(
                    r.listening_csv), strip_white_space(f.read()))


if __name__ == '__main__':
    unittest.main()
