#! /usr/bin/python3

from absl import app
from absl import flags
from absl import logging
import xml.etree.ElementTree as ET
import networkx as nx

from src import card as card_lib
from src import decomposer as decomposer_lib

FLAGS = flags.FLAGS
flags.DEFINE_string("xml_input_path", None,
                    "Path to the .xml file exported by Pleco.")


def add(G, D, headword):
    if len(headword) > 1:
        # many characters
        G.add_node(headword)
        for w in headword:
            G.add_node(w)
            G.add_edge(w, headword)
    else:
        # one character
        G.add_node(headword)
        try:
            for w in D.decompose(headword).decomposition:
                if w not in decomposer_lib._VERBS and w != headword:
                    G.add_edge(w, headword)
                    add(G, D, w)
        except:
            pass

def main(argv):
    del argv

    if not FLAGS.xml_input_path:
        raise app.UsageError("Must provide --xml_input_path.")

    cards_list = ET.parse(FLAGS.xml_input_path).getroot().find('cards')
    if cards_list is None:
        raise app.UsageError("Could not find inner element `cards`.")

    D = decomposer_lib.Decomposer()
    G = nx.DiGraph()  # G.add_edge(part, whole)

    logging.info("Analyzing %d cards.", len(cards_list))

    card_objects = []
    for xml_card in cards_list:
        entry = xml_card.find('entry')
        try:
            card_obj = card_lib.Card.Build(entry)
            card_objects.append(card_obj)
        except:
            continue
        add(G, D, card_obj._headword)

    # detect cycles
    try:
        nx.algorithms.cycles.find_cycle(G)
    except nx.NetworkXNoCycle:
        pass

    print(list(nx.algorithms.dag.lexicographical_topological_sort(G)))

    logging.info(f"Processed {len(card_objects)} cards.")


if __name__ == '__main__':
    app.run(main)
