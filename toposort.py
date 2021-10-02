#! /usr/bin/python3

from absl import app
from absl import flags
from absl import logging
import xml.etree.ElementTree as ET
import networkx as nx
from typing import List, Text

from src import card as card_lib
from src import decomposer as decomposer_lib
from src import toposorter as toposorter_lib
from src import frequency as frequency_lib

FLAGS = flags.FLAGS
flags.DEFINE_string("xml_input_path", None,
                    "Path to the .xml file exported by Pleco.")
flags.DEFINE_string("frequencies_csv_path", None,
                    "Path to the frequencies csv, if available.")


def main(argv):
    del argv

    if not FLAGS.xml_input_path:
        raise app.UsageError("Must provide --xml_input_path.")
    if not FLAGS.frequencies_csv_path:
        raise app.UsageError("Must provide --frequencies_csv_path.")

    cards_list = ET.parse(FLAGS.xml_input_path).getroot().find('cards')
    if cards_list is None:
        raise app.UsageError("Could not find inner element `cards`.")

    D = decomposer_lib.Decomposer()

    logging.info("Analyzing %d cards.", len(cards_list))

    card_objects = []
    for xml_card in cards_list:
        entry = xml_card.find('entry')
        try:
            card_obj = card_lib.Card.Build(entry)
            card_objects.append(card_obj)
        except:
            continue

    TS = toposorter_lib.Toposorter(D, card_objects)
    fq = frequency_lib.Frequencies(FLAGS.frequencies_csv_path)

    logging.info(f"Processed {len(card_objects)} cards.")
    logging.info(TS.get_sorted(key=lambda l: fq.get_frequency(l)))


if __name__ == '__main__':
    app.run(main)
