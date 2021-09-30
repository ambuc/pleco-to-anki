import converter

import unittest
import tempfile


def strip_white_space(str):
    return str.replace(" ", "").replace("\t", "").replace("\n", "")


class ConverterTest(unittest.TestCase):

    def test(self):
        self.maxDiff = 10000
        with tempfile.TemporaryDirectory() as audio_output_dir:
            r = converter.PlecoToAnki(
                "testdata/input.xml",
                audio_output_dir,
                "testdata/frequencies.csv")
            with open("testdata/output-vocab.csv", "r") as f:
                self.assertEqual(strip_white_space(
                    r.vocab_csv), strip_white_space(f.read()))
            with open("testdata/output-listening.csv", "r") as f:
                self.assertEqual(strip_white_space(
                    r.listening_csv), strip_white_space(f.read()))


if __name__ == '__main__':
    unittest.main()
