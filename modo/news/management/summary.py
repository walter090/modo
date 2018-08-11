import re
import string

from goose3 import Goose
from gensim.summarization import keywords, summarize


class Summarizer:
    def __init__(self):
        self.raw_info = None

        self.title = None
        self.description = None
        self.text = None
        self.summary = None
        self.keywords = None

        self.language = None
        self.domain = None
        self.type = None
        self.authors = None
        self.canonical_url = None

        self.shrinkage = 0
        self.original_length = -1
        self.shrunk_length = -1

    def fetch(self, url, num_keywords=5, result_ratio=0.2, min_wordcount=50, max_wordcount=150):
        self.fetch_only(url)
        self._parse(num_keywords, result_ratio, min_wordcount, max_wordcount)

    def fetch_only(self, url):
        """Fetch from source without parsing.

        Args:
            url: string. URL to the source of article.

        Returns:
            None
        """
        goose = Goose()
        article = goose.extract(url)
        self.raw_info = article.infos

    def _parse(self, num_keywords, result_ratio, min_wordcount, max_wordcount):
        self.title = self.raw_info['title']
        self.description = self.raw_info['meta']['description']
        self.text = self.raw_info['cleaned_text']

        self.language = self.raw_info['meta']['lang']
        self.domain = self.raw_info['domain']
        self.type = self.raw_info['opengraph']['type']
        self.authors = self.raw_info['authors']
        self.canonical_url = self.raw_info['opengraph']['url']

        self.summary = self.summarize_text('. '.join([self.description, self.text]),
                                           result_ratio=result_ratio,
                                           min_wordcount=min_wordcount,
                                           max_wordcount=max_wordcount)
        self.keywords = keywords(text='. '.join([self.title,
                                                 self.description,
                                                 self.text]),
                                 ratio=0.25,
                                 words=num_keywords, split=True, lemmatize=True)

    def dump(self):
        """ Return all extracted information in a dictionary.

        Returns:
            extraction: dict. Extracted info in a Python dictionary.
        """
        extraction = {key: value for key, value in self.__dict__.items()
                      if not (key.startswith('raw') or key.startswith('_'))}
        return extraction

    def dump_raw(self):
        """ Dump pulled raw information.

        Returns:
            raw_info: dict. Raw information.
        """
        return self.raw_info

    def summarize_text(self, text, result_ratio=0.2, min_wordcount=50, max_wordcount=150):
        self.original_length = self._count_words(text)

        shrunk_wordcount = int(self.original_length * result_ratio)

        if shrunk_wordcount < min_wordcount:
            summary = summarize(text, word_count=min_wordcount)
        elif shrunk_wordcount > max_wordcount:
            summary = summarize(text, word_count=max_wordcount)
        else:
            summary = summarize(text, ratio=result_ratio)

        self.shrunk_length = self._count_words(summary)
        self.shrinkage = round((self.original_length - self.shrunk_length) / self.original_length, 2)

        return summary

    @staticmethod
    def _count_words(text):
        stripped = text.strip(string.punctuation)
        if stripped == '':
            return 0

        return len(re.split(r'[^0-9A-Za-z]+', stripped))
