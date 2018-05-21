import os
import re
from requests.exceptions import Timeout

from celery import shared_task
from newsapi import NewsApiClient

from news.models import Article
from .secret_constants import API_KEY


@shared_task()
def pull_articles(*args):
    # Pull news stories every 2 hours.
    api = NewsApiClient(api_key=API_KEY)

    # Fetch up-to-date sources.
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'sources.txt'), 'r') as file:
        sources = file.read().split('\n')

    for chunk_i in range(len(sources) // 10):
        # Pull multiple sources at a time to minimize number of requests.
        source_chunk = ', '.join(sources[chunk_i * 10: chunk_i * 10 + 10])
        print(source_chunk)
        try:
            articles = api.get_top_headlines(sources=source_chunk,
                                             page_size=100,
                                             language='en')['articles']
        except Timeout:
            continue

        for article in articles:
            Article.objects.create_article(
                url=article['url'],
                authors=article['author'],
                publish_time=article['publishedAt'],
                title_image=article['urlToImage']
            )


@shared_task()
def update_sources(*args):
    # Update news sources once a month.
    api = NewsApiClient(api_key=API_KEY)
    sources = api.get_sources()['sources']
    sources = [source['id'] for source in sources]
    # Exclude Google News
    regex = re.compile(r'^(?!(google-news|financial-times|fox-sports))')
    sources = list(filter(regex.search, sources))

    # Save sources to text file.
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'sources.txt'), 'w') as file:
        for source in sources:
            file.write(source)
            file.write('\n')
