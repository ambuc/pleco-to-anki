#! /usr/bin/python3

from absl import app
from absl import flags
from absl import logging
import os

from src import anki_utils as anki_utils_lib
from src import converter as converter_lib
from src import decomposer as decomposer_lib
from src import toposorter as toposorter_lib
from src import frequency as frequency_lib


FLAGS = flags.FLAGS
flags.DEFINE_string("xml_input_path", None, "Path to the input .xml.")
flags.DEFINE_string("audio_out", None,
                    "Path to write audio files, or None to disable.")
flags.DEFINE_string("collection_path", None,
                    "Path to Anki collection .ank2 file.")
flags.DEFINE_string("frequencies_csv_path", None,
                    "Path to the frequencies csv, if available.")
flags.DEFINE_string("apkg_out", None, "Path to write .apkg.")

_OUTPUT_APKG = 'output.apkg'


def main(argv):
    del argv

    if not FLAGS.xml_input_path:
        raise app.UsageError("Must provide --xml_input_path.")
    if not FLAGS.audio_out:
        raise app.UsageError("Must provide --audio_out.")
    if not FLAGS.collection_path:
        raise app.UsageError("Must provide --collection_path.")
    if not FLAGS.frequencies_csv_path:
        raise app.UsageError("Must provide --frequencies_csv_path.")
    if not FLAGS.apkg_out:
        raise app.UsageError("Must provide --apkg_out.")

    cards_dict = converter_lib.ExtractCards(FLAGS.xml_input_path)

    frequencies = frequency_lib.Frequencies(FLAGS.frequencies_csv_path)
    decomposer = decomposer_lib.Decomposer()
    toposorter = toposorter_lib.Toposorter(decomposer, cards_dict.values())
    anki_reader = anki_utils_lib.AnkiReader(FLAGS.collection_path)
    anki_builder = anki_utils_lib.AnkiBuilder(
        FLAGS.audio_out, anki_reader, decomposer, cards_dict)

    added, skipped = set(), set()
    for hw in toposorter.get_sorted(key=frequencies.get_frequency):
        try:
            anki_builder.process(hw)
        except Exception as e:
            logging.info(e)
            skipped.add(hw)
            continue
        added.add(hw)
    logging.info(f"Added {len(added)}, skipped {len(skipped)}.")
    # logging.info(f"Skipped: {list(skipped)}")

    anki_builder.make_package().write_to_file(
        os.path.join(FLAGS.apkg_out, _OUTPUT_APKG))


if __name__ == '__main__':
    app.run(main)
