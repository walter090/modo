import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

from person.models import Human
from modo.util import auxiliary


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

    saved_by = models.ManyToManyField(Human, through='Readership')

    def __str__(self):
        return self.title


class Readership(models.Model):
    person = models.ForeignKey(Human, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    saved_on = models.DateField(default=datetime.date.today)
