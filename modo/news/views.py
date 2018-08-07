from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from . import serializers
from .management.paginators import ArticlePaginator
from .management import tasks
from .models import Article


class NewsView(ModelViewSet):
    """
    retrieve:
    Return a given news article according to ID.

    create:
    Create a new news article. Only admin can perform this action.

    delete:
    Delete a news article instance. Only admin can perform this action.

    list:
    List all news articles 40 per page.

    share:
    Add given article to the shared articles list of authenticated user.

    save:
    Save the given article for authenticated user.

    view:
    Add the article to authenticated user's viewed articles.

    get_primary_key:
    Get the article ID given the url of article source.

    pull_articles:
    Pull latest news articles from the internet.

    update_sources:
    Update list of news sources.
    """
    queryset = Article.objects.defer('text', 'tweets').order_by('-publish_time')
    pagination_class = ArticlePaginator

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ArticleCreationSerializer
        elif self.action == 'list':
            return serializers.ArticleHeadlineSerializer
        elif self.action == 'summarize':
            return serializers.ArticleSummarySerializer
        else:
            return serializers.ArticleSerializer

    def get_permissions(self):
        if self.action == 'destroy' \
                or self.action == 'partial_update' \
                or self.action == 'create':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

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
    def share(self, request, *args, **kwargs):
        try:
            article = self.get_object()
        except PermissionDenied as pd:
            return Response({'error': str(pd)})

        article.shared_by.add(request.user)
        return Response({'message': '"{}" is shared'.format(article.title)})

    @action(methods=['post'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def save(self, request, *args, **kwargs):
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
    def view(self, request, *args, **kwargs):
        try:
            article = self.get_object()
        except PermissionDenied as pd:
            return Response({'error': str(pd)})

        if article.viewed_by.filter(identifier=request.user.identifier).count() == 0:
            # Check if the article is already viewed by current user.
            article.viewed_by.add(request.user)
            return Response({'message': '"{}" is viewd.'.format(article.title)})

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAdminUser])
    def get_primary_key(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        url = request.data['url']
        try:
            article = get_object_or_404(queryset, url=url)
            return Response({'primary_key': article.identifier})
        except Http404 as e:
            return Response({'error': str(e)})

    @csrf_exempt
    @action(methods=['post'], detail=False)
    def pull_articles(self, request, *args, **kwargs):
        tasks.pull_articles()
        return Response({})

    @csrf_exempt
    @action(methods=['post'], detail=False)
    def update_sources(self, request, *args, **kwargs):
        tasks.update_sources()
        return Response({})

    @action(methods=['get'], detail=True)
    def summarize(self, request, *args, **kwargs):
        article = self.get_object()
        summary_data = self.get_serializer(article).data

        keywords = summary_data['keywords']
        related_articles = \
            Article.objects.filter(keywords__contains=keywords[:2]) \
            .order_by('-publish_time')[:11] \
            .values('identifier', 'title', 'images', 'site_name', 'publish_time')

        related_articles = [related for related in list(related_articles)
                            if related['identifier'] != article.identifier]

        summary_data['related'] = related_articles

        return Response(summary_data)
