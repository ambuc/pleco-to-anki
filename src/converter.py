from src import pinyin
from src import sound
from src import frequency

from absl import logging
from typing import Text, Optional, List
import xml.etree.ElementTree as ET


def get_headword(entry) -> Text:
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
    if headword_sc.text == None:
        # return traditional as a fallback.
        return headwords_all[0].text

    return headword_sc.text


def get_pron_numbers(entry) -> Optional[Text]:
    pron = entry.find('pron')
    if pron == None:
        logging.warning("Encountered an entry with no pron: %s",
                        ET.tostring(entry))
        return None
    if pron.get('type') != "hypy":
        logging.warning(
            "Encountered an entry without type='hypy': %s", ET.tostring(entry))
        return None
    if pron.get('tones') != "numbers":
        logging.warning(
            "Encountered an entry without tones='numbers': %s", ET.tostring(entry))
        return None
    if pron.text == None:
        logging.warning(
            "Encountered an entry with an empty pron: %s", ET.tostring(entry))
        return None
    return pron.text


def get_defn(entry) -> Optional[Text]:
    defn = entry.find('defn')
    if defn == None:
        logging.warning("Encountered an entry with no defn: %s",
                        ET.tostring(entry))
        return None
    if defn.text == None:
        logging.warning("Encountered an entry with no defn.text: %s",
                        ET.tostring(entry))
        return None
    ret = defn.text
    # MUST remove semicolons, csv is semicolon-separated.
    ret = ret.replace(';', '.')
    return ret


def match_numbers(defn) -> Text:
    els = []
    matching = 1
    while True:
        i = defn.find(f"{matching} ")
        if i == -1:
            break
        a = i + len(str(matching)) + 1
        j = defn.find(f"{matching+1} ")
        if j == -1:
            els.append(defn[a:])
            break
        els.append(defn[a:j])
        matching += 1
    html = "<ol>"
    for e in els:
        html += "<li>" + e + "</li>"
    html += "</ol>"
    return html


def make_defn_html(defn) -> Text:
    # match things like "1 foo 2 bar 3 baz"
    if "1 " in defn and "2 " in defn:
        return match_numbers(defn)
    return defn


def to_csv_cols(pinyin_html: Text, characters: Text, definition: Text, sound: Text, frequency: Text) -> Text:
    cols = []
    cols.append(pinyin_html)
    cols.append(characters)
    cols.append(definition)
    cols.append(sound)
    cols.append(frequency)
    return ';'.join(cols)


def PlecoToAnki(path_to_xml_input_file, directory_of_anki_collection_dot_media, path_to_frequencies_csv):
    frequencies_dict = frequency.make_frequencies_dict(
        path_to_frequencies_csv)

    element_tree = ET.parse(path_to_xml_input_file)
    root = element_tree.getroot()
    cards_list = root.find('cards')
    if cards_list == None:
        raise ValueError("Could not find inner element `cards`.")
    logging.info("Analyzing %d cards.", len(cards_list))

    csv_rows = []

    for card in cards_list:
        entry = card.find('entry')
        headword = get_headword(entry)  # 进行
        if headword == None:
            continue

        pron_numbers = get_pron_numbers(entry)  # jin4xing2
        if pron_numbers == None:
            continue
        pinyin_str = pinyin.sanitize(pron_numbers)

        defn = get_defn(entry)  # whatever
        if defn == None:
            continue

        filename = sound.make_filename(pinyin_str)
        fullpath = sound.make_fullpath(
            directory_of_anki_collection_dot_media, filename)
        sound.write_soundfile(fullpath, headword)

        csv_rows.append(
            ";".join(
                [
                    headword,

                    # pinyin_html
                    pinyin.pinyin_text_to_html(pinyin_str),

                    # defn html
                    make_defn_html(defn),

                    # soundstring
                    f"[sound:{filename}]",

                    # frequency_str
                    str(frequency.get_frequency(frequencies_dict, headword)),
                ]
            )
        )

    return "\n".join(csv_rows)
