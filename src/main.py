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

    pleco_struct = converter_lib.PlecoToAnki(
        FLAGS.xml_input_path, FLAGS.audio_out, FLAGS.frequencies_csv_path)

    FQ = frequency_lib.Frequencies(FLAGS.frequencies_csv_path)
    D = decomposer_lib.Decomposer()
    TS = toposorter_lib.Toposorter(D, pleco_struct.cards.values())
    AR = anki_utils_lib.AnkiReader(FLAGS.collection_path)
    AB = anki_utils_lib.AnkiBuilder(
        FLAGS.audio_out, AR, D, pleco_struct.cards)

    sorted_headwords = TS.get_sorted(key=FQ.get_frequency)

    for hw in sorted_headwords:
        try:
            AB.process(hw)
        except Exception as e:
            logging.info(e)
            continue

    AB.make_package().write_to_file(os.path.join(FLAGS.apkg_out, _OUTPUT_APKG))


if __name__ == '__main__':
    app.run(main)
