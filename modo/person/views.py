from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .forms import SignupForm, SignInForm
from .models import Human
from .serializers import HumanSerializer


class HumanView(ModelViewSet):
    queryset = Human.objects.all()
    serializer_class = HumanSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, **kwargs):
        queryset = self.get_queryset()
        human = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(human)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        model_form = SignupForm(request.data)
        serializer = self.get_serializer(data=request.data)

        if model_form.is_valid() and serializer.is_valid():
            Human.objects.create_user(email=request.data['email'],
                                      password=request.data['password'])
            return Response(serializer.data['email'], status=201)
        else:
            return Response({'errors': model_form.errors}, status=400)
