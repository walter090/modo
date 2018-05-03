from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = (
            'url',
            'title',
            'authors',
            'description',
            'language',
            'text',
            'site_name',
            'tweets',
            'publish_time',
            'videos',
            'tags'
        )


class ArticleCreationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ('url', 'authors', 'publish_time', 'images')
