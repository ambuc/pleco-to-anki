from anki.collection import Collection
from enum import IntEnum
from typing import Text, Mapping, List
import genanki

from src import card as card_lib
from src import decomposer as decomposer_lib


class Deck(IntEnum):
    UNKNOWN = 0
    VocabV1 = 1
    VocabV2 = 2
    ListeningV1 = 3
    ListeningV2 = 4
    RadicalsV2 = 5


def _GetDeckId(deck):
    return {Deck.VocabV1: 20000,
            Deck.VocabV2: 20001,
            Deck.ListeningV1: 20010,
            Deck.ListeningV2: 20012,
            Deck.RadicalsV2: 20003, }.get(deck)


def _GetDeckName(deck):
    return {Deck.VocabV1: "zw::vocab_v1",
            Deck.VocabV2: "zw::vocab_v2",
            Deck.ListeningV1: "zw::listening_v1",
            Deck.ListeningV2: "zw::listening_v2",
            Deck.RadicalsV2: "zw::radicals_v2", }.get(deck)


def _GetModelId(deck):
    return {Deck.VocabV1: 10000,
            Deck.VocabV2: 10001,
            Deck.ListeningV1: 10010,
            Deck.ListeningV2: 10002,
            Deck.RadicalsV2: 10003, }.get(deck)


def _GetModelName(deck):
    return {Deck.VocabV1: "model_zw_vocab_v1",
            Deck.VocabV2: "model_zw_vocab_v2",
            Deck.ListeningV1: "model_zw_listening_v1",
            Deck.ListeningV2: "model_zw_listening_v2",
            Deck.RadicalsV2: "model_zw_radicals_v2", }.get(deck)


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
    _GetModelId(Deck.VocabV2),
    _GetModelName(Deck.VocabV2),
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
    _GetModelId(Deck.ListeningV2),
    _GetModelName(Deck.ListeningV2),
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

_RADICALS_V2_MODEL = genanki.Model(
    _GetModelId(Deck.RadicalsV2),
    _GetModelName(Deck.RadicalsV2),
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

        self._decks = {
            e: genanki.Deck(_GetDeckId(e), _GetDeckName(e))
            for e in [Deck.RadicalsV2, Deck.VocabV2, Deck.ListeningV2]
        }

    def process(self, headword):
        if headword not in self._pleco_cards:
            raise KeyError(
                f"{headword} not in Pleco cards, cannot create Anki card.")

        if not self._add_to_radicalv2_deck(headword):
            self._add_to_vocabv2_deck(headword)
            self._add_to_listeningv2_deck(headword)

    def _add_to_radicalv2_deck(self, headword):
        # returns True if added as a radical
        if self._anki_reader.vocab_v1_contains(headword):
            return False
        if len(headword) > 1:
            return False
        decomposition = self._decomposer.decompose(headword).decomposition
        if not (decomposition == [] or decomposition == [
                headword] or decomposition == headword):
            return False
        card_obj = self._pleco_cards[headword]
        card_obj.WriteSoundfile(self._audio_dir)
        self._decks[Deck.RadicalsV2].add_note(genanki.Note(model=_RADICALS_V2_MODEL,
                                                           fields=[
                                                               card_obj._headword,
                                                               card_obj._pinyin_html,
                                                               card_obj._defn_html,
                                                               card_obj._sound,
                                                           ]))
        return True

    def _add_to_vocabv2_deck(self, headword) -> bool:
        if self._anki_reader.vocab_v1_contains(headword):
            return False

        # raises a verbose exception if not added for some reason.
        card_type = self._anki_reader.get_type(headword)
        if card_type == CardType.Mature:
            # don't add it if it's already mature.
            return False
        if headword not in self._pleco_cards:
            # can't add it if we don't have a pleco entry.
            return False

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
            return False

        card_obj = self._pleco_cards[headword]
        card_obj.WriteSoundfile(self._audio_dir)
        self._decks[Deck.VocabV2].add_note(genanki.Note(model=_VOCAB_MODEL,
                                                        fields=[
                                                            card_obj._headword,
                                                            card_obj._pinyin_html,
                                                            card_obj._defn_html,
                                                            card_obj._sound,
                                                        ]))
        return True

    def _add_to_listeningv2_deck(self, headword) -> bool:
        if self._anki_reader.listening_v1_contains(headword):
            return False

        if len(headword) == 1:
            # too short, don't make a card in the listening deck.
            return False

        card_obj = self._pleco_cards[headword]
        card_obj.WriteSoundfile(self._audio_dir)
        self._decks[Deck.ListeningV2].add_note(
            genanki.Note(
                model=_LISTENING_V2_MODEL,
                fields=[
                    card_obj._sound,
                    card_obj._defn_html,
                    card_obj._pinyin_html,
                    card_obj._headword,
                ]))
        return True

    def make_package(self):
        return genanki.Package(self._decks.values())
