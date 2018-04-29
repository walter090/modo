from dateutil import parser

from django.db.models import Manager

from person.models import Human


class ArticleManager(Manager):
    use_in_migration = True

    def create_article(self, url,
                       title, text,
                       site_name, publish_time,
                       authors, description,
                       tweets, videos,
                       tags, language='en',
                       topic='general'):
        """Function for creating a new article.

        Args:
            url: str, URL to the article.
            title: str, Title of the article.
            text: str, Cleaned text of the article.
            site_name: str, Name of the source site.
            publish_time: str, Date time of the article's publishing.
            authors: list, List of strings of the authors.
            description: str, Description/subtitle of the article.
            tweets: list, List of links to tweets in the article.
            videos: list, List of links to videos in the article.
            tags: list, List of tags attached to the article.
            language: str, Code for the language of the article.
            topic: str, Category of an article.

        Returns:
            None.
        """
        article = self.model(url=url, title=title,
                             text=text, site_name=site_name,
                             language=language, description=description,
                             category=topic)

        article.publish_time = parser(publish_time)
        article.authors = ', '.join(authors)
        article.tweets = ', '.join(tweets)
        article.videos = ', '.join(videos)
        article.tags = ', '.join(tags)

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

    def fetch_articles(self, num=20):
        raise NotImplementedError
