from django.db import models
from django.utils.translation import ugettext_lazy as _

from modo.person.models import Human
from modo.modo.util import auxiliary


class Article(models.Model):
    identifier = models.BigIntegerField(_('identifier'), unique=True,
                                        primary_key=True, default=auxiliary.make_id)
    url = models.TextField(_('url'), unique=True)
    title = models.TextField(_('title'))
    authors = models.TextField(_('authors'))
    description = models.TextField(_('description'))
    language = models.CharField(_('language'), max_length=10)
    text = models.TextField(_('text'))
    site_name = models.CharField(_('site name'), max_length=50)
    tweets = models.TextField(_('tweets'))
    publish_time = models.DateTimeField(_('publish time'))
    videos = models.TextField(_('videos'))
    tags = models.TextField(_('tags'))

    saved_by = models.ManyToManyField(Human, through='Readership')

    def __str__(self):
        return self.title
