from absl import logging
import xml.etree.ElementTree as ET
from typing import Text, Optional


def get_headword(entry) -> Text:
    if entry is None:
        raise ValueError(
            f"Can't call get_headword() on an absent XML entry.")

    headwords_all = list(entry.iter('headword'))
    if len(headwords_all) == 0:
        raise ValueError(
            f"Encountered an entry with no headwords at all: {ET.tostring(entry)}")

    headwords_sc = list(
        filter(lambda hw: hw.get('charset') == 'sc', headwords_all))
    if len(headwords_sc) == 0:
        raise ValueError(
            f"Could not find a headword with charset=='sc' for entry: {ET.tostring(entry)}")

    headword_sc = headwords_sc[0]
    if headword_sc.text is None:
        raise ValueError(
            f"Encountered an entry with an absent headword text: {ET.tostring(entry)}.")

    return headword_sc.text


def get_pron_numbers(entry) -> Optional[Text]:
    if entry is None:
        logging.warning("Encountered an empty entry.")
        return None
    pron = entry.find('pron')
    if pron is None:
        logging.warning("Encountered an entry with no pron: %s",
                        ET.tostring(entry))
        return None
    if pron.get('type') != "hypy":
        logging.warning(
            "Encountered an entry without type='hypy': %s", ET.tostring(entry))
        return None
    if pron.get('tones') != "numbers":
        logging.warning(
            "Encountered an entry without tones='numbers': %s",
            ET.tostring(entry))
        return None
    if pron.text is None:
        logging.warning(
            "Encountered an entry with an empty pron: %s", ET.tostring(entry))
        return None
    return pron.text


def get_defn(entry) -> Optional[Text]:
    if entry is None:
        logging.warning("Encountered an absent entry.")
        return None
    defn = entry.find('defn')
    if defn is None:
        logging.warning("Encountered an entry with no defn: %s",
                        ET.tostring(entry))
        return None
    if defn.text is None:
        logging.warning("Encountered an entry with no defn.text: %s",
                        ET.tostring(entry))
        return None
    ret = defn.text
    # MUST remove semicolons, csv is semicolon-separated.
    ret = ret.replace(';', '.')
    ret = ret.replace('\n', ' ')
    return ret
