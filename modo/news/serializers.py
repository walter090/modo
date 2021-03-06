from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = (
            'identifier',
            'url',
            'title',
            'slug',
            'authors',
            'description',
            'language',
            'text',
            'site_name',
            'publish_time',
            'images',
        )


class ArticleSummarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = [
            'identifier',
            'url',
            'title',
            'authors',
            'summary',
            'keywords',
            'site_name',
            'domain',
            'publish_time',
            'images',
        ]


class ArticleCreationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ['url', 'authors', 'publish_time', 'images']


class ArticlePKRetrievalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ['url']


class ArticleMinimalRetrievalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ['identifier']


class ArticleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = []


class ArticleHeadlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = [
            'identifier',
            'url',
            'authors',
            'publish_time',
            'images',
            'title',
            'description',
            'site_name',
            'domain',
        ]
