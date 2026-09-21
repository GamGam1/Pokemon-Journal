from django.contrib.auth.models import User
from rest_framework import serializers
from .models import JournalEntry


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        # create_user hashes the password automatically
        user = User.objects.create_user(**validated_data)
        return user


class JournalEntrySerializer(serializers.ModelSerializer):
    # user is set automatically from the request, never from the payload
    user = serializers.StringRelatedField(read_only=True)
    # Claude fills these — user never sends them
    detected_themes = serializers.JSONField(read_only=True)
    pokemon_song = serializers.JSONField(read_only=True)

    class Meta:
        model = JournalEntry
        fields = [
            'id',
            'user',
            'content',
            'created_at',
            'detected_themes',
            'pokemon_song',
        ]
        read_only_fields = ['created_at']