from rest_framework import serializers
from .models import Tournament, Team, Player, Match

class TournamentSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Tournament
        fields = ('id', 'name', 'description', 'sport', 'format', 'created_by', 'created_by_name', 'created_at')


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'team')


class TeamSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ('id', 'name', 'manager', 'manager_name', 'tournament', 'tournament_name', 'players')

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user:
            tournament = attrs.get('tournament')
            if not tournament:
                raise serializers.ValidationError({"tournament": "Tournament selection is required to register a team."})
            # Verify if user has already registered a team in this tournament
            if Team.objects.filter(manager=request.user, tournament=tournament).exists():
                raise serializers.ValidationError("You have already registered a team in this tournament.")
        return attrs


class MatchSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)

    class Meta:
        model = Match
        fields = (
            'id', 'tournament', 'tournament_name', 'home_team', 'home_team_name',
            'away_team', 'away_team_name', 'home_score', 'away_score', 'scheduled_time'
        )


class MatchScoreUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('home_score', 'away_score', 'scheduled_time')

    def validate(self, attrs):
        home_score = attrs.get('home_score')
        away_score = attrs.get('away_score')
        if home_score is not None and home_score < 0:
            raise serializers.ValidationError("Scores cannot be negative.")
        if away_score is not None and away_score < 0:
            raise serializers.ValidationError("Scores cannot be negative.")
        return attrs
