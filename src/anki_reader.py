from anki.collection import Collection

from typing import Text


class AnkiReader():
    def __init__(self, collection_path: Text):
        self._collection = Collection(collection_path)

    def get_type(self, headword: Text):
        # # This is 0 for learning cards,
        # # 1 for review cards,
        # # 2 for relearn cards, and "mature"
        # # 3 for early "cram" cards (cards being studied in a filtered deck when they are not due).
        note_ids = self._collection.find_notes(f"characters:{headword}")
        note = self._collection.get_note(note_ids[0])
        return min(self._collection.get_card(
            card_id).type for card_id in note.card_ids())
