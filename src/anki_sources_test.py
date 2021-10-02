from src import anki_sources as anki_sources_test

from absl.testing import absltest


class AnkiSourcesTest(absltest.TestCase):

    def test(self):
        self.assertEqual(anki_sources_test.gen_template(1,
                                                        ["foo",
                                                         "bar"],
                                                        ["baz"]),
                         {'name': 'Card 1 foo+bar=>baz',
                          'qfmt': "<span id='foo'>{{foo}}</span><br><span id='bar'>{{bar}}</span>",
                          'afmt': "{{FrontSide}} <hr><span id='baz'>{{baz}}</span>",
                          })


if __name__ == "__main__":
    absltest.main()
