import converter

import unittest
import tempfile


class ConverterTest(unittest.TestCase):

    def test(self):
        cards = converter.ExtractCards(
            "testdata/input.xml")

        self.assertEqual(len(cards), 4)
        self.assertSetEqual(set(cards.keys()),
                            set(["再次", "进行", "黑", "感冒"]))


if __name__ == '__main__':
    unittest.main()
