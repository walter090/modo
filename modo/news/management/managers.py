import datetime

from dateutil import parser
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Manager
from django.template.defaultfilters import slugify
from goose3 import Goose

from person.models import Human
from news.models import Article


class ArticleManager(Manager):
    use_in_migration = True

    def create_article(self, url, authors,
                       publish_time, title_image, description,
                       title):
        """Function for creating a new article.

        Args:
            title: str, Title of the article.
            description: str, Description of the article.
            url: str, URL to the article.
            authors: str, Authors' names.
            publish_time: str, Time of publishing.
            title_image: str, URL to title image.

        Returns:
            None.
        """
        if Article.objects.filter(url=url).count() == 0:
            print('Article "{}" already in database'.format(title))
            return

        article = self.model(url=url, authors=authors)

        goose = Goose()

        article_info = goose.extract(url=url)
        article_info = article_info.infos
        article.description = description
        article.title = title

        article.images = title_image
        article.domain = article_info['domain']
        article.text = self._extract_section(article_info, 'cleaned_text', None)

        try:
            site_name = article_info['opengraph']['site_name']
        except KeyError:
            site_name = 'Unknown'

        article.site_name = site_name

        if authors is None or authors == '':
            article.authors = site_name
        else:
            authors = authors.strip()
            article.authors = ' '.join([author.capitalize() for author in authors.split(' ')])

        lang = article_info['meta']['lang']
        article.language = lang if lang else 'en'

        tweets = self._extract_section(article_info, 'tweets', None)
        tags = self._extract_section(article_info, 'tags', None)
        videos = self._extract_section(article_info, 'videos', None)

        article.slug = slugify(article.title) if article.title else None

        try:
            article.publish_time = parser.parse(publish_time)
        except (ValueError, OverflowError, TypeError):
            print('Invalid datetime format.')
            article.publish_time = datetime.datetime.now()

        article.tweets = ', '.join(tweets) if tweets and len(tweets) else None
        article.videos = ', '.join([video['src'] for video in videos]) if videos and len(videos) else None
        article.tags = ', '.join(tags) if tags and len(tags) else None

        try:
            article.full_clean()
            article.save()
            print('Fetched article "{}" from {}'.format(article.title, article.site_name))
        except ValidationError:
            print('Article "{}" from {} already in database.'.format(article.title, article.site_name))
        except IntegrityError as ie:
            print('{} while fetching {} from {}'.format(ie, article.title, article.site_name))
            pass

    @staticmethod
    def _extract_section(info, section, absent):
        """ Catch KeyError when extracting information.

        Args:
            info: dict, Dictionary containing article information.
            section: str, Key in the dictionary to extract.
            absent: str, Fill in value when a KeyError is thrown.

        Returns:

        """
        try:
            value = info[section]
        except KeyError:
            value = absent

        return value.lstrip() if isinstance(value, str) else value

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
