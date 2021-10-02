#! /usr/bin/python3

from absl import app
from absl import flags
from absl import logging
import xml.etree.ElementTree as ET

from src import card as card_lib

FLAGS = flags.FLAGS
flags.DEFINE_string("xml_input_path", None,
                    "Path to the .xml file exported by Pleco.")


def main(argv):
    del argv

    if not FLAGS.xml_input_path:
        raise app.UsageError("Must provide --xml_input_path.")

    cards_list = ET.parse(FLAGS.xml_input_path).getroot().find('cards')
    if cards_list is None:
        raise app.UsageError("Could not find inner element `cards`.")

    logging.info("Analyzing %d cards.", len(cards_list))

    card_objects = []
    for xml_card in cards_list:
        entry = xml_card.find('entry')
        try:
            card_obj = card_lib.Card.Build(entry)
            card_objects.append(card_obj)
        except:
            continue
        logging.info(card_obj._headword)

    logging.info(f"Processed {len(card_objects)} cards.")


if __name__ == '__main__':
    app.run(main)
