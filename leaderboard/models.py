# leaderboard/models.py
from django.db import models
import uuid

class LeaderboardEntry(models.Model):
    user_id = models.CharField(max_length=128, unique=True)  # from Google Play Games
    email = models.EmailField()
    username = models.CharField(max_length=50)
    score = models.IntegerField(default=0)
    puzzles_solved = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"{self.username} ({self.score})"
