#! /usr/bin/python3

from absl import app
from absl import flags
from absl import logging
import os

from src import anki_utils as anki_utils_lib
from src import categorizer as categorizer_lib
from src import converter as converter_lib
from src import decomposer as decomposer_lib
from src import frequency as frequency_lib
from src import hsk_utils as hsk_utils_lib


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

    hsk_reader = hsk_utils_lib.HskReader()
    decomposer = decomposer_lib.Decomposer()
    categorizer = categorizer_lib.Categorizer(decomposer, hsk_reader)
    anki_builder = anki_utils_lib.AnkiBuilder(
        FLAGS.audio_out, categorizer, cards_dict)
    frequencies = frequency_lib.Frequencies(FLAGS.frequencies_csv_path)
    anki_reader = anki_utils_lib.AnkiReader(FLAGS.collection_path)

    added, skipped = set(), set()
    for hw in cards_dict.keys():
        if anki_builder.process(hw):
            added.add(hw)
        else:
            skipped.add(hw)
    logging.info(f"added {len(added)}, skipped {len(skipped)}")

    anki_builder.make_package().write_to_file(
        os.path.join(FLAGS.apkg_out, _OUTPUT_APKG))


if __name__ == '__main__':
    app.run(main)
