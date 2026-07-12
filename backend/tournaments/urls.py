from django.urls import path
from .views import (
    TournamentListCreateView, TournamentRetrieveUpdateDestroyView,
    TournamentGenerateFixturesView, TournamentStandingsView,
    TournamentResultsView, TournamentFixturesView,
    TeamListCreateView, TeamRetrieveUpdateDestroyView, TeamPerformanceView,
    MatchListView, MatchUpdateView
)

urlpatterns = [
    # Tournaments
    path('tournaments/', TournamentListCreateView.as_view(), name='tournament-list-create'),
    path('tournaments/<int:pk>/', TournamentRetrieveUpdateDestroyView.as_view(), name='tournament-detail'),
    path('tournaments/<int:pk>/generate-fixtures/', TournamentGenerateFixturesView.as_view(), name='tournament-generate-fixtures'),
    path('tournaments/<int:pk>/standings/', TournamentStandingsView.as_view(), name='tournament-standings'),
    path('tournaments/<int:pk>/results/', TournamentResultsView.as_view(), name='tournament-results'),
    path('tournaments/<int:pk>/fixtures/', TournamentFixturesView.as_view(), name='tournament-fixtures'),

    # Teams
    path('teams/', TeamListCreateView.as_view(), name='team-list-create'),
    path('teams/<int:pk>/', TeamRetrieveUpdateDestroyView.as_view(), name='team-detail'),
    path('teams/<int:pk>/performance/', TeamPerformanceView.as_view(), name='team-performance'),

    # Matches
    path('matches/', MatchListView.as_view(), name='match-list'),
    path('matches/<int:pk>/', MatchUpdateView.as_view(), name='match-update'),
]
