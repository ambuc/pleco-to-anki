from src import anki_utils as anki_utils_lib

import tempfile
from unittest.mock import MagicMock, call
from absl.testing import absltest


class AnkiUtilsTest(absltest.TestCase):

    def test(self):
        self.assertEqual(anki_utils_lib._gen_template(1,
                                                      ["foo",
                                                       "bar"],
                                                      ["baz"]),
                         {'name': 'Card 1 foo+bar=>baz',
                          'qfmt': "<span id='foo'>{{foo}}</span><br><span id='bar'>{{bar}}</span>",
                          'afmt': "{{FrontSide}} <hr><span id='baz'>{{baz}}</span>",
                          })

    def test_headword_not_in_pleco_cards(self):
        anki_reader = MagicMock()
        decomposer = MagicMock()
        hsk_reader = MagicMock()
        with tempfile.TemporaryDirectory() as audio_output_dir, tempfile.NamedTemporaryFile(mode='w+',
                                                                                            suffix='.csv') as f:
            ab = anki_utils_lib.AnkiBuilder(
                audio_output_dir,
                anki_reader,
                decomposer,
                hsk_reader,
                pleco_cards={})

            with self.assertRaisesRegex(KeyError, ".*感冒 not in Pleco cards, cannot create Anki card.*"):
                ab.process("感冒")

    def test_headword_in_pleco_cards(self):
        anki_reader = MagicMock()

        def _sef(*args):
            if args[0] == "感冒":
                return anki_utils_lib.CardType.New
            return anki_utils_lib.CardType.Mature
        anki_reader.get_type.side_effect = _sef

        anki_reader.listening_v1_contains.return_value = False
        anki_reader.vocab_v1_contains.return_value = False

        decomposer = MagicMock()
        hsk_reader = MagicMock()
        with tempfile.TemporaryDirectory() as audio_output_dir, tempfile.NamedTemporaryFile(mode='w+',
                                                                                            suffix='.csv') as f:
            ab = anki_utils_lib.AnkiBuilder(
                audio_output_dir,
                anki_reader,
                decomposer,
                hsk_reader,
                pleco_cards={
                    "感冒": MagicMock(
                        _headword="感冒",
                        _pinyin_html="pinyin",
                        _sound="sound",
                        _defn_html="defn"),
                    "感": MagicMock(
                        _headword="感"),
                    "冒": MagicMock(
                        _headword="冒"),
                })

            ab.process("感冒")

            package = ab.make_package()
            self.assertEqual(len(package.decks), 3)

            vocab_v2_deck = next(
                filter(lambda d: d.name == "zw::vocab_v2", package.decks))
            self.assertEqual(vocab_v2_deck.name, "zw::vocab_v2")
            self.assertEqual(len(vocab_v2_deck.notes), 1)
            self.assertEqual(vocab_v2_deck.notes[0].fields, [
                             "感冒", "pinyin", "defn", "sound"])
            self.assertEqual(len(vocab_v2_deck.notes[0].cards), 4)
            vocab_model = vocab_v2_deck.notes[0].model
            self.assertEqual(vocab_model.model_id, 10001)
            self.assertEqual(vocab_model.name, 'model_zw_vocab_v2')
            self.assertEqual(vocab_model.fields, [{'name': 'characters'}, {
                             'name': 'pinyin'}, {'name': 'meaning'}, {'name': 'audio'}])

            listening_v2_deck = next(
                filter(lambda d: d.name == "zw::listening_v2", package.decks))
            self.assertEqual(listening_v2_deck.name, "zw::listening_v2")
            self.assertEqual(len(listening_v2_deck.notes), 1)
            self.assertEqual(listening_v2_deck.notes[0].fields, [
                             "sound", "defn", "pinyin", "感冒"])
            self.assertEqual(len(listening_v2_deck.notes[0].cards), 1)
            listening_model = listening_v2_deck.notes[0].model
            self.assertEqual(listening_model.model_id, 10002)
            self.assertEqual(listening_model.name, 'model_zw_listening_v2')
            self.assertEqual(listening_model.fields, [{'name': 'audio'}, {
                             'name': 'meaning'}, {'name': 'pinyin'}, {'name': 'characters'}])


if __name__ == "__main__":
    absltest.main()
