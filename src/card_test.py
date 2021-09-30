import card

import unittest
import xml.etree.ElementTree as ET

_XML = """
<entry>
	<headword charset="sc">感冒</headword>
	<headword charset="tc">感冒</headword>
	<pron type="hypy" tones="numbers">gan3mao4</pron>
	<defn>noun common cold
b 1 catch cold 2 dialect be interested in; like (usu. used in the negative)</defn>
</entry>
"""


class CardCreationTest(unittest.TestCase):
    def test(self):
        entry_element = ET.fromstring(_XML)
        c = card.Card.Build(entry_element)
        self.assertEqual(c._headword, "感冒")
        self.assertEqual(c._pinyin_str, "gan3mao4")
        self.assertRegexpMatches(c._defn, ".*noun common cold.*")


if __name__ == '__main__':
    unittest.main()
