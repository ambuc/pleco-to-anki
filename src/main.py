#! /usr/bin/python3

from absl import app
from absl import flags
from absl import logging
import os
import genanki

from src import anki_sources
from src import converter as converter_lib
from src import decomposer as decomposer_lib
from src import toposorter as toposorter_lib
from src import anki_reader as anki_reader_lib
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

_MODEL_ID = 10001
_MODEL_NAME = "note_zw_v2"
_DECK_ID = 20001
_DECK_NAME = 'zw_v2'
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

    fields = [
        {'name': 'characters'},
        {'name': 'pinyin'},
        {'name': 'meaning'},
        {'name': 'audio'},
    ]
    templates = [
        anki_sources.gen_template(
            1, ["characters", "meaning"], ["pinyin", "audio"]),
        anki_sources.gen_template(
            2, ["characters", "pinyin", "audio"], ["meaning"]),
        anki_sources.gen_template(
            3, ["pinyin", "audio", "meaning"], ["characters"]),
        anki_sources.gen_template(
            4, ["characters"], ["pinyin", "meaning", "audio"]),
    ]
    model = genanki.Model(
        _MODEL_ID,
        _MODEL_NAME,
        fields=fields,
        templates=templates,
        css=anki_sources._CSS)

    struct = converter_lib.PlecoToAnki(
        FLAGS.xml_input_path, FLAGS.audio_out, FLAGS.frequencies_csv_path)

    FQ = frequency_lib.Frequencies(FLAGS.frequencies_csv_path)
    D = decomposer_lib.Decomposer()
    TS = toposorter_lib.Toposorter(D, struct.cards.values())
    AR = anki_reader_lib.AnkiReader(FLAGS.collection_path)

    deck = genanki.Deck(_DECK_ID, _DECK_NAME)

    sorted_headwords = TS.get_sorted(key=FQ.get_frequency)

    print(sorted_headwords)

    note = genanki.Note(model=model, fields=[
                        '你好', 'ni hao', 'hello', 'some_audio'])
    deck.add_note(note)

    genanki.Package(deck).write_to_file(
        os.path.join(FLAGS.apkg_out, _OUTPUT_APKG))


if __name__ == '__main__':
    app.run(main)
