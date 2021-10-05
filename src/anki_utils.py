import networkx as nx
from anki.collection import Collection
from absl import logging
from enum import Enum, auto
from typing import Text, Mapping, List
import genanki

from src import card as card_lib
from src import decomposer as decomposer_lib
from src import hsk_utils as hsk_utils_lib


class Deck(Enum):
    UNKNOWN = auto()
    VocabV1 = auto()
    VocabV2 = auto()
    ListeningV1 = auto()
    ListeningV2 = auto()
    RadicalsV2 = auto()
    HSK_1_V1 = auto()
    HSK_2_V1 = auto()
    HSK_3_V1 = auto()
    HSK_4_V1 = auto()
    HSK_5_V1 = auto()
    HSK_6_V1 = auto()
    HSK_1_MINUS_V1 = auto()
    HSK_2_MINUS_V1 = auto()
    HSK_3_MINUS_V1 = auto()
    HSK_4_MINUS_V1 = auto()
    HSK_5_MINUS_V1 = auto()
    HSK_6_MINUS_V1 = auto()
    HSK_1_PLUS_V1 = auto()
    HSK_2_PLUS_V1 = auto()
    HSK_3_PLUS_V1 = auto()
    HSK_4_PLUS_V1 = auto()
    HSK_5_PLUS_V1 = auto()
    HSK_6_PLUS_V1 = auto()
    OTHER_V1 = auto()


def _GetDeckId(deck):
    return {Deck.VocabV1: 20000,
            Deck.VocabV2: 20001,
            Deck.ListeningV1: 20010,
            Deck.ListeningV2: 20012,
            Deck.RadicalsV2: 20003, }.get(deck, 12345)


def _GetDeckName(deck):
    return {Deck.VocabV1: "zw::vocab_v1",
            Deck.VocabV2: "zw::vocab_v2",
            Deck.ListeningV1: "zw::listening_v1",
            Deck.ListeningV2: "zw::listening_v2",
            Deck.RadicalsV2: "zw::radicals_v2",
            Deck.HSK_1_V1: "hsk::1",
            Deck.HSK_2_V1: "hsk::2",
            Deck.HSK_3_V1: "hsk::3",
            Deck.HSK_4_V1: "hsk::4",
            Deck.HSK_5_V1: "hsk::5",
            Deck.HSK_6_V1: "hsk::6",
            Deck.HSK_1_MINUS_V1: "hsk::1m",
            Deck.HSK_2_MINUS_V1: "hsk::2m",
            Deck.HSK_3_MINUS_V1: "hsk::3m",
            Deck.HSK_4_MINUS_V1: "hsk::4m",
            Deck.HSK_5_MINUS_V1: "hsk::5m",
            Deck.HSK_6_MINUS_V1: "hsk::6m",
            Deck.HSK_1_PLUS_V1: "hsk::1p",
            Deck.HSK_2_PLUS_V1: "hsk::2p",
            Deck.HSK_3_PLUS_V1: "hsk::3p",
            Deck.HSK_4_PLUS_V1: "hsk::4p",
            Deck.HSK_5_PLUS_V1: "hsk::5p",
            Deck.HSK_6_PLUS_V1: "hsk::1p",
            }.get(deck, "other")


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
                 anki_reader: AnkiReader,
                 decomposer: decomposer_lib.Decomposer,
                 hsk_reader: hsk_utils_lib.HskReader,
                 pleco_cards: Mapping[Text,
                                      card_lib.Card]):
        self._audio_dir = audio_dir
        self._anki_reader = anki_reader
        self._decomposer = decomposer
        self._hsk_reader = hsk_reader
        self._pleco_cards = pleco_cards

        self._decks = {
            e: genanki.Deck(_GetDeckId(e), _GetDeckName(e))
            for e in [
                Deck.HSK_1_V1,
                Deck.HSK_2_V1,
                Deck.HSK_3_V1,
                Deck.HSK_4_V1,
                Deck.HSK_5_V1,
                Deck.HSK_6_V1,
                Deck.HSK_1_MINUS_V1,
                Deck.HSK_2_MINUS_V1,
                Deck.HSK_3_MINUS_V1,
                Deck.HSK_4_MINUS_V1,
                Deck.HSK_5_MINUS_V1,
                Deck.HSK_6_MINUS_V1,
                Deck.HSK_1_PLUS_V1,
                Deck.HSK_2_PLUS_V1,
                Deck.HSK_3_PLUS_V1,
                Deck.HSK_4_PLUS_V1,
                Deck.HSK_5_PLUS_V1,
                Deck.HSK_6_PLUS_V1,
                Deck.OTHER_V1,
            ]
        }

    def process(self, headword):
        deck = self._sort_into_deck(headword)
        if deck:
            self._add_to_deck(headword, deck)
        return deck

    def _sort_into_deck(self, headword) -> Deck:
        if headword not in self._pleco_cards:
            logging.error(
                f"{headword} not in Pleco cards, cannot create Anki card.")
            return None

        hsk_level = self._hsk_reader.GetHskLevel(headword)
        if hsk_level is not None:
            deck = [Deck.HSK_1_V1,
                    Deck.HSK_2_V1,
                    Deck.HSK_3_V1,
                    Deck.HSK_4_V1,
                    Deck.HSK_5_V1,
                    Deck.HSK_6_V1,
                    ][hsk_level - 1]
            return deck

        G = self._decomposer._graph

        if len(headword) == 1:
            # If our headword is a single character,
            for deck, checkset in [
                # For every HSK tier,
                (Deck.HSK_1_MINUS_V1, self._hsk_reader.GetHskAndBelow(1)),
                (Deck.HSK_2_MINUS_V1, self._hsk_reader.GetHskAndBelow(2)),
                (Deck.HSK_3_MINUS_V1, self._hsk_reader.GetHskAndBelow(3)),
                (Deck.HSK_4_MINUS_V1, self._hsk_reader.GetHskAndBelow(4)),
                (Deck.HSK_5_MINUS_V1, self._hsk_reader.GetHskAndBelow(5)),
                (Deck.HSK_6_MINUS_V1, self._hsk_reader.GetHskAndBelow(6)),
            ]:
                if headword in set(c for w in checkset for c in w):
                    return deck

                try:
                    # If the headword is a part of any whole in our checkset up
                    # to and including HSK N
                    next(
                        nx.algorithms.simple_paths.all_simple_paths(
                            G, headword, checkset | set(
                                c for w in checkset for c in w)))
                    return deck
                except nx.NodeNotFound as e:
                    logging.error(str(e))
                    continue
                except StopIteration:
                    continue
        # else if our headword is many characters,
        hsk_levels = [self._hsk_reader.GetHskLevel(c) for c in headword]
        hsk_levels = [h for h in hsk_levels if h is not None]
        if hsk_levels == []:
            return Deck.OTHER_V1
        hsk_level = max(hsk_levels)
        deck = [Deck.HSK_1_PLUS_V1,
                Deck.HSK_2_PLUS_V1,
                Deck.HSK_3_PLUS_V1,
                Deck.HSK_4_PLUS_V1,
                Deck.HSK_5_PLUS_V1,
                Deck.HSK_6_PLUS_V1,
                ][hsk_level - 1]
        return deck

    def _add_to_deck(self, headword, deck_enum):
        card_obj = self._pleco_cards[headword]
        card_obj.WriteSoundfile(self._audio_dir)
        deck = self._decks[deck_enum]
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

    def make_package(self):
        return genanki.Package(self._decks.values())
