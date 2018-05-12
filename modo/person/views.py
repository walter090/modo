from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from news.serializers import ArticleHeadlineSerializer
from person.management import constants
from person.management.permissions import IsSelfOrAdmin
from .forms import SignupForm
from .models import Human
from .serializers import HumanSerializer


class HumanView(ModelViewSet):
    queryset = Human.objects.all()
    serializer_class = HumanSerializer

    lookup_field = 'username'

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'destroy' or self.action == 'partial_update':
            permission_classes = [IsSelfOrAdmin]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, **kwargs):
        try:
            human = self.get_object()
            serializer = self.get_serializer(human)
            return Response(serializer.data)
        except Http404 as e:
            return Response({'errors': str(e)})

    def create(self, request, *args, **kwargs):
        model_form = SignupForm(request.data)
        serializer = self.get_serializer(data=request.data)

        if model_form.is_valid() and serializer.is_valid():
            Human.objects.create_user(username=request.data['username'],
                                      email=request.data['email'],
                                      password=request.data['password'])
            return Response({'email': serializer.data['email'],
                             'username': serializer.data['username']})
        else:
            return Response({'errors': model_form.errors})

    def partial_update(self, request, *args, **kwargs):
        try:
            human = self.get_object()
        except Http404 as e:
            return Response({'errors': str(e)})

        updates = request.data

        for key, value in updates.items():
            if key in constants.EDITABLE_FIELDS:
                setattr(human, key, value)

        human.save()

        return Response({'info': 'Account updated.'})

    def destroy(self, request, *args, **kwargs):
        try:
            human = self.get_object()
        except Http404 as e:
            return Response({'errors': str(e)})

        email = human.email
        human.delete()
        return Response({'email': email})

    @action(methods=['get'], detail=True, permission_classes=[IsSelfOrAdmin])
    def saved(self, request, *args, **kwargs):
        try:
            human = self.get_object()
        except Http404 as e:
            return Response({'errors': str(e)})

        saved_articles = human.saved.all()
        serializer = ArticleHeadlineSerializer(saved_articles, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[IsSelfOrAdmin])
    def viewed(self, request, *args, **kwargs):
        try:
            human = self.get_object()
        except Http404 as e:
            return Response({'errors': str(e)})

        saved_articles = human.viewd.all()
        serializer = ArticleHeadlineSerializer(saved_articles, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAdminUser])
    def get_primary_key(self, request):
        queryset = self.get_queryset()
        email = request.data['email']
        try:
            human = get_object_or_404(queryset, email=email)
            return Response({'primary_key': human.identifier})
        except Http404 as e:
            return Response({'errors': str(e)})
