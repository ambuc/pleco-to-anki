#! /usr/bin/python3

from absl import app
from absl import flags
from absl import logging
from src import converter

FLAGS = flags.FLAGS
flags.DEFINE_string("xml_input_path", None, "Path to the input .xml.")
flags.DEFINE_string("audio_out", None, "Path to write audio files, or None to "
                    "disable.")
flags.DEFINE_string("frequencies_csv_path", None,
                    "Path to the frequencies csv, if available.")
flags.DEFINE_string("vocab_csv_out", None,
                    "Path to the output vocab csv to write.")
flags.DEFINE_string("listening_csv_out", None,
                    "Path to the output listening csv to write.")


def main(argv):
    del argv

    csvs_struct = converter.PlecoToAnki(FLAGS.xml_input_path,
                                        FLAGS.audio_out, FLAGS.frequencies_csv_path)

    with open(FLAGS.vocab_csv_out, "w") as f:
        f.write(csvs_struct.vocab_csv)
        logging.info(
            f"Wrote {csvs_struct.vocab_length} rows to {FLAGS.vocab_csv_out}")

    with open(FLAGS.listening_csv_out, "w") as f:
        f.write(csvs_struct.listening_csv)
        logging.info(
            f"Wrote {csvs_struct.listening_length} rows to {FLAGS.listening_csv_out}")

    # MUST MUST MUST dedup these impls


if __name__ == '__main__':
    app.run(main)
