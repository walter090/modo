import datetime

from dateutil import parser
from django.db.models import Manager
from goose3 import Goose

from person.models import Human


class ArticleManager(Manager):
    use_in_migration = True

    def create_article(self, url, authors,
                       publish_time, title_image):
        """Function for creating a new article.

        Args:
            url: str, URL to the article.
            authors: str, Authors' names.
            publish_time: str, Time of publishing.
            title_image: str, URL to title image.

        Returns:
            None.
        """
        article = self.model(url=url)

        goose = Goose()

        article_info = goose.extract(url=article['url']).infos

        article.title = article_info['title'],
        article.language = article_info['meta']['lang'],
        article.site_name = article_info['site_name'],
        article.authors = authors,
        article.description = article_info['opengraph']['description'],
        article.images = title_image,

        tweets = article_info['tweets'],
        tags = article_info['tags'],
        videos = article_info['movies'],

        try:
            article.publish_time = parser.parse(publish_time)
        except (ValueError, OverflowError):
            print('Invalid datetime format.')
            article.publish_time = datetime.datetime.now()

        article.tweets = ', '.join(tweets) if tweets and len(tweets) else None
        article.videos = ', '.join(videos) if videos and len(videos) else None
        article.tags = ', '.join(tags) if tags and len(tags) else None

        article.save()

    def save_article(self, user_id, article_id):
        """Perform the action of user saving an article.

        Args:
            user_id: bigint, User identifier/pk.
            article_id: bigint, Article identifier/pk.

        Returns:
            None
        """
        user = Human.objects.get(identifer=user_id)
        article = self.get(identifier=article_id)
        article.saved_by.add(user)

    def remove_saved_article(self, user_id, article_id):
        """Remove a saved article for a particular user.

        Args:
            user_id: bigint, User identifier/pk.
            article_id: bigint, Article identifier/pk.

        Returns:
            None.
        """
        user = Human.objects.get(identifier=user_id)
        article = self.get(identifier=article_id)
        article.saved_by.remove(user)
