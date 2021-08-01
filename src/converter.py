from src import pinyin
from src import sound
from src import frequency
from src import xml_extractors

from absl import logging
from typing import Text
from dataclasses import dataclass
import xml.etree.ElementTree as ET


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


@dataclass
class CsvsStruct:
    listening_csv: Text
    vocab_csv: Text


def PlecoToAnki(path_to_xml_input_file, directory_of_anki_collection_dot_media, path_to_frequencies_csv):
    frequencies_dict = frequency.make_frequencies_dict(
        path_to_frequencies_csv)

    element_tree = ET.parse(path_to_xml_input_file)
    root = element_tree.getroot()
    cards_list = root.find('cards')
    if cards_list == None:
        raise ValueError("Could not find inner element `cards`.")
    logging.info("Analyzing %d cards.", len(cards_list))

    vocab_csv_rows = []
    listening_csv_rows = []

    for card in cards_list:
        entry = card.find('entry')
        headword = xml_extractors.get_headword(entry)  # 进行
        if headword == None:
            continue

        pron_numbers = xml_extractors.get_pron_numbers(entry)  # jin4xing2
        if pron_numbers == None:
            continue
        pinyin_str = pinyin.sanitize(pron_numbers)

        defn = xml_extractors.get_defn(entry)  # whatever
        if defn == None:
            continue

        filename = sound.make_filename(pinyin_str)
        fullpath = sound.make_fullpath(
            directory_of_anki_collection_dot_media, filename)
        sound.write_soundfile(fullpath, headword)

        vocab_csv_rows.append(
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

        listening_csv_rows.append(
            ";".join(
                [
                    # audiofile
                    f"[sound:{filename}]",
                    # meaning
                    make_defn_html(defn),
                    # pinyin
                    pinyin.pinyin_text_to_html(pinyin_str),
                    # characters
                    headword,
                ]
            )
        )
    return CsvsStruct(
        vocab_csv="\n".join(vocab_csv_rows),
        listening_csv="\n".join(listening_csv_rows)
    )
