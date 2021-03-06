#! /usr/bin/python3

from absl import app
from absl import flags
import src.converter as converter_lib

FLAGS = flags.FLAGS
flags.DEFINE_string("path", None, "Path to the input .xml.")
flags.DEFINE_string("audio_out", None, "Path to write audio files, or None to "
                    "disable.")
flags.DEFINE_string("frequencies_csv_path", None,
                    "Path to the frequencies csv, if available.")


def main(argv):
    del argv
    p2ac = converter_lib.PlecoToAnkiConverter(FLAGS.path,
                                              FLAGS.audio_out,
                                              FLAGS.frequencies_csv_path)
    print(p2ac.return_csv())


if __name__ == '__main__':
    app.run(main)
