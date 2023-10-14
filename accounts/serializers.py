from rest_framework import serializers

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    MESSAGE_TYPE = 'user'
    VERSION = 1
    KEY_FIELD = 'id'

    class Meta:
        model = User
        fields = "__all__"

    @classmethod
    def lookup_instance(cls, id, **kwargs):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            pass