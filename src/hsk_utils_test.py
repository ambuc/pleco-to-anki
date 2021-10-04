from src import hsk_utils as hsk_utils_lib

import tempfile
from unittest.mock import MagicMock, call
from absl.testing import absltest


_R = hsk_utils_lib.HskReader()


class HskUtilsTest(absltest.TestCase):

    def testHas(self):
        self.assertTrue(_R.Has("我"))
        self.assertFalse(_R.Has(""))
        self.assertFalse(_R.Has("a"))
        self.assertFalse(_R.Has("."))
        self.assertFalse(_R.Has("[]"))

    def testInHsk(self):
        self.assertTrue(_R.InHsk(1, "我"))
        self.assertFalse(_R.InHsk(2, "我"))
        self.assertFalse(_R.InHsk(3, "我"))
        self.assertFalse(_R.InHsk(4, "我"))
        self.assertFalse(_R.InHsk(5, "我"))
        self.assertFalse(_R.InHsk(6, "我"))

        self.assertTrue(_R.InHsk(2, "笔"))
        self.assertFalse(_R.InHsk(1, "笔"))
        self.assertFalse(_R.InHsk(3, "笔"))
        self.assertFalse(_R.InHsk(4, "笔"))
        self.assertFalse(_R.InHsk(5, "笔"))
        self.assertFalse(_R.InHsk(6, "笔"))

    def testGetHskLevel(self):
        self.assertEqual(_R.GetHskLevel("我"), 1)
        self.assertEqual(_R.GetHskLevel("笔"), 2)
        self.assertEqual(_R.GetHskLevel(""), None)


if __name__ == "__main__":
    absltest.main()
