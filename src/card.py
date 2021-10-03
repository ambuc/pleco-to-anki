from src import xml_extractors
from src import frequency as frequency_lib

from absl import logging
from enum import IntEnum
from typing import Text, List, Tuple, Optional
import os
import re
import subprocess
import xml.etree.ElementTree as ET

_CHARACTER_SPLITTER_RE = re.compile(r"([a-zü]+?[0-9]+?)+?")
_TONE_SPLITTER_RE = re.compile(r"([a-zü]+?)([0-9]+?)")


class Tone(IntEnum):
    FLAT = 1
    RISING = 2
    USHAPED = 3
    FALLING = 4
    NEUTRAL = 5

    @staticmethod
    def parse(s):
        return {
            "1": Tone.FLAT,
            "2": Tone.RISING,
            "3": Tone.USHAPED,
            "4": Tone.FALLING, }.get(s, Tone.NEUTRAL)

    def to_color(self) -> Text:
        return {
            Tone.FLAT: "red",
            Tone.RISING: "green",
            Tone.USHAPED: "blue",
            Tone.FALLING: "purple",
        }.get(self, "grey")

    def apply_to(self, letter: Text) -> Text:
        diacritic = {
            Tone.FLAT: u'\u0304',
            Tone.RISING: u'\u0301',
            Tone.USHAPED: u'\u0306',
            Tone.FALLING: u'\u0300',
        }.get(self, None)
        return letter + diacritic if diacritic else letter


def _make_filename(pinyin: Text) -> Text:
    # filename has the shape: "foo1bar2.flac"
    return re.sub(r'\W+', '', str(pinyin)).lower() + ".flac"


def _match_numbers(defn) -> Text:
    els = []
    matching = 1
    while True:
        i = defn.find(f"{matching} ")
        if i == -1:
            break
        a = i + len(str(matching)) + 1
        j = defn.find(f"{matching+1} ")
        if j == -1:
            els.append(defn[a:])
            break
        els.append(defn[a:j])
        matching += 1
    html = "<ol>"
    for e in els:
        html += "<li>" + e + "</li>"
    html += "</ol>"
    return html


def _make_defn_html(defn) -> Text:
    # match things like "1 foo 2 bar 3 baz"
    if "1 " in defn and "2 " in defn:
        return _match_numbers(defn)
    return defn


def _is_vowel(n):
    return n in frozenset(['a', 'e', 'i', 'o', 'u', 'y', 'ü'])


def _add_diacritic_to_word(syllable: Text, tone: Tone) -> Text:
    """
    Takes a syllable "gao" and a tone "1" and returns the syllable with the
    applied diacritic over its first vowel, if possible.
    """
    try:
        idx = next(i for i, x in enumerate(syllable) if _is_vowel(x))
        return syllable[:idx] + tone.apply_to(
            syllable[idx]) + syllable[idx + 1:]
    except StopIteration:
        return syllable


def _sanitize_pinyin(a: Text) -> Text:
    """Turns a string like "gan1//Bei1" into "gan1bei1"."""
    return re.sub(r'\W+', '', a).lower()


def _to_syllablepairs(s: Text) -> List[Tuple[Text, Tone]]:
    """
    Turns a sanitized string like "bie2ren5" into [("bie",Tone.RISING), ("ren", Tone.NEUTRAL)].
    """
    return [
        (syllable, Tone.parse(tone_string))
        for syllable, tone_string in [
            _TONE_SPLITTER_RE.match(group).groups()
            for group in _CHARACTER_SPLITTER_RE.findall(s)
        ]
    ]


def _pinyin_text_to_html(s: Text) -> Text:
    """
    Turns a string like "bie2ren5" into (green)bié(black)ren, in HTML
    1 = Flat       = Red    = ā
    2 = Rising     = Green  = á
    3 = U-shaped   = Blue   = ǎ
    4 = Descending = Purple = à
    5 = Neutral    = Grey   = a

    """
    output = []
    for (syllable, tone) in _to_syllablepairs(_sanitize_pinyin(s)):
        font = ET.Element('font', attrib={'color': tone.to_color()})
        font.text = _add_diacritic_to_word(syllable, tone)
        span = ET.Element('span')
        span.append(font)
        output.append(str(ET.tostring(span, encoding='unicode')))
    return ' '.join(output)


class Card():
    def __init__(self, headword, pinyin_str, defn):
        self._headword = headword
        self._pinyin_str = pinyin_str
        self._defn = defn
        # derived
        self._filename = _make_filename(self._pinyin_str)
        self._sound = f"[sound:{self._filename}]"
        self._pinyin_html = _pinyin_text_to_html(self._pinyin_str)
        self._defn_html = _make_defn_html(self._defn)

    @staticmethod
    def Build(entry) -> "Card":
        headword = xml_extractors.get_headword(entry)
        pron_numbers = xml_extractors.get_pron_numbers(entry)
        pinyin_str = _sanitize_pinyin(pron_numbers)
        defn = xml_extractors.get_defn(entry)
        return Card(headword, pinyin_str, defn)

    def WriteSoundfile(self,
                       directory_of_anki_collection_dot_media: Text):
        fullpath = os.path.join(
            directory_of_anki_collection_dot_media, self._filename)

        # Render the soundfile only if it does not already exist.
        if os.path.exists(fullpath):
            return

        output = subprocess.run(
            [
                "/usr/bin/say",
                "-v",
                "Ting-Ting",
                self._headword,
                "-o",
                fullpath,
            ], capture_output=True)
        logging.info("%s", output)

    def MakeRow(self):
        return {
            "characters": self._headword,
            "pinyin": self._pinyin_html,
            "meaning": self._defn_html,
            "sound": self._sound,
        }

    def MakeCsvRow(self,
                   fq: frequency_lib.Frequencies):
        row = self.MakeRow()
        return ";".join(
            [
                row["characters"],
                row["pinyin"],
                row["meaning"],
                row["sound"],
                # frequency_str
                str(fq.get_frequency(self._headword)),
            ]
        )

    def MakeCsvRowForListening(self,
                               fq: frequency_lib.Frequencies):
        row = self.MakeRow()
        return ";".join(
            [
                row["sound"],
                row["meaning"],
                row["pinyin"],
                row["characters"],
                # frequency_str
                str(fq.get_frequency(self._headword)),
            ]
        )
