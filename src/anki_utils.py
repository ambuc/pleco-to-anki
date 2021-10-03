from absl import logging
from anki.collection import Collection
from enum import IntEnum
from typing import Text, Mapping, List
import genanki

from src import card as card_lib
from src import decomposer as decomposer_lib

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

_SCRIPT = """
<script>
var fonts = ['nbl', 'nbo', 'nli', 'nme', 'nre', 'nth', 'rbl', 'rbo', 'rex', 'rli', 'rme', 'rre', 'rse'];
document.getElementById('characters').style.fontFamily = fonts[Math.floor(
    Math.random() * fonts.length)];
</script>
"""

_CSS = """
@font-face { font-family: 'nbl'; src: url("_NotoSansSC-Black.otf"); }
@font-face { font-family: 'nbo'; src: url("_NotoSansSC-Bold.otf"); }
@font-face { font-family: 'nli'; src: url("_NotoSansSC-Light.otf"); }
@font-face { font-family: 'nme'; src: url("_NotoSansSC-Medium.otf"); }
@font-face { font-family: 'nre'; src: url("_NotoSansSC-Regular.otf"); }
@font-face { font-family: 'nth'; src: url("_NotoSansSC-Thin.otf"); }
@font-face { font-family: 'rbl'; src: url("_NotoSerifSC-Black.otf"); }
@font-face { font-family: 'rbo'; src: url("_NotoSerifSC-Bold.otf"); }
@font-face { font-family: 'rex'; src: url("_NotoSerifSC-ExtraLight.otf"); }
@font-face { font-family: 'rli'; src: url("_NotoSerifSC-Light.otf"); }
@font-face { font-family: 'rme'; src: url("_NotoSerifSC-Medium.otf"); }
@font-face { font-family: 'rre'; src: url("_NotoSerifSC-Regular.otf"); }
@font-face { font-family: 'rse'; src: url("_NotoSerifSC-SemiBold.otf"); }

.card {
 font-family: serif;
 text-align: center;
}

#meaning {
  font-size: 2em;
  display: inline-block;
}
#characters {
  font-size: 5em;
}
#pinyin {
  font-size: 2em;
  font-weight: 900;
}

.night_mode font[color="blue"] {
   color: blue;
}
.night_mode font[color="purple"] {
   color: purple;
}
.night_mode font[color="red"] {
   color: red;
}
.night_mode font[color="green"] {
   color: green;
}
.night_mode font[color="grey"] {
   color: grey;
}
"""


def _to_span_html(fieldname: Text):
    return f"<span id='{fieldname}'>{{{{{fieldname}}}}}</span>"


def gen_template(idx, map_from: List[Text], map_to: List[Text]):
    name = f"Card {idx} {'+'.join(map_from)}=>{'+'.join(map_to)}"
    qfmt = "<br>".join(_to_span_html(f) for f in map_from)
    if "characters" in map_from:
        qfmt += _SCRIPT
    afmt = "{{FrontSide}} <hr>"

    afmt += "<br>".join(_to_span_html(f) for f in map_to)

    return {
        'name': name,
        'qfmt': qfmt,
        'afmt': afmt,
    }


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
        gen_template(
            1, ["characters", "meaning"], ["pinyin", "audio"]),
        gen_template(
            2, ["characters", "pinyin", "audio"], ["meaning"]),
        gen_template(
            3, ["pinyin", "audio", "meaning"], ["characters"]),
        gen_template(
            4, ["characters"], ["pinyin", "meaning", "audio"]),
    ],
    css=_CSS)

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
        gen_template(
            1, ["audio"], ["characters", "pinyin", "meaning"]),
    ],
    css=_CSS)

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
        gen_template(
            1, ["characters", "meaning"], ["pinyin", "audio"]),
        gen_template(
            2, ["characters", "pinyin", "audio"], ["meaning"]),
        gen_template(
            3, ["pinyin", "audio", "meaning"], ["characters"]),
        gen_template(
            4, ["characters"], ["pinyin", "meaning", "audio"]),
    ],
    css=_CSS)


class CardType(IntEnum):
    New = 0
    Learning = 1
    Mature = 2
    Absent = 3
    Other = 4

    @staticmethod
    def parse(s):
        return {
            0: CardType.New,
            1: CardType.Learning,
            2: CardType.Mature,
        }.get(s, CardType.Other)


class AnkiReader():
    def __init__(self, collection_path: Text):
        self._collection = Collection(collection_path)

    def listening_v1_contains(self, headword: Text) -> bool:
        # returns True if the headword already exists in `deck:listening`
        return len(self._collection.find_notes(
            f"deck:zw::listening_v1 characters:{headword}")) != 0

    def vocab_v1_contains(self, headword: Text) -> bool:
        # returns True if the headword already exists in `deck:zw::vocab`
        return len(self._collection.find_notes(
            f"deck:zw::vocab_v1 characters:{headword}")) != 0

    def get_type(self, headword: Text) -> CardType:
        try:
            # # This is 0 for learning cards,
            # # 1 for review cards,
            # # 2 for relearn cards, and "mature"
            # # 3 for early "cram" cards (cards being studied in a filtered deck when they are not due).
            note_ids = self._collection.find_notes(f"characters:{headword}")
            note = self._collection.get_note(note_ids[0])
            subtypes = [self._collection.get_card(
                card_id).type for card_id in note.card_ids()]
            int_val = min(subtypes)
            return CardType.parse(int_val)
        except IndexError:
            return CardType.Absent


class AnkiBuilder():
    def __init__(self,
                 audio_dir: Text,
                 anki_reader: AnkiReader,
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
        if card_type == CardType.Mature:
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
               CardType.Mature for c in components):
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
