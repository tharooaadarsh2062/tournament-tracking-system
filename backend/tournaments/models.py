from django.db import models
from django.conf import settings

class Tournament(models.Model):
    FORMAT_CHOICES = [
        ('round_robin', 'Round Robin'),
        ('knockout', 'Knockout'),
        ('group_knockout', 'Group + Knockout'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sport = models.CharField(max_length=100, default='football')
    format = models.CharField(max_length=50, choices=FORMAT_CHOICES, default='round_robin')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Team(models.Model):
    name = models.CharField(max_length=255)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams', null=True, blank=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    scheduled_time = models.DateTimeField()
