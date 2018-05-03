from django.http import Http404
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
            return Response({'error': 'Invalid input.'})

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
