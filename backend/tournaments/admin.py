from django.contrib import admin, messages
from .models import Tournament, Team, Player, Match
from .services.fixture_generators import generate_round_robin, generate_knockout

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sport', 'format', 'created_by', 'created_at')
    list_filter = ('format', 'sport', 'created_at')
    search_fields = ('name', 'sport', 'created_by__username')
    ordering = ('-created_at',)
    actions = ['generate_fixtures_action']

    @admin.action(description='Generate fixtures for selected tournaments')
    def generate_fixtures_action(self, request, queryset):
        for tournament in queryset:
            if tournament.matches.exists():
                self.message_user(
                    request,
                    f"Fixtures already exist for tournament '{tournament.name}'.",
                    messages.WARNING
                )
                continue

            teams = tournament.teams.all()
            if teams.count() < 2:
                self.message_user(
                    request,
                    f"Tournament '{tournament.name}' needs at least 2 registered teams to generate fixtures.",
                    messages.ERROR
                )
                continue

            try:
                if tournament.format == 'round_robin':
                    count = generate_round_robin(tournament, teams)
                else:
                    count = generate_knockout(tournament, teams)
                self.message_user(
                    request,
                    f"Successfully generated {count} fixtures for tournament '{tournament.name}'.",
                    messages.SUCCESS
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Error generating fixtures for '{tournament.name}': {str(e)}",
                    messages.ERROR
                )

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manager', 'tournament')
    list_filter = ('tournament',)
    search_fields = ('name', 'manager__username')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'team')
    search_fields = ('name', 'team__name')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'tournament', 'home_team', 'away_team', 'home_score', 'away_score', 'scheduled_time')
    list_filter = ('tournament', 'scheduled_time')
    search_fields = ('home_team__name', 'away_team__name')
