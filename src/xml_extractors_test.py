import unittest
import xml_extractors
import xml.etree.ElementTree as ET


class GetHeadwordTest(unittest.TestCase):
    def test_none(self):
        with self.assertRaisesRegex(ValueError, ".*Can't call get_headword().*"):
            xml_extractors.get_headword(None)

    def test_no_headwords(self):
        entry = ET.Element('entry')
        with self.assertRaisesRegex(ValueError, ".*no headwords at all.*"):
            xml_extractors.get_headword(entry)

    def test_no_sc_charset(self):
        entry = ET.Element('entry')
        ET.SubElement(entry, 'headword', {'charset': 'tc'})

        with self.assertRaisesRegex(ValueError, ".*Could not find a headword with charset=='sc'.*"):
            xml_extractors.get_headword(entry)

    def test_sc_no_text(self):
        entry = ET.Element('entry')

        sc = ET.SubElement(entry, 'headword', {'charset': 'sc'})
        sc.text = None

        with self.assertRaisesRegex(ValueError, ".*absent headword text.*"):
            xml_extractors.get_headword(entry)

    def test_happy_path(self):
        entry = ET.Element('entry')

        sc = ET.SubElement(entry, 'headword', {'charset': 'sc'})
        sc.text = "foo"

        self.assertEqual(xml_extractors.get_headword(entry), "foo")


class GetPronNumbersTest(unittest.TestCase):
    def test_no_entry(self):
        entry = None
        self.assertEqual(xml_extractors.get_pron_numbers(entry), None)

    def test_no_pron(self):
        entry = ET.Element('entry')
        self.assertEqual(xml_extractors.get_pron_numbers(entry), None)

    def test_no_type(self):
        entry = ET.Element('entry')
        pron = ET.SubElement(entry, 'pron')
        self.assertEqual(xml_extractors.get_pron_numbers(entry), None)

    def test_no_tones(self):
        entry = ET.Element('entry')
        pron = ET.SubElement(entry, 'pron', {'type': 'hypy'})
        self.assertEqual(xml_extractors.get_pron_numbers(entry), None)

    def test_no_text(self):
        entry = ET.Element('entry')
        pron = ET.SubElement(
            entry, 'pron', {'type': 'hypy', 'tones': 'numbers'})
        self.assertEqual(xml_extractors.get_pron_numbers(entry), None)

    def test_happy_path(self):
        entry = ET.Element('entry')
        pron = ET.SubElement(
            entry, 'pron', {'type': 'hypy', 'tones': 'numbers'})
        pron.text = "foo"
        self.assertEqual(xml_extractors.get_pron_numbers(entry), "foo")


class GetDefnTest(unittest.TestCase):
    def test_no_entry(self):
        entry = None
        self.assertEqual(xml_extractors.get_defn(entry), None)

    def test_no_defn(self):
        entry = ET.Element('entry')
        self.assertEqual(xml_extractors.get_defn(entry), None)

    def test_no_defn_text(self):
        entry = ET.Element('entry')
        defn = ET.SubElement(entry, 'defn')
        defn.text = None
        self.assertEqual(xml_extractors.get_defn(entry), None)

    def test_happy_path(self):
        entry = ET.Element('entry')
        defn = ET.SubElement(entry, 'defn')
        defn.text = "foo:; bar\nbaz"
        # NB: ';'  => '.'
        # NB: '\n' => ' '
        self.assertEqual(xml_extractors.get_defn(entry), "foo:. bar baz")


if __name__ == '__main__':
    unittest.main()
