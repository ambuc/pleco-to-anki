from anki.collection import Collection

from absl import logging
from typing import Text
from enum import IntEnum


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
