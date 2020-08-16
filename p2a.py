#! /usr/bin/python3

# by James Buckland
# Aug 2020

import xml.etree.ElementTree as ET
import re

def is_cjk(character):
    """"
    Checks whether character is CJK.
    https://stackoverflow.com/a/37311125
    """
    return any([start <= ord(character) <= end for start, end in 
                [(4352, 4607), (11904, 42191), (43072, 43135), (44032, 55215), 
                 (63744, 64255), (65072, 65103), (65381, 65500), 
                 (131072, 196607)]
                ])

def extract_entry(card):
    """
    Extracts the entry or throws.
    :param card: The XML card object.
    :return: text
    """
    entry = card.find('entry')
    assert entry is not None
    return entry

def extract_headword(entry):
    headword = None
    for headword_cand in entry.iter('headword'):
        if headword_cand.get('charset') == "sc":
            headword = headword_cand
            break
    assert headword is not None
    return headword

def extract_pron(entry):
    pron = None
    for pron_cand in entry.iter('pron'):
        if pron_cand.get('type') == "hypy" and pron_cand.get('tones') == "numbers":
            pron = pron_cand
            break
    assert pron is not None
    return pron

def extract_short_defn(entry):
    defn = entry.find('defn')
    assert defn is not None

    last_english_char = 0
    for char in defn.text:
      if not is_cjk(char):
        last_english_char += 1
      else:
        break
    return defn.text[:last_english_char]

character_splitter = re.compile(r"([a-zü]+?[0-9]+?)+?") 
tone_splitter = re.compile(r"([a-zü]+?)([0-9]+?)") 

def sanitize_pron(a):
    """
    Turns a string like "gan1//Bei1" into "gan1bei1".
    """
    # Can have non-alphanumeric stuff. Strip it.
    a = re.sub(r'\W+','', a)
    # Can have capitals. Lowercase it.
    a = a.lower()
    return a

def pron_to_list(s):
    """
    Turns a sanitized string like "bie2ren5" into [("bie","2"), ("ren", "5")].
    """
    return [tone_splitter.match(group).groups() for group in
            character_splitter.findall(s)]

def tone_to_color(s):
    """
    Takes a string like "1" or "5" and returns a color like "red" or "grey".
    """
    if s == "1":
        # flat
        return "red"
    elif s == "2":
        # rising
        return "green"
    elif s == "3":
        # u-shaped
        return "blue"
    elif s == "4":
        # falling
        return "purple"
    else:
        return "grey"

def index_of_first_vowel(s):
    """
    Returns the index of the first vowel (a,e,i,o,u,y,ü), or None.
    """
    for idx, char in enumerate(s):
        if char in ['a','e','i','o','u','y','ü']:
            return idx
    return None

def add_diacritic_to_letter(letter, tone):
    """
    Takes a letter 'a' and a tone '1' and returns the letter with the applied
    diacritic.
    """
    if tone == "1":
        # flat
        return letter + u'\u0304'
    elif tone == "2":
        # rising
        return letter + u'\u0301'
    elif tone == "3":
        # u-shaped
        return letter + u'\u0306'
    elif tone == "4":
        # falling
        return letter + u'\u0300'
    else:
        return letter

def add_diacritic_to_word(syllable, tone):
    """
    Takes a syllable "gao" and a tone "1" and returns the syllable with the
    applied diacritic over its first vowel, if possible.
    """
    idx = index_of_first_vowel(syllable)
    if idx is None:
        return syllable
    return syllable[:idx] + add_diacritic_to_letter(syllable[idx], tone) + syllable[idx+1:]

def pron_to_html(pron):
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
    for (syllable, tone) in pron_to_list(sanitize_pron(pron)):
        font = ET.Element('font', attrib={'color': tone_to_color(tone)})
        font.text = add_diacritic_to_word(syllable, tone)
        span = ET.Element('span')
        span.append(font)
        output.append(str(ET.tostring(span, encoding='unicode')))
    return ' '.join(output)

for card in ET.parse("example.xml").getroot().find('cards'):
    entry = extract_entry(card)
    headword = extract_headword(entry)
    pron = extract_pron(entry)
    pron_to_html(pron.text)
    short_defn = extract_short_defn(entry)
    print("%s;%s;%s" % (headword.text, pron_to_html(pron.text), short_defn))



