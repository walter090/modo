import unittest
from .management.summary import Summarizer


class SummaryTestCase(unittest.TestCase):
    def setUp(self):
        self.summarizer = Summarizer()

    def test_count_words(self):
        self.assertEqual(self.summarizer._count_words(
            'The quick fox, walked over the hardworking frog, all done.'), 10)
        self.assertEqual(self.summarizer._count_words('.;,][]/'), 0)
        self.assertEqual(self.summarizer._count_words(''), 0)
        self.assertEqual(self.summarizer._count_words('The quick fox jumped over the lazy dog'), 8)


if __name__ == 'news':
    unittest.main()
