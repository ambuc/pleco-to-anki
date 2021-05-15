from absl import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Text, Dict
import csv
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

_CHARACTER_SPLITTER_RE = re.compile(r"([a-zü]+?[0-9]+?)+?")
_TONE_SPLITTER_RE = re.compile(r"([a-zü]+?)([0-9]+?)")


def _is_cjk(character):
    """Checks whether character is CJK.

    See https://stackoverflow.com/a/37311125.

    Returns:
      a boolean.
    """
    return any([start <= ord(character) <= end for start, end in
                [(4352, 4607), (11904, 42191), (43072, 43135), (44032, 55215),
                 (63744, 64255), (65072, 65103), (65381, 65500),
                 (131072, 196607)]
                ])


def _lens_headword(entry_element: ET.Element):
    for headword_cand in entry_element.iter('headword'):
        if headword_cand.get('charset') == "sc":
            return headword_cand
    raise Exception("No headword found in entry: %s" % str(entry_element))


def _lens_pron(entry: ET.Element) -> ET.Element:
    cand = next(entry.iter("pron"))
    # <pron type="hypy" tones="numbers">_payload_</pron>
    if cand.get('type') == "hypy" and cand.get('tones') == "numbers":
        return cand
    raise Exception("No pronunciationstring could be made from entry: %s" %
                    str(entry))


def _lens_defn(entry):
    defn = entry.find('defn')
    if defn == None:
        return "<no defn>"
    last_english_char = 0
    for char in defn.text:
        if not _is_cjk(char):
            last_english_char += 1
        else:
            break
    return defn.text[:last_english_char].replace(';',
                                                 '.').replace('\t',
                                                              '').replace('\n',
                                                                          '')


def sanitize(a):
    """Turns a string like "gan1//Bei1" into "gan1bei1"."""
    return re.sub(r'\W+', '', a).lower()


def to_syllablepairs(s):
    """
    Turns a sanitized string like "bie2ren5" into [("bie",Tone.RISING), ("ren", Tone.NEUTRAL)].
    """
    return [
        (syllable, Tone.parse(tone_string))
        for syllable, tone_string
        in [
            _TONE_SPLITTER_RE.match(group).groups()
            for group
            in _CHARACTER_SPLITTER_RE.findall(s)
        ]
    ]


class Tone(Enum):
    FLAT = 1
    RISING = 2
    USHAPED = 3
    FALLING = 4
    NEUTRAL = 5

    @staticmethod
    def parse(s):
        if s == "1":
            return Tone.FLAT
        elif s == "2":
            return Tone.RISING
        elif s == "3":
            return Tone.USHAPED
        elif s == "4":
            return Tone.FALLING
        else:
            return Tone.NEUTRAL

    def to_color(self):
        if self == Tone.FLAT:
            return "red"
        elif self == Tone.RISING:
            return "green"
        elif self == Tone.USHAPED:
            return "blue"
        elif self == Tone.FALLING:
            return "purple"
        else:
            return "grey"

    def apply_to(self, letter):
        if self == Tone.FLAT:
            return letter + u'\u0304'
        elif self == Tone.RISING:
            return letter + u'\u0301'
        elif self == Tone.USHAPED:
            return letter + u'\u0306'
        elif self == Tone.FALLING:
            return letter + u'\u0300'
        else:
            return letter


def _is_vowel(n):
    return n in frozenset(['a', 'e', 'i', 'o', 'u', 'y', 'ü'])


def _add_diacritic_to_word(syllable, tone):
    """
    Takes a syllable "gao" and a tone "1" and returns the syllable with the
    applied diacritic over its first vowel, if possible.
    """
    try:
        idx = next(i for i, x in enumerate(syllable) if _is_vowel(x))
        return syllable[:idx] + tone.apply_to(syllable[idx]) + syllable[idx+1:]
    except StopIteration:
        return syllable


