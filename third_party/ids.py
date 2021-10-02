import os

PATH_TO_IDS_TXT = os.path.join(os.sep,
                               *os.path.split(__file__)[0].split('/')[:-1],
                               "third_party",
                               "IDS.txt")
