import csv
import subprocess
import re
from enum import Enum
import sys
import os
import xml.etree.ElementTree as ET
from absl import logging

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


def make_frequencies_dict(csv_path):
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
    

def process_path(path, audio_path, frequencies_csv_path):
    frequencies_dict = make_frequencies_dict(frequencies_csv_path)

    result = []
    for card in ET.parse(path).getroot().find('cards'):
        entry = card.find('entry')
        pronunciation_obj = _extract_pronunicationstring(entry)

        characters = _extract_headword(entry).text

        in_progress = [ to_html(pronunciation_obj.text), characters, _extract_short_definition(entry),  ]

        if audio_path is not None:
            # "foo1bar2.flac"
            partial_path = re.sub(
                r'\W+', '', str(pronunciation_obj.text)).lower() + ".flac"
            # "~/path/to/foo1bar2.flac"
            full_path = os.path.join(audio_path, partial_path)
            if not os.path.exists(full_path):
              cmd = ["/usr/bin/say", "-v", "Ting-Ting", characters,
                     "-o", full_path]
              logging.info("%s", subprocess.run(cmd, capture_output=True))
            in_progress.append(f"[sound:{partial_path}]")

        if frequencies_dict is not None:
            s = [ frequencies_dict.get(c, 99999999) for c in characters ]
            # average
            in_progress.append(str(sum(s) / len(s)))

        result.append(";".join(in_progress))

    return '\n'.join(result)
