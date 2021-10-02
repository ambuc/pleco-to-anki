from src import frequency as frequency_lib

import tempfile
import csv
from unittest.mock import MagicMock, call
from typing import cast
from absl.testing import absltest
from absl import logging


class FrequencyTest(absltest.TestCase):
    def test(self):
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv') as f:
            with open(f.name, 'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows([
                    ['1', '的', '1000', '1.0'],
                    ['2', '一', '500', '2.0'],
                    ['3', '是', '250', '4.0'],
                    ['4', '不', '125', '8.0'],
                ])

            d = frequency_lib.make_frequencies_dict(f.name)
            print(d)
            self.assertEqual(frequency_lib.get_frequency(d, '的'), 1.0)
            self.assertEqual(frequency_lib.get_frequency(d, '一'), 2.0)
            self.assertEqual(frequency_lib.get_frequency(d, '是'), 4.0)
            self.assertEqual(frequency_lib.get_frequency(d, '不'), 8.0)

            self.assertEqual(frequency_lib.get_frequency(d, '?'), 99999999)


if __name__ == "__main__":
    absltest.main()
