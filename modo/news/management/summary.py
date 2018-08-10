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

        self.min_wordcount = 50
        self.max_wordcount = 150
        self.result_ratio = 0.2
        self.num_keywords = 5

    def fetch(self, url):
        goose = Goose()
        article = goose.extract(url)
        self.raw_info = article.infos
        self._parse()

    def _parse(self):
        self.title = self.raw_info['title']
        self.description = self.raw_info['meta']['description']
        self.text = self.raw_info['cleaned_text']

        self.language = self.raw_info['meta']['lang']
        self.domain = self.raw_info['domain']
        self.type = self.raw_info['opengraph']['type']
        self.authors = self.raw_info['opengraph']['authors']
        self.canonical_url = self.raw_info['opengraph']['url']

        self.summary = self.summarize_text('. '.join([self.description, self.text]))
        self.keywords = keywords(text='. '.join([self.title, self.description, self.text]), ratio=0.25,
                                 words=self.num_keywords, split=True, lemmatize=True)

    def dump(self):
        return self.raw_info

    def summarize_text(self, text):
        original_wordcount = self._count_words(text)
        shrunk_wordcount = int(original_wordcount * self.result_ratio)

        if shrunk_wordcount < self.min_wordcount:
            summary = summarize(text, word_count=self.min_wordcount)
        elif shrunk_wordcount > self.max_wordcount:
            summary = summarize(text, word_count=self.max_wordcount)
        else:
            summary = summarize(text, ratio=self.result_ratio)

        return summary

    @staticmethod
    def _count_words(text):
        stripped = text.strip(string.punctuation)
        if stripped == '':
            return 0

        return len(re.split(r'[^0-9A-Za-z]+', stripped))