def _pinyin_text_to_html(pronunciation_obj):
    """
    Turns a string like "bie2ren5" into (green)bié(black)ren, in HTML
    1 = Flat       = Red    = ā
    2 = Rising     = Green  = á
    3 = U-shaped   = Blue   = ǎ
    4 = Descending = Purple = à
    5 = Neutral    = Grey   = a

    """
    html = ET.Element
    output = []
    for (syllable, tone) in to_syllablepairs(sanitize(pronunciation_obj)):
        font = ET.Element(
            'font', attrib={'color': tone.to_color()})
        font.text = _add_diacritic_to_word(syllable, tone)
        span = ET.Element('span')
        span.append(font)
        output.append(str(ET.tostring(span, encoding='unicode')))
    return ' '.join(output)


def _make_frequencies_dict(csv_path) -> Optional[Dict[Text, float]]:
    """Returns dict from char to float; lower is more common."""
    if csv_path is None:
        return None

    d = {}
    with open(csv_path) as f:
        reader = csv.reader(f)
        # idx, char, count, percentage
        # ['1', '的', '123456', '1.23456']
        for row in reader:
            d[row[1]] = float(row[3])
    return d


@dataclass
class Card:
    pinyin_html: str
    characters: str
    definition: str
    sound: Optional[str] = None
    frequency: Optional[float] = None


class PlecoToAnkiConverter:
    def __init__(self, xml_path, audio_path=None, frequencies_csv_path=None):
        """
        Args:
          xml_path: Path to the Pleco xml output file.
          audio_path: Path to the Anki collection.media folder.
          frequencies_csv_path: Path to the frequencies csv file.
        """
        self._xml_path = xml_path
        self._audio_path = audio_path
        self._frequencies_csv_path = frequencies_csv_path

        self._should_render_audio = (self._audio_path != None)
        self._should_compute_frequency = (self._frequencies_csv_path != None)

        self._frequencies_dict = None
        if self._should_compute_frequency:
            self._frequencies_dict = _make_frequencies_dict(
                frequencies_csv_path)

    def _convert_xml_to_cardobj(self, card: ET.Element) -> Optional[Card]:
        """Returns None on failure."""
        entry_element: ET.Element = card.find('entry')
        assert(entry_element is not None)

        pinyin_element = _lens_pron(entry_element)
        pinyin_text = pinyin_element.text
        pinyin_html = _pinyin_text_to_html(pinyin_text)

        characters_element = _lens_headword(entry_element)
        characters_text = characters_element.text

        definition_text = _lens_defn(entry_element)

        cardobj = Card(pinyin_html=pinyin_html,
                       characters=characters_text,
                       definition=definition_text)

        if self._should_render_audio:
            assert(self._audio_path is not None)
            # filename has the shape: "foo1bar2.flac"
            filename = re.sub(
                r'\W+', '', str(pinyin_element.text)).lower() + ".flac"

            # fullpath has the shape: "~/path/to/foo1bar2.flac"
            fullpath = os.path.join(self._audio_path, filename)

            # Render the soundfile only if it does not already exist.
            if not os.path.exists(fullpath):
                logging.info("%s", subprocess.run(
                    ["/usr/bin/say", "-v", "Ting-Ting",
                        characters_text, "-o", fullpath, ],
                    capture_output=True))

            cardobj.sound = f"[sound:{filename}]"

        if self._should_compute_frequency:
            assert(self._frequencies_dict is not None)
            s = [self._frequencies_dict.get(c, 99999999)
                 for c in characters_text]
            # average
            cardobj.frequency = sum(s) / len(s)

        return cardobj

    def _convert_cardobj_to_csv_line(self, cardobj: Card) -> Text:
        csv_line = []
        csv_line.append(cardobj.pinyin_html)
        csv_line.append(cardobj.characters)
        csv_line.append(cardobj.definition)
        if cardobj.sound is not None:
            csv_line.append(cardobj.sound)
        if cardobj.frequency is not None:
            csv_line.append(str(cardobj.frequency))
        return csv_line

    def return_csv(self) -> Text:
        et_root = ET.parse(self._xml_path).getroot()
        result = []
        for cardxml in et_root.find('cards'):
            cardobj = self._convert_xml_to_cardobj(cardxml)
            if cardobj is None:
                continue
            csv_line = self._convert_cardobj_to_csv_line(cardobj)
            result.append(';'.join(csv_line))
        return "\n".join(result)
