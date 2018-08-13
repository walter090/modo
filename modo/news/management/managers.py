import logging

from dateutil import parser
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Manager
from django.template.defaultfilters import slugify
from django.utils import timezone
from gensim.summarization import keywords, summarize
from goose3 import Goose

from person.models import Human

logger = logging.getLogger(__name__)


class ArticleManager(Manager):
    use_in_migration = True

    def create_article(self, url, authors,
                       publish_time, title_image, description,
                       title, undesirables=None):
        """Function for creating a new article.

        Args:
            title: str, Title of the article.
            description: str, Description of the article.
            url: str, URL to the article.
            authors: str, Authors' names.
            publish_time: str, Time of publishing.
            title_image: str, URL to title image.
            undesirables: str, List of undesirable sources.

        Returns:
            None.
        """
        if undesirables is None:
            undesirables = []

        if self.filter(url=url).count():
            return

        article = self.model(authors=authors)

        goose = Goose()

        article_info = goose.extract(url=url)
        article_info = article_info.infos

        if article_info['domain'] in undesirables:
            return

        article.url = article_info['opengraph']['url']

        article.description = description
        article.title = title

        article.images = title_image
        article.domain = article_info['domain']

        article_text = self._extract_section(article_info, 'cleaned_text', None)
        article.text = article_text
        article.keywords = keywords('. '.join([title, description, article_text]), words=5, split=True,
                                    ratio=0.25, lemmatize=True)

        summary = summarize('. '.join([description, article_text]), ratio=0.2)
        if summary == '':
            summary = summarize('. '.join([description, article_text]), word_count=50)
        if summary == '':
            summary = article_text
        article.summary = summary

        try:
            site_name = article_info['opengraph']['site_name']
        except KeyError:
            site_name = 'Unknown'

        article.site_name = site_name

        if authors is None or authors == '':
            article.authors = site_name
        else:
            authors = authors.strip()
            article.authors = ', '.join([author.capitalize() for author in authors.split(' ')])

        lang = article_info['meta']['lang']
        article.language = lang if lang else 'en'

        article.slug = slugify(article.title) if article.title else None

        current_time = timezone.now()
        try:
            publish_time = parser.parse(publish_time)

            article.publish_time = publish_time if publish_time <= current_time \
                else current_time
        except (ValueError, OverflowError, TypeError):
            article.publish_time = current_time

        try:
            article.full_clean()
            article.save()
        except ValidationError:
            pass
        except IntegrityError as ie:
            logger.warning('{} while fetching {} from {}'.format(ie, article.title, article.site_name))
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
