# by James Buckland
# Nov 2020

import unittest
import os

import p2a_lib


def strip_white_space(str):
    return str.replace(" ", "").replace("\t", "").replace("\n", "")


class P2aLibTest(unittest.TestCase):

    def test_run(self):
        with open("testdata/output.csv", "r") as f:
            self.assertEqual(strip_white_space(p2a_lib.process_path(
                "testdata/input.xml")), strip_white_space(f.read()))


if __name__ == '__main__':
    unittest.main()
