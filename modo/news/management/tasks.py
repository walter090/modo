import os
import re
from requests.exceptions import Timeout

from celery import shared_task
from newsapi import NewsApiClient
from zappa.async import task

from news.models import Article
from .secret_constants import API_KEY


@shared_task()
@task()
def pull_articles(*args):
    # Pull news stories every 2 hours.
    api = NewsApiClient(api_key=API_KEY)

    # Fetch up-to-date sources.
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'sources.txt'), 'r') as file:
        sources = file.read().split('\n')

    articles = []
    for chunk_i in range(len(sources) // 2):
        # Pull multiple sources at a time to minimize number of requests.
        source_chunk = ', '.join(sources[chunk_i * 2: chunk_i * 2 + 2])
        try:
            articles += api.get_top_headlines(sources=source_chunk,
                                              page_size=100)['articles']
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


@shared_task()
@task()
def update_sources(*args):
    # Update news sources once a month.
    api = NewsApiClient(api_key=API_KEY)
    sources = api.get_sources()['sources']
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
