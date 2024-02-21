from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shared_with = models.ManyToManyField(User, related_name='shared_notes')

    class Meta:
        app_label = 'notes_app'

class NoteVersion(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
