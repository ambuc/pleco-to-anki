from src.is_cjk import is_cjk

import unittest


class IsCjkTest(unittest.TestCase):
    def test_iscjk(self):
        self.assertTrue(is_cjk("你"))
        self.assertFalse(is_cjk("a"))
        self.assertFalse(is_cjk("1"))
        self.assertFalse(is_cjk(" "))


if __name__ == '__main__':
    unittest.main()
