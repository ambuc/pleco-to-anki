import re
from enum import Enum
import sys
import xml.etree.ElementTree as ET

_CHARACTER_SPLITTER_RE = re.compile(r"([a-zü]+?[0-9]+?)+?")
_TONE_SPLITTER_RE = re.compile(r"([a-zü]+?)([0-9]+?)")


def is_cjk(character):
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


def _extract_headword(entry):
    for headword_cand in entry.iter('headword'):
        if headword_cand.get('charset') == "sc":
            return headword_cand
    raise Exception("No headword found in entry: %s" % str(entry))


def _extract_pronunicationstring(entry):
    for cand in entry.iter('pron'):
        if cand.get('type') == "hypy" and cand.get('tones') == "numbers":
            return cand
    raise Exception("No pronunciationstring could be made from entry: %s" %
                    str(entry))


def _extract_short_definition(entry):
    defn = entry.find('defn')
    last_english_char = 0
    for char in defn.text:
        if not is_cjk(char):
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


def to_html(pronunciation_obj):
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


def process_path(path):
    result = []
    for card in ET.parse(path).getroot().find('cards'):
        entry = card.find('entry')
        pronunciation_obj = _extract_pronunicationstring(entry)
        result.append("%s;%s;%s" % (to_html(pronunciation_obj.text),
                                    _extract_headword(entry).text,
                                    _extract_short_definition(entry)))
    return '\n'.join(result)