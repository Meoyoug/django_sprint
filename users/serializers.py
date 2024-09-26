from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        exclude = ['is_active', 'is_superuser', 'last_login', 'groups', 'user_permissions']
        # fields = ('username', 'email', 'password')
