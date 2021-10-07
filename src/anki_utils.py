import networkx as nx
from anki.collection import Collection
from absl import logging
from enum import Enum, auto
from typing import Text, Mapping, List
import genanki

from src import card as card_lib
from src import categorizer as categorizer_lib
from src import decomposer as decomposer_lib
from src import hsk_utils as hsk_utils_lib


_SCRIPT = """
<script>
var fonts = ['nbl', 'nbo', 'nli', 'nme', 'nre', 'nth', 'rbl', 'rbo', 'rex', 'rli', 'rme', 'rre', 'rse'];
document.getElementById('characters').style.fontFamily = fonts[Math.floor(Math.random() * fonts.length)];
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

.card { font-family: serif; text-align: center; }
#meaning { font-size: 2em; display: inline-block; }
#characters { font-size: 5em; }
#pinyin { font-size: 2em; font-weight: 900; }
.night_mode font[color="blue"  ] { color: blue;   }
.night_mode font[color="purple"] { color: purple; }
.night_mode font[color="red"   ] { color: red;    }
.night_mode font[color="green" ] { color: green;  }
.night_mode font[color="grey"  ] { color: grey;   }
"""


def _to_span_html(fieldname: Text):
    return f"<span id='{fieldname}'>{{{{{fieldname}}}}}</span>"


def _gen_template(idx, map_from: List[Text], map_to: List[Text]):
    name = f"Card {idx} {'+'.join(map_from)}=>{'+'.join(map_to)}"
    qfmt = "<br>".join(_to_span_html(f) for f in map_from)
    if "characters" in map_from:
        qfmt += _SCRIPT
    afmt = "{{FrontSide}} <hr>" + "<br>".join(_to_span_html(f) for f in map_to)
    return {
        'name': name,
        'qfmt': qfmt,
        'afmt': afmt,
    }


_VOCAB_MODEL = genanki.Model(
    12345,
    "model_zw_vocab_v2",
    fields=[
        {'name': 'characters'},
        {'name': 'pinyin'},
        {'name': 'meaning'},
        {'name': 'audio'},
    ],
    templates=[
        _gen_template(
            1, ["characters", "meaning"], ["pinyin", "audio"]),
        _gen_template(
            2, ["characters", "pinyin", "audio"], ["meaning"]),
        _gen_template(
            3, ["pinyin", "audio", "meaning"], ["characters"]),
        _gen_template(
            4, ["characters"], ["pinyin", "meaning", "audio"]),
    ],
    css=_CSS)

_LISTENING_V2_MODEL = genanki.Model(
    12345,
    "model_zw_listening_v2",
    fields=[
        {'name': 'audio'},
        {'name': 'meaning'},
        {'name': 'pinyin'},
        {'name': 'characters'},
    ],
    templates=[
        _gen_template(
            1, ["audio"], ["characters", "pinyin", "meaning"]),
    ],
    css=_CSS)


class CardType(Enum):
    New = auto()
    Learning = auto()
    Mature = auto()
    Absent = auto()
    Other = auto()

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
                 categorizer: categorizer_lib.Categorizer,
                 pleco_cards: Mapping[Text,
                                      card_lib.Card]):
        self._audio_dir = audio_dir
        self._categorizer = categorizer
        self._pleco_cards = pleco_cards

        # TODO Rather than write apkg, why not reach into anki db and create
        # cards / set tags?
        self._decks = {e: genanki.Deck(123, str(e))
                       for e in categorizer_lib.Deck}

    def process(self, headword):
        if headword not in self._pleco_cards:
            return False
        card_obj = self._pleco_cards[headword]
        deck = self._categorizer.sort_into_deck(headword)
        if not deck:
            return False
        logging.info(f"{headword}, {str(deck)}")
        card_obj.WriteSoundfile(self._audio_dir)
        deck = self._decks[deck]
        deck.add_note(
            genanki.Note(
                model=_VOCAB_MODEL,
                fields=[
                    card_obj._headword,
                    card_obj._pinyin_html,
                    card_obj._defn_html,
                    card_obj._sound,
                ]))
        if len(headword) > 1:
            deck.add_note(genanki.Note(
                model=_LISTENING_V2_MODEL, fields=[
                    card_obj._sound,
                    card_obj._defn_html,
                    card_obj._pinyin_html,
                    card_obj._headword,
                ]))

        return True

    def make_package(self):
        for deck_enum, deck_obj in self._decks.items():
            logging.info(f"{deck_enum}:  {len(deck_obj.notes)}")
        return genanki.Package(self._decks.values())
