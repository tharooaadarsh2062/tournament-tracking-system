from rest_framework import serializers
from .models import Tournament, Team, Player, Match

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__'
