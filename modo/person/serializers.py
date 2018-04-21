from rest_framework.serializers import HyperlinkedModelSerializer

from .models import Human


class HumanSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Human
        fields = ('email', 'first_name', 'last_name', 'registered_since')
