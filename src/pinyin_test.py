import pinyin

from pinyin import to_syllablepairs
from tone import Tone

import unittest


class VowelTest(unittest.TestCase):
    def test_isvowel(self):
        for v in ['a', 'e', 'i', 'o', 'u', 'y', 'ü']:
            self.assertTrue(pinyin.is_vowel(v))
        for v in ['b', 'c', '你', '好']:
            self.assertFalse(pinyin.is_vowel(v))


class DiacriticTest(unittest.TestCase):
    def test_add_diacritic_to_word(self):
        for unaccented, tone, accented in [
                ("gao", Tone.RISING, "gáo"),
                ("gao", Tone.FALLING, "gào"),
                ("gao", Tone.NEUTRAL, "gao"),
                ("gao", Tone.USHAPED, "găo"),
                ("gao", Tone.FLAT, "gāo"),
        ]:
            self.assertEqual(
                pinyin.add_diacritic_to_word(unaccented, tone),
                accented)

    def test_add_diacritic_to_word_without_vowel(self):
        self.assertEqual(pinyin.add_diacritic_to_word("xz", Tone.FLAT), "xz")


class SanitizerTest(unittest.TestCase):
    def test_sanitization(self):
        self.assertEqual(pinyin.sanitize("gan1//Bei1"), "gan1bei1")
        self.assertEqual(pinyin.sanitize("GAN1BEI1"), "gan1bei1")
        self.assertEqual(pinyin.sanitize("gan1//BEI1"), "gan1bei1")
        self.assertEqual(pinyin.sanitize("gan 1 bei 1"), "gan1bei1")


class SyllablePairsTest(unittest.TestCase):
    def test_syllablepairs(self):
        self.assertListEqual(
            [
                ("bie", Tone.RISING),
                ("ren", Tone.NEUTRAL),
            ],
            pinyin.to_syllablepairs("bie2ren5"))


class ToHtmlTest(unittest.TestCase):
    def test_to_html(self):
        for input, output in [
            ("bie2ren5",
             '<span><font color="green">bíe</font></span> <span><font color="grey">ren</font></span>'
             ),
            ("gan3mao1",
             '<span><font color="blue">găn</font></span> <span><font color="red">māo</font></span>'),
        ]:
            self.assertEqual(pinyin.pinyin_text_to_html(input), output)


if __name__ == '__main__':
    unittest.main()
