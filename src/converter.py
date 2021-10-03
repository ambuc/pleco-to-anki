from src import card

from absl import logging
from typing import Mapping, Text
import xml.etree.ElementTree as ET


def ExtractCards(path_to_xml_input_file) -> Mapping[Text, card.Card]:

    cards_list = ET.parse(path_to_xml_input_file).getroot().find('cards')
    if cards_list is None:
        raise ValueError("Could not find inner element `cards`.")
    logging.info("Analyzing %d cards.", len(cards_list))

    cards = {}

    for xml_card in cards_list:
        try:
            card_obj = card.Card.Build(xml_card.find('entry'))
        except BaseException:
            continue
        cards[card_obj._headword] = card_obj

    return cards
