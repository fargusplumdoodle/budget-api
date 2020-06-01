from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20, min_length=3, required=True)
    password = serializers.CharField(max_length=20, min_length=3, required=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def validate_username(self, value):
        # we shouldn't create duplicate users with this
        if len(User.objects.filter(username=value)) != 0:
            raise serializers.ValidationError("user already exists")
