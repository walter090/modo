from django.db import models
from django.utils.translation import ugettext_lazy as _

from modo.util import auxiliary
from person.models import Human
from news.management.managers import ArticleManager


class Article(models.Model):
    identifier = models.BigIntegerField(_('identifier'), unique=True,
                                        primary_key=True, default=auxiliary.make_id)
    url = models.TextField(_('url'), unique=True)
    title = models.TextField(_('title'), null=True)
    authors = models.TextField(_('authors'), null=True)
    description = models.TextField(_('description'), null=True)
    language = models.CharField(_('language'), max_length=10, default='en')
    text = models.TextField(_('text'), null=True)
    site_name = models.CharField(_('site name'), max_length=50, null=True)
    tweets = models.TextField(_('tweets'), null=True)
    publish_time = models.DateTimeField(_('publish time'), null=True)
    videos = models.TextField(_('videos'), null=True)
    tags = models.TextField(_('tags'), null=True)
    topic = models.CharField(_('category'), max_length=20, default='general')
    images = models.TextField(_('images'), null=True)

    saved_by = models.ManyToManyField(Human, related_name='saved')
    viewed_by = models.ManyToManyField(Human, related_name='viewed')
    shared_by = models.ManyToManyField(Human, related_name='shared')

    views = models.IntegerField(_('views'), default=0)

    objects = ArticleManager

    class Meta:
        ordering = ['-publish_time', 'views']

    def __str__(self):
        return self.title
