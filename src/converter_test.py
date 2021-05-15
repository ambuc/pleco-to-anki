import converter
import os
import unittest
import tempfile


def strip_white_space(str):
    return str.replace(" ", "").replace("\t", "").replace("\n", "")


class UtilsTest(unittest.TestCase):
    def test_iscjk(self):
        self.assertTrue(converter._is_cjk("你"))
        self.assertFalse(converter._is_cjk("a"))
        self.assertFalse(converter._is_cjk("1"))
        self.assertFalse(converter._is_cjk(" "))

    def test_sanitize(self):
        expected = "gan1bei2"
        self.assertEqual(converter.sanitize("gan1bei2"), expected)
        self.assertEqual(converter.sanitize("GAN1BEI2"), expected)
        self.assertEqual(converter.sanitize("gan1//BEI2"), expected)
        self.assertEqual(converter.sanitize(" gan1/ BEI2/"), expected)
        self.assertEqual(converter.sanitize("gan1//Bei2"), expected)

    def test_tosyllablepairs(self):
        self.assertEqual(converter.to_syllablepairs("bie2ren5"), [
                         ("bie", converter.Tone.RISING), ("ren", converter.Tone.NEUTRAL)])

    def test_tohtml(self):
        self.assertEqual(converter._pinyin_text_to_html(
            "foo1bar2"), """<span><font color="red">fōo</font></span> <span><font color="green">bár</font></span>""")
        self.assertEqual(converter._pinyin_text_to_html(
            "foo3bar4"), """<span><font color="blue">fŏo</font></span> <span><font color="purple">bàr</font></span>""")
        self.assertEqual(converter._pinyin_text_to_html("foo5"),
                         """<span><font color="grey">foo</font></span>""")


class ConverterTest(unittest.TestCase):

    def test_run(self):
        with open("testdata/output.csv", "r") as f:
            p2ac = converter.PlecoToAnkiConverter(
                "testdata/input.xml", None, None)
            a = strip_white_space(p2ac.return_csv())
            b = strip_white_space(f.read())
            self.assertEqual(a, b)

    def test_run_with_audio(self):
        with open("testdata/output-audio.csv", "r") as f:
            with tempfile.TemporaryDirectory() as d:
                p2ac = converter.PlecoToAnkiConverter(
                    "testdata/input.xml", d, None)
                a = strip_white_space(p2ac.return_csv())
                b = strip_white_space(f.read())
                self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
