import converter
import os
import unittest


def strip_white_space(str):
    return str.replace(" ", "").replace("\t", "").replace("\n", "")


class UtilsTest(unittest.TestCase):
    def test_iscjk(self):
        self.assertTrue(converter.is_cjk("你"))
        self.assertFalse(converter.is_cjk("a"))
        self.assertFalse(converter.is_cjk("1"))
        self.assertFalse(converter.is_cjk(" "))

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
        self.assertEqual(converter.to_html(
            "foo1bar2"), """<span><font color="red">fōo</font></span> <span><font color="green">bár</font></span>""")
        self.assertEqual(converter.to_html(
            "foo3bar4"), """<span><font color="blue">fŏo</font></span> <span><font color="purple">bàr</font></span>""")
        self.assertEqual(converter.to_html("foo5"),
                         """<span><font color="grey">foo</font></span>""")


class ConverterTest(unittest.TestCase):

    def test_run(self):
        with open("testdata/output.csv", "r") as f:
            self.assertEqual(strip_white_space(converter.process_path(
                "testdata/input.xml")), strip_white_space(f.read()))


if __name__ == '__main__':
    unittest.main()
