from rest_framework.serializers import HyperlinkedModelSerializer

from .models import Human


class HumanSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Human
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'registered_since',
            'profile_pic'
        )
