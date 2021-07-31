from src.tone import Tone

import xml.etree.ElementTree as ET
from typing import Text, List, Tuple
import re

_CHARACTER_SPLITTER_RE = re.compile(r"([a-zü]+?[0-9]+?)+?")
_TONE_SPLITTER_RE = re.compile(r"([a-zü]+?)([0-9]+?)")


def is_vowel(n):
    return n in frozenset(['a', 'e', 'i', 'o', 'u', 'y', 'ü'])


def add_diacritic_to_word(syllable: Text, tone: Tone) -> Text:
    """
    Takes a syllable "gao" and a tone "1" and returns the syllable with the
    applied diacritic over its first vowel, if possible.
    """
    try:
        idx = next(i for i, x in enumerate(syllable) if is_vowel(x))
        return syllable[:idx] + tone.apply_to(
            syllable[idx]) + syllable[idx + 1:]
    except StopIteration:
        return syllable


def sanitize(a: Text) -> Text:
    """Turns a string like "gan1//Bei1" into "gan1bei1"."""
    return re.sub(r'\W+', '', a).lower()


def to_syllablepairs(s: Text) -> List[Tuple[Text, Tone]]:
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

def pinyin_text_to_html(s: Text) -> Text:
    """
    Turns a string like "bie2ren5" into (green)bié(black)ren, in HTML
    1 = Flat       = Red    = ā
    2 = Rising     = Green  = á
    3 = U-shaped   = Blue   = ǎ
    4 = Descending = Purple = à
    5 = Neutral    = Grey   = a

    """
    output = []
    for (syllable, tone) in to_syllablepairs(sanitize(s)):
        font = ET.Element('font', attrib={'color': tone.to_color()})
        font.text = add_diacritic_to_word(syllable, tone)
        span = ET.Element('span')
        span.append(font)
        output.append(str(ET.tostring(span, encoding='unicode')))
    return ' '.join(output)