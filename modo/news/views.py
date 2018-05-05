from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Article
from .serializers import ArticleSerializer, ArticleCreationSerializer


class NewsView(ModelViewSet):
    queryset = Article.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreationSerializer
        else:
            return ArticleSerializer

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

    @action(methods=['get'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def share(self, request, *args, **kwargs):
        try:
            article = self.get_object()
        except PermissionDenied as pd:
            return Response({'error': str(pd)})

        article.shared_by.add(request.user)
        return Response({'message': '"{}" is shared'.format(article.title)})

    @action(methods=['get'], detail=True, permission_classes=[permissions.IsAuthenticated])
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
            return Response({'message': '"{}" is saved.'.format(article.title)})
        else:
            article.viewed_by.remove(request.user)
            return Response({'message': '"{}" is no longer saved.'.format(article.title)})

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAdminUser])
    def get_primary_key(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        url = request.data['url']
        try:
            article = get_object_or_404(queryset, url=url)
            return Response({'primary_key': article.identifier})
        except Http404:
            return Response({'error': 'Article does not exist.'})
