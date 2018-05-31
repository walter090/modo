import os
import re
from requests.exceptions import Timeout

from newsapi import NewsApiClient
from zappa.async import task

from news.models import Article
from .secret_constants import API_KEY

import time


def pull_articles_decoy(*args):
    pull_articles()


@task
def pull_articles():
    start = int(round(time.time()))
    # Pull news stories every 2 hours.
    api = NewsApiClient(api_key=API_KEY)

    # Fetch up-to-date sources.
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'sources.txt'), 'r') as file:
        sources = file.read().split('\n')

    articles = []
    for chunk_i in range(len(sources) // 10):
        # Pull multiple sources at a time to minimize number of requests.
        source_chunk = ', '.join(sources[chunk_i * 10: chunk_i * 10 + 10])
        try:
            articles += api.get_top_headlines(sources=source_chunk,
                                              page_size=50)['articles']
        except Timeout:
            continue

    for article in articles:
        try:
            Article.objects.create_article(
                url=article['url'],
                authors=article['author'],
                publish_time=article['publishedAt'],
                title_image=article['urlToImage'],
                title=article['title'],
                description=article['description']
            )
        except:
            continue
    end = int(round(time.time()))
    print(end - start)


def update_sources_decoy(*args):
    update_sources()


@task
def update_sources():
    # Update news sources once a month.
    api = NewsApiClient(api_key=API_KEY)
    sources = api.get_sources(language='en')['sources']
    sources = [source['id'] for source in sources]
    # Exclude Google News
    regex = re.compile(r'^(?!(google-news|financial-times|fox-sports|australian-financial-review))')
    sources = list(filter(regex.search, sources))

    # Save sources to text file.
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'sources.txt'), 'w') as file:
        for source in sources:
            file.write(source)
            file.write('\n')
