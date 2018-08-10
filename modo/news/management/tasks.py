import logging
import os
import re
import time

from newsapi.newsapi_client import NewsApiClient
from requests.exceptions import Timeout

from news.models import Article
from .secret_constants import API_KEY

logger = logging.getLogger(__name__)
base = os.path.dirname(os.path.abspath(__file__))


def log_completion_time(task):
    """Log time needed to complete scheduled task

    Args:
        task: function, Task to log.

    Returns:
        task_logged
    """
    def task_logged():
        start = int(round(time.time()))
        task()
        end = int(round(time.time()))
        logger.info('Task completed in {} seconds'.format(end - start))
    return task_logged


@log_completion_time
def pull_articles():
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

    undesirables = []
    with open(os.path.join(base, 'undesirable_sources.txt'), 'r') as file:
        for line in file:
            undesirables.append(line)

    for article in articles:
        try:
            Article.objects.create_article(
                url=article['url'],
                authors=article['author'],
                publish_time=article['publishedAt'],
                title_image=article['urlToImage'],
                title=article['title'],
                description=article['description'],
                undesirables=undesirables
            )
        except:
            continue


@log_completion_time
def update_sources():
    # Update news sources once a month.
    api = NewsApiClient(api_key=API_KEY)
    sources = api.get_sources(language='en')['sources']
    sources = [source['id'] for source in sources]
    # Exclude Google News
    regex = re.compile(r'^(?!(google-news|financial-times|fox-sports|'
                       r'australian-financial-review|reddit-r-all|the-lad-bible))')
    sources = list(filter(regex.search, sources))

    # Save sources to text file.
    with open(os.path.join(base, 'sources.txt'), 'w') as file:
        for source in sources:
            file.write(source)
            file.write('\n')
