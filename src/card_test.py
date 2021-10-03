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


class MatchNumbersTest(unittest.TestCase):
    def test(self):
        input = "1 foo 2 bar 3 baz"
        self.assertEqual(card._match_numbers(input),
                         "<ol><li>foo </li><li>bar </li><li>baz</li></ol>")


class MakeDefnHtml(unittest.TestCase):
    def test_make_defn_html(self):
        for input, expected_output in [
            ("1 foo 2 bar 3 baz",
             "<ol><li>foo </li><li>bar </li><li>baz</li></ol>"),
            ("foo bar baz",
             "foo bar baz"),
        ]:
            actual_output = card._make_defn_html(input)
            self.assertEqual(expected_output, actual_output)


class VowelTest(unittest.TestCase):
    def test_isvowel(self):
        for v in ['a', 'e', 'i', 'o', 'u', 'y', 'ü']:
            self.assertTrue(card._is_vowel(v))
        for v in ['b', 'c', '你', '好']:
            self.assertFalse(card._is_vowel(v))


class DiacriticTest(unittest.TestCase):
    def test_add_diacritic_to_word(self):
        for unaccented, tone, accented in [
                ("gao", card.Tone.RISING, "gáo"),
                ("gao", card.Tone.FALLING, "gào"),
                ("gao", card.Tone.NEUTRAL, "gao"),
                ("gao", card.Tone.USHAPED, "găo"),
                ("gao", card.Tone.FLAT, "gāo"),
        ]:
            self.assertEqual(
                card._add_diacritic_to_word(unaccented, tone),
                accented)

    def test_add_diacritic_to_word_without_vowel(self):
        self.assertEqual(card._add_diacritic_to_word(
            "xz", card.Tone.FLAT), "xz")


class SanitizerTest(unittest.TestCase):
    def test_sanitization(self):
        self.assertEqual(card._sanitize_pinyin("gan1//Bei1"), "gan1bei1")
        self.assertEqual(card._sanitize_pinyin("GAN1BEI1"), "gan1bei1")
        self.assertEqual(card._sanitize_pinyin("gan1//BEI1"), "gan1bei1")
        self.assertEqual(card._sanitize_pinyin("gan 1 bei 1"), "gan1bei1")


class SyllablePairsTest(unittest.TestCase):
    def test_syllablepairs(self):
        self.assertListEqual(
            [
                ("bie", card.Tone.RISING),
                ("ren", card.Tone.NEUTRAL),
            ],
            card._to_syllablepairs("bie2ren5"))


class ToHtmlTest(unittest.TestCase):
    def test_to_html(self):
        for input, output in [
            ("bie2ren5",
             '<span><font color="green">bíe</font></span> <span><font color="grey">ren</font></span>'
             ),
            ("gan3mao1",
             '<span><font color="blue">găn</font></span> <span><font color="red">māo</font></span>'),
        ]:
            self.assertEqual(card._pinyin_text_to_html(input), output)


if __name__ == '__main__':
    unittest.main()
