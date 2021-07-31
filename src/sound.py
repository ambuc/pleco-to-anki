from absl import logging
from typing import Text
import os
import re
import subprocess


def make_filename(pinyin: Text) -> Text:
    # filename has the shape: "foo1bar2.flac"
    return re.sub(r'\W+', '', str(pinyin)).lower() + ".flac"


def make_fullpath(dir_path: Text, filename: Text) -> Text:
    # fullpath has the shape: "~/path/to/foo1bar2.flac"
    return os.path.join(dir_path, filename)


def write_soundfile(fullpath: Text, characters: Text):
    # Render the soundfile only if it does not already exist.
    if os.path.exists(fullpath):
        return

    output = subprocess.run(
        [
            "/usr/bin/say",
            "-v",
            "Ting-Ting",
            characters,
            "-o",
            fullpath,
        ], capture_output=True)
    logging.info("%s", output)
