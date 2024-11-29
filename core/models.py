from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.username


class Video(models.Model):
    GENRE_CHOICES = [
        ("ACTION", "Action"),
        ("COMEDY", "Comedy"),
        ("DRAMA", "Drama"),
        ("HORROR", "Horror"),
        ("SCIFI", "Science Fiction"),
        ("DOCUMENTARY", "Documentary"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="videos"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_file = models.URLField()
    thumbnail = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " " + self.title
