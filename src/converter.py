from src import frequency as frequency_lib
from src import card
from src import xml_extractors

from absl import logging
from typing import Mapping, Text, List
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
class PlecoToAnkiReturnStruct:
    listening_csv: Text
    listening_length: int
    cards: Mapping[Text, card.Card]
    vocab_csv: Text
    vocab_length: int


def PlecoToAnki(
        path_to_xml_input_file,
        directory_of_anki_collection_dot_media,
        path_to_frequencies_csv):
    fq = frequency_lib.Frequencies(path_to_frequencies_csv)

    element_tree = ET.parse(path_to_xml_input_file)
    root = element_tree.getroot()
    cards_list = root.find('cards')
    if cards_list is None:
        raise ValueError("Could not find inner element `cards`.")
    logging.info("Analyzing %d cards.", len(cards_list))

    cards = []
    vocab_csv_rows = []
    listening_csv_rows = []

    for xml_card in cards_list:
        entry = xml_card.find('entry')
        try:
            card_obj = card.Card.Build(entry)
        except BaseException:
            continue

        card_obj.WriteSoundfile(directory_of_anki_collection_dot_media)

        cards.append(card_obj)

        vocab_csv_rows.append(
            card_obj.MakeCsvRow(fq)
        )

        # exclude single-syllable phrases from listening csv
        if len(card_obj._headword) > 1:
            listening_csv_rows.append(
                card_obj.MakeCsvRowForListening(fq)
            )

    return PlecoToAnkiReturnStruct(
        cards={card._headword: card for card in cards},
        vocab_csv="\n".join(vocab_csv_rows),
        vocab_length=len(vocab_csv_rows),
        listening_csv="\n".join(listening_csv_rows),
        listening_length=len(listening_csv_rows)
    )
