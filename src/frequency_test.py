from src import frequency as frequency_lib

import tempfile
import csv
from absl.testing import absltest


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

            fq = frequency_lib.Frequencies(f.name)
            self.assertEqual(fq.get_frequency('的'), 1.0)
            self.assertEqual(fq.get_frequency('一'), 2.0)
            self.assertEqual(fq.get_frequency('是'), 4.0)
            self.assertEqual(fq.get_frequency('不'), 8.0)

            self.assertEqual(fq.get_frequency('?'), 99999999)


if __name__ == "__main__":
    absltest.main()
