from rest_framework import serializers
from .models import Note, NoteVersion
from django.contrib.auth.models import User

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'user', 'title', 'content', 'created_at', 'updated_at']
    
    def validate(self, data):

        if not data.get('title'):
            raise serializers.ValidationError("Title field is required.")
        if not data.get('content'):
            raise serializers.ValidationError("Content field is required.")
        return data

class NoteVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteVersion
        fields = ['id', 'note', 'content', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
