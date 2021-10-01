from src import xml_extractors
from src import frequency
from src import defn_extractor
from src import pinyin
from src import sound

from typing import Optional, Text


class Card():
    def __init__(self, headword, pinyin_str, defn):
        self._headword = headword
        self._pinyin_str = pinyin_str
        self._defn = defn
        # derived
        self._filename = sound.make_filename(self._pinyin_str)
        self._pinyin_html = pinyin.pinyin_text_to_html(self._pinyin_str)
        self._defn_html = defn_extractor.make_defn_html(self._defn)

    @staticmethod
    def Build(entry) -> "Card":
        headword = xml_extractors.get_headword(entry)
        pron_numbers = xml_extractors.get_pron_numbers(entry)
        pinyin_str = pinyin.sanitize(pron_numbers)
        defn = xml_extractors.get_defn(entry)
        return Card(headword, pinyin_str, defn)

    def WriteSoundfile(self,
                       directory_of_anki_collection_dot_media: Text):
        fullpath = sound.make_fullpath(
            directory_of_anki_collection_dot_media, self._filename)

        sound.write_soundfile(fullpath, self._headword)

    def MakeCsvRow(self,
                   directory_of_anki_collection_dot_media: Text,
                   frequencies_dict):
        return ";".join(
            [
                self._headword,

                # pinyin_html
                self._pinyin_html,

                # defn html
                self._defn_html,

                # soundstring
                f"[sound:{self._filename}]",

                # frequency_str
                str(frequency.get_frequency(
                    frequencies_dict, self._headword)),
            ]
        )

    def MakeCsvRowForListening(self,
                               directory_of_anki_collection_dot_media: Text,
                               frequencies_dict):
        return ";".join(
            [
                # audiofile
                f"[sound:{self._filename}]",
                # meaning
                self._defn_html,
                # pinyin
                self._pinyin_html,
                # characters
                self._headword,
                # frequency_str
                str(frequency.get_frequency(
                    frequencies_dict, self._headword)),
            ]
        )
