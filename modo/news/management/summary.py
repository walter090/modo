import re
import string

from goose3 import Goose
from gensim.summarization import keywords, summarize


class Summarizer:
    def __init__(self):
        self._raw_info = None

        self.num_keywords = 5
        self.default_ratio = 0.2
        self.min_wordcount = 50
        self.max_wordcount = 150

    def fetch(self, url, num_keywords=None, result_ratio=None, min_wordcount=None, max_wordcount=None):
        if num_keywords is None:
            num_keywords = self.num_keywords

        if result_ratio is None:
            result_ratio = self.default_ratio

        if min_wordcount is None:
            min_wordcount = self.min_wordcount

        if max_wordcount is None:
            max_wordcount = self.max_wordcount

        if result_ratio > 1 or result_ratio < 0:
            raise ValueError('Illegal value for ratio: ratio must be between 0 and 1.')

        if min_wordcount > max_wordcount:
            raise ValueError('Minimum word count cannot be greater that maximum word count.')

        self.fetch_only(url)
        return self._parse(num_keywords, result_ratio, min_wordcount, max_wordcount)

    def fetch_only(self, url):
        """Fetch from source without parsing.

        Args:
            url: string. URL to the source of article.

        Returns:
            None
        """
        goose = Goose()
        article = goose.extract(url)
        self._raw_info = article.infos

    def _parse(self, num_keywords, result_ratio, min_wordcount, max_wordcount):
        result = dict()

        title = self._raw_info['title']
        result['title'] = title

        description = self._raw_info['meta']['description']
        result['description'] = description

        text = self._raw_info['cleaned_text']
        result['text'] = text

        result['language'] = self._raw_info['meta']['lang']
        result['domain'] = self._raw_info['domain']
        result['type'] = self._raw_info['opengraph']['type']
        result['authors'] = self._raw_info['authors']
        result['canonical_url'] = self._raw_info['opengraph']['url']

        result['summarizaion'] = self.summarize_text('. '.join([description, text]),
                                                     result_ratio=result_ratio,
                                                     min_wordcount=min_wordcount,
                                                     max_wordcount=max_wordcount)
        result['keywords_'] = keywords(text='. '.join([title,
                                                       description,
                                                       text]),
                                       ratio=0.25,
                                       words=num_keywords, split=True, lemmatize=True)

        return result

    @property
    def raw_info(self):
        """ Dump pulled raw information.

        Returns:
            raw_info: dict. Raw information.
        """
        return self._raw_info

    def summarize_text(self, text, result_ratio=0.2, min_wordcount=50, max_wordcount=150):
        original_length = self._count_words(text)

        shrunk_wordcount = int(original_length * result_ratio)

        if shrunk_wordcount < min_wordcount:
            summary = summarize(text, word_count=min_wordcount)
        elif shrunk_wordcount > max_wordcount:
            summary = summarize(text, word_count=max_wordcount)
        else:
            summary = summarize(text, ratio=result_ratio)

        shrunk_length = self._count_words(summary)
        shrinkage = round((original_length - shrunk_length) / original_length, 2)

        return {
            'summary': summary,
            'original_length': original_length,
            'summary_length': shrunk_length,
            'shrinkage': shrinkage
        }

    @staticmethod
    def _count_words(text):
        stripped = text.strip(string.punctuation)
        if stripped == '':
            return 0

        return len(re.split(r'[^0-9A-Za-z]+', stripped))
