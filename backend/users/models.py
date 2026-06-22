from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMIN = 'admin'
    MANAGER = 'manager'
    SPECTATOR = 'spectator'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Team Manager'),
        (SPECTATOR, 'Spectator'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=SPECTATOR)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
