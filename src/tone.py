from enum import IntEnum
from typing import Text


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
