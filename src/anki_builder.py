
import genanki

from absl import logging
from src import anki_sources
from src import card as card_lib
from src import decomposer as decomposer_lib
from src import anki_reader as anki_reader_lib

from typing import Text, Mapping

_VOCAB_V2_DECK_ID = 20001
_VOCAB_V2_DECK_NAME = 'zw::vocab_v2'
_VOCAB_V2_MODEL_ID = 10001
_VOCAB_V2_MODEL_NAME = "model_zw_vocab_v2"

_LISTENING_DECK_ID = 20002
_LISTENING_DECK_NAME = 'zw::listening_v2'
_LISTENING_V2_MODEL_ID = 10002
_LISTENING_V2_MODEL_NAME = "model_zw_listening_v2"

_RADICALS_V2_DECK_ID = 20003
_RADICALS_V2_DECK_NAME = 'zw::radicals_v2'
_RADICALS_V2_MODEL_ID = 10003
_RADICALS_V2_MODEL_NAME = "model_zw_radicals_v2"

_VOCAB_MODEL = genanki.Model(
    _VOCAB_V2_MODEL_ID,
    _VOCAB_V2_MODEL_NAME,
    fields=[
        {'name': 'characters'},
        {'name': 'pinyin'},
        {'name': 'meaning'},
        {'name': 'audio'},
    ],
    templates=[
        anki_sources.gen_template(
            1, ["characters", "meaning"], ["pinyin", "audio"]),
        anki_sources.gen_template(
            2, ["characters", "pinyin", "audio"], ["meaning"]),
        anki_sources.gen_template(
            3, ["pinyin", "audio", "meaning"], ["characters"]),
        anki_sources.gen_template(
            4, ["characters"], ["pinyin", "meaning", "audio"]),
    ],
    css=anki_sources._CSS)

_LISTENING_V2_MODEL = genanki.Model(
    _LISTENING_V2_MODEL_ID,
    _LISTENING_V2_MODEL_NAME,
    fields=[
        {'name': 'audio'},
        {'name': 'meaning'},
        {'name': 'pinyin'},
        {'name': 'characters'},
    ],
    templates=[
        anki_sources.gen_template(
            1, ["audio"], ["characters", "pinyin", "meaning"]),
    ],
    css=anki_sources._CSS)

_RADICALS_V2_MODEL = genanki.Model(
    _RADICALS_V2_MODEL_ID,
    _RADICALS_V2_MODEL_NAME,
    fields=[
        {'name': 'characters'},
        {'name': 'pinyin'},
        {'name': 'meaning'},
        {'name': 'audio'},
    ],
    templates=[
        anki_sources.gen_template(
            1, ["characters", "meaning"], ["pinyin", "audio"]),
        anki_sources.gen_template(
            2, ["characters", "pinyin", "audio"], ["meaning"]),
        anki_sources.gen_template(
            3, ["pinyin", "audio", "meaning"], ["characters"]),
        anki_sources.gen_template(
            4, ["characters"], ["pinyin", "meaning", "audio"]),
    ],
    css=anki_sources._CSS)


class AnkiBuilder():
    def __init__(self,
                 audio_dir: Text,
                 anki_reader: anki_reader_lib.AnkiReader,
                 decomposer: decomposer_lib.Decomposer,
                 pleco_cards: Mapping[Text,
                                      card_lib.Card]):
        self._audio_dir = audio_dir
        self._anki_reader = anki_reader
        self._decomposer = decomposer
        self._pleco_cards = pleco_cards

        self._radicals_v2_deck = genanki.Deck(
            _RADICALS_V2_DECK_ID, _RADICALS_V2_DECK_NAME)
        self._vocab_v2_deck = genanki.Deck(
            _VOCAB_V2_DECK_ID, _VOCAB_V2_DECK_NAME)
        self._listening_v2_deck = genanki.Deck(
            _LISTENING_DECK_ID, _LISTENING_DECK_NAME)

        # derived

    def process(self, headword):
        if headword not in self._pleco_cards:
            raise KeyError(
                f"{headword} not in Pleco cards, cannot create Anki card.")

        added_as_radical = self._process_radical_v2(headword)
        if not added_as_radical:
            self._process_vocab_v2(headword)
            self._process_listening(headword)

    def _process_radical_v2(self, headword):
        # returns True if added as a radical
        if self._anki_reader.vocab_v1_contains(headword):
            return False
        if len(headword) > 1:
            return False
        decomposition = self._decomposer.decompose(headword).decomposition
        if not (decomposition == [] or decomposition == [
                headword] or decomposition == headword):
            return False
        logging.info(f"{headword} and decomposition {decomposition}")
        card_obj = self._pleco_cards[headword]
        card_obj.WriteSoundfile(self._audio_dir)
        self._radicals_v2_deck.add_note(genanki.Note(model=_RADICALS_V2_MODEL,
                                                     fields=[
                                                         card_obj._headword,
                                                         card_obj._pinyin_html,
                                                         card_obj._defn_html,
                                                         card_obj._sound,
                                                     ]))
        return True

    def _process_vocab_v2(self, headword):
        if self._anki_reader.vocab_v1_contains(headword):
            raise KeyError(f"{headword} already exists in vocab_v1")

        # raises a verbose exception if not added for some reason.
        card_type = self._anki_reader.get_type(headword)
        if card_type == anki_reader_lib.CardType.Mature:
            # don't add it if it's already mature.
            raise KeyError(
                f"{headword} cannot be added to vocab_v2, it is already mature.")
        if headword not in self._pleco_cards:
            # can't add it if we don't have a pleco entry.
            raise KeyError(
                f"{headword} cannot be added to vocab_v2, it does not have a Pleco entry.")

        # find components
        components = []
        if len(headword) > 1:
            components = [w for w in headword]
        else:
            try:
                components = self._decomposer.decompose(
                    headword).decomposition[1:] or []
            except ValueError:
                components = []

        if any(self._anki_reader.get_type(c) !=
               anki_reader_lib.CardType.Mature for c in components):
            raise KeyError(
                f"{headword} cannot be added to vocab_v2; it has a subcomponent which is not mature.")

        # logging.info(f"Found a candidate: {hw} is {card_type} and no components {components} are immature")
        card_obj = self._pleco_cards[headword]
        card_obj.WriteSoundfile(self._audio_dir)
        self._vocab_v2_deck.add_note(genanki.Note(model=_VOCAB_MODEL,
                                                  fields=[
                                                      card_obj._headword,
                                                      card_obj._pinyin_html,
                                                      card_obj._defn_html,
                                                      card_obj._sound,
                                                  ]))

    def _process_listening(self, headword):
        if self._anki_reader.listening_v1_contains(headword):
            raise KeyError(f"{headword} already exists in listening_v1")

        if len(headword) == 1:
            # too short, don't make a card in the listening deck.
            raise KeyError(
                f"{headword} cannot be added to listening_v2, it is too short to be identifiable in the listening deck.")

        card_obj = self._pleco_cards[headword]
        card_obj.WriteSoundfile(self._audio_dir)

        self._listening_v2_deck.add_note(
            genanki.Note(
                model=_LISTENING_V2_MODEL,
                fields=[
                    card_obj._sound,
                    card_obj._defn_html,
                    card_obj._pinyin_html,
                    card_obj._headword,
                ]))

    def make_package(self):
        return genanki.Package([
            self._radicals_v2_deck,
            self._vocab_v2_deck,
            self._listening_v2_deck,
        ])
