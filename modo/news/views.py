from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from . import serializers
from .management import tasks
from .management.paginators import ArticlePaginator
from .management.summary import Summarizer
from .models import Article


class NewsView(ModelViewSet):
    queryset = Article.objects.defer('text').order_by('-publish_time')
    pagination_class = ArticlePaginator
    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = ['title', 'keywords']
    ordering = ['-publish_time']

    def get_serializer_class(self):
        serializer_assignment = {
            'create': serializers.ArticleCreationSerializer,
            'list': serializers.ArticleHeadlineSerializer,
            'summary': serializers.ArticleSummarySerializer,
            'get_primary_key': serializers.ArticlePKRetrievalSerializer,
            'pull_articles': serializers.ArticleTaskSerializer,
            'update_sources': serializers.ArticleTaskSerializer,

        }

        return serializers.ArticleSerializer \
            if self.action not in serializer_assignment \
            else serializer_assignment[self.action]

    def get_permissions(self):
        if self.action == 'destroy' \
                or self.action == 'update' \
                or self.action == 'partial_update' \
                or self.action == 'create':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @ensure_csrf_cookie
    def create(self, request, *args, **kwargs):
        """ Add a news story manually, for admin use only.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data
            Article.objects.create_article(url=data['url'],
                                           authors=data['authors'],
                                           publish_time=data['publish_time'],
                                           title_image=data['images'])
            return Response({'message': 'News story added.'})
        else:
            return Response({'error': serializer.errors})

    def destroy(self, request, *args, **kwargs):
        """ Delete a news story, for admin use only.
        """
        try:
            article = self.get_object()
        except PermissionDenied as pd:
            return Response({'error': str(pd)})

        title = article.title
        site_name = article.site_name
        article.delete()
        return Response({'message': '{0} from {1} is removed.'.format(title, site_name)})

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article_data = self.get_serializer(article).data
        article_data['views'] = article.viewed_by.count()
        article_data['saves'] = article.saved_by.count()
        return Response(article_data)

    @action(methods=['get'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def share(self, request):
        """ Add the article to current user's list of shared articles."""
        try:
            article = self.get_object()
        except PermissionDenied as pd:
            return Response({'error': str(pd)})

        article.shared_by.add(request.user)
        return Response({'message': '"{}" is shared'.format(article.title)})

    @action(methods=['get'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def save(self, request):
        """ Add the article to current user's list of saved articles."""
        try:
            article = self.get_object()
        except PermissionDenied as pd:
            return Response({'error': str(pd)})

        if article.saved_by.filter(identifier=request.user.identifier).count() == 0:
            # Check if the article is already saved by current user.
            article.saved_by.add(request.user)
            return Response({'message': '"{}" is saved.'.format(article.title)})
        else:
            article.saved_by.remove(request.user)
            return Response({'message': '"{}" is no longer saved.'.format(article.title)})

    @action(methods=['get'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def view(self, request):
        """ Add the article to current user's list of viewed articles."""
        try:
            article = self.get_object()
        except PermissionDenied as pd:
            return Response({'error': str(pd)})

        if article.viewed_by.filter(identifier=request.user.identifier).count() == 0:
            # Check if the article is already viewed by current user.
            article.viewed_by.add(request.user)
            return Response({'message': '"{}" is viewd.'.format(article.title)})

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAdminUser])
    def get_primary_key(self, request):
        """ Get article instance primary key from input article source url. Admin only."""
        queryset = self.get_queryset()
        url = request.data['url']
        try:
            article = get_object_or_404(queryset, url=url)
            return Response({'primary_key': article.identifier})
        except Http404 as e:
            return Response({'error': str(e)})

    @csrf_exempt
    @action(methods=['post'], detail=False)
    def pull_articles(self, *args, **kwargs):
        """ Pull new articles from the internet. Avoid frequently making this request.
        """
        tasks.pull_articles()
        return Response({})

    @csrf_exempt
    @action(methods=['post'], detail=False)
    def update_sources(self, *args, **kwargs):
        """ Update the list of news sources.
        """
        tasks.update_sources()
        return Response({})

    @action(methods=['get'], detail=True)
    def summary(self, *args, **kwargs):
        """ Get the summary and keywords on the current article instance.
        """
        article = self.get_object()
        summary_data = self.get_serializer(article).data

        keywords = summary_data['keywords']
        related_articles = \
            Article.objects.filter(Q(keywords__contains=keywords[:1])
                                   | Q(keywords__contains=keywords[1:2])
                                   | Q(keywords__contains=keywords[2:3])) \
            .order_by('-publish_time')[:11] \
            .values('identifier', 'title', 'images', 'site_name', 'domain', 'publish_time')

        related_articles = [related for related in list(related_articles)
                            if related['identifier'] != article.identifier]

        summary_data['related'] = related_articles

        return Response(summary_data)

    @action(methods=['get'], detail=False)
    def summarize(self, request):
        """ Get summary and keywords from given source url in param sourceUrl.
        """
        summarizer = Summarizer()
        data = request.query_params
        print('numKeywords' in data)

        summarizer.num_keywords = summarizer.num_keywords if 'numKeywords' not in data \
            else data['numKeywords']
        summarizer.min_wordcount = summarizer.min_wordcount if 'minWords' not in data \
            else data['minWords']
        summarizer.max_wordcount = summarizer.max_wordcount if 'maxWords' not in data \
            else data['maxWords']
        summarizer.default_ratio = summarizer.default_ratio if 'ratio' not in data \
            else data['ratio']

        try:
            result = summarizer.fetch(data['sourceUrl'])
        except MultiValueDictKeyError as e:
            return Response({'error': str(e)})

        return Response(result)
