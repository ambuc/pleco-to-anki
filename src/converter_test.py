import converter

import unittest
import tempfile

def strip_white_space(str):
    return str.replace(" ", "").replace("\t", "").replace("\n", "")

class ConverterTest(unittest.TestCase):

    def test_run_with_audio(self):
        with open("testdata/output.csv", "r") as f:
            with tempfile.TemporaryDirectory() as audio_output_dir:
                self.maxDiff=10000
                return_csv = converter.PlecoToAnki(
                    "testdata/input.xml", audio_output_dir, "testdata/frequencies.csv")
                a = strip_white_space(return_csv)
                b = strip_white_space(f.read())
                self.assertEqual(a, b)

if __name__ == '__main__':
    unittest.main()
