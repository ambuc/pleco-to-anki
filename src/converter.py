from src import frequency
from src import card
from src import xml_extractors

from absl import logging
from typing import Text
from dataclasses import dataclass
import xml.etree.ElementTree as ET


def to_csv_cols(
        pinyin_html: Text,
        characters: Text,
        definition: Text,
        sound: Text,
        frequency: Text) -> Text:
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


def PlecoToAnki(
        path_to_xml_input_file,
        directory_of_anki_collection_dot_media,
        path_to_frequencies_csv):
    frequencies_dict = frequency.make_frequencies_dict(
        path_to_frequencies_csv)

    element_tree = ET.parse(path_to_xml_input_file)
    root = element_tree.getroot()
    cards_list = root.find('cards')
    if cards_list is None:
        raise ValueError("Could not find inner element `cards`.")
    logging.info("Analyzing %d cards.", len(cards_list))

    vocab_csv_rows = []
    listening_csv_rows = []

    for xml_card in cards_list:
        entry = xml_card.find('entry')
        card_obj = card.Card.Build(entry)
        if not card_obj:
            continue
        headword = xml_extractors.get_headword(entry)  # 进行
        if headword is None:
            continue

        defn = xml_extractors.get_defn(entry)  # whatever
        if defn is None:
            continue

        card_obj.WriteSoundfile(directory_of_anki_collection_dot_media)

        vocab_csv_rows.append(
            card_obj.MakeCsvRow(
                directory_of_anki_collection_dot_media, frequencies_dict)
        )

        # exclude single-syllable phrases from listening csv
        if len(headword) > 1:
            listening_csv_rows.append(
                card_obj.MakeCsvRowForListening(
                    directory_of_anki_collection_dot_media, frequencies_dict)
            )

    return CsvsStruct(
        vocab_csv="\n".join(vocab_csv_rows),
        listening_csv="\n".join(listening_csv_rows)
    )
