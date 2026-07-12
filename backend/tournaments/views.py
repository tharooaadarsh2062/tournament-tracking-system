from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Tournament, Team, Match
from .serializers import (
    TournamentSerializer, TeamSerializer, MatchSerializer, 
    MatchScoreUpdateSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdminUser, IsTeamManagerOrAdmin
from .services.fixture_generators import generate_round_robin, generate_knockout

class TournamentListCreateView(generics.ListCreateAPIView):
    """
    List all tournaments (anyone) or create a new tournament (Admin only).
    """
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class TournamentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve details of a tournament (anyone) or update/delete it (Admin only).
    """
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]

class TournamentGenerateFixturesView(APIView):
    """
    Generate fixtures for a tournament. Accessible by Admins only.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        try:
            tournament = Tournament.objects.get(pk=pk)
        except Tournament.DoesNotExist:
            return Response({"detail": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

        if tournament.matches.exists():
            return Response({"detail": "Fixtures have already been generated for this tournament."}, status=status.HTTP_400_BAD_REQUEST)

        teams = tournament.teams.all()
        if teams.count() < 2:
            return Response({"detail": "At least 2 teams must be registered to generate fixtures."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if tournament.format == 'round_robin':
                count = generate_round_robin(tournament, teams)
            else:
                count = generate_knockout(tournament, teams)
            return Response({"detail": f"Successfully generated {count} fixtures."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TournamentStandingsView(APIView):
    """
    Calculate and display current standings for a tournament (anyone).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            tournament = Tournament.objects.get(pk=pk)
        except Tournament.DoesNotExist:
            return Response({"detail": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

        teams = tournament.teams.all()
        matches = tournament.matches.all()

        # Initialize statistics for all registered teams
        standings = {}
        for team in teams:
            standings[team.id] = {
                "team_id": team.id,
                "team_name": team.name,
                "played": 0,
                "won": 0,
                "drawn": 0,
                "lost": 0,
                "points": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0
            }

        # Calculate statistics based on finished matches
        for match in matches:
            if match.home_score is not None and match.away_score is not None:
                h_id = match.home_team.id
                a_id = match.away_team.id

                if h_id not in standings or a_id not in standings:
                    continue

                standings[h_id]["played"] += 1
                standings[a_id]["played"] += 1

                standings[h_id]["goals_for"] += match.home_score
                standings[h_id]["goals_against"] += match.away_score

                standings[a_id]["goals_for"] += match.away_score
                standings[a_id]["goals_against"] += match.home_score

                if match.home_score > match.away_score:
                    standings[h_id]["won"] += 1
                    standings[h_id]["points"] += 3
                    standings[a_id]["lost"] += 1
                elif match.home_score < match.away_score:
                    standings[a_id]["won"] += 1
                    standings[a_id]["points"] += 3
                    standings[h_id]["lost"] += 1
                else:
                    standings[h_id]["drawn"] += 1
                    standings[h_id]["points"] += 1
                    standings[a_id]["drawn"] += 1
                    standings[a_id]["points"] += 1

        standings_list = list(standings.values())
        for s in standings_list:
            s["goal_difference"] = s["goals_for"] - s["goals_against"]

        # Sort: points desc, GD desc, goals_for desc
        standings_list.sort(key=lambda x: (x["points"], x["goal_difference"], x["goals_for"]), reverse=True)
        return Response(standings_list, status=status.HTTP_200_OK)

class TournamentResultsView(generics.ListAPIView):
    """
    List completed matches/results for a specific tournament (anyone).
    """
    serializer_class = MatchSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        tournament_id = self.kwargs.get('pk')
        return Match.objects.filter(
            tournament_id=tournament_id,
            home_score__isnull=False,
            away_score__isnull=False
        ).order_by('-scheduled_time')

class TournamentFixturesView(generics.ListAPIView):
    """
    List scheduled/upcoming matches for a specific tournament (anyone).
    """
    serializer_class = MatchSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        tournament_id = self.kwargs.get('pk')
        return Match.objects.filter(
            tournament_id=tournament_id,
            home_score__isnull=True,
            away_score__isnull=True
        ).order_by('scheduled_time')

class TeamListCreateView(generics.ListCreateAPIView):
    """
    List teams (anyone, filterable by tournament) or Register a team (Managers and Admins only).
    """
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsTeamManagerOrAdmin]

    def get_queryset(self):
        queryset = Team.objects.all()
        tournament_id = self.request.query_params.get('tournament')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

class TeamRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve team details (anyone), update or unregister/delete a team (Admin or assigned Manager only).
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsTeamManagerOrAdmin]

class TeamPerformanceView(APIView):
    """
    Track performance for a specific team, showing wins/losses/draws and recent form (anyone).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        completed_matches = Match.objects.filter(
            Q(home_team=team) | Q(away_team=team),
            home_score__isnull=False,
            away_score__isnull=False
        ).order_by('-scheduled_time')

        played = completed_matches.count()
        won = 0
        lost = 0
        drawn = 0
        goals_for = 0
        goals_against = 0
        recent_form = []

        for match in completed_matches:
            is_home = (match.home_team == team)
            team_score = match.home_score if is_home else match.away_score
            opp_score = match.away_score if is_home else match.home_score

            goals_for += team_score
            goals_against += opp_score

            if team_score > opp_score:
                won += 1
                if len(recent_form) < 5:
                    recent_form.append('W')
            elif team_score < opp_score:
                lost += 1
                if len(recent_form) < 5:
                    recent_form.append('L')
            else:
                drawn += 1
                if len(recent_form) < 5:
                    recent_form.append('D')

        points = (won * 3) + drawn
        goal_diff = goals_for - goals_against

        performance_data = {
            "team_id": team.id,
            "team_name": team.name,
            "played": played,
            "won": won,
            "drawn": drawn,
            "lost": lost,
            "points": points,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goal_diff,
            "recent_form": recent_form
        }

        return Response(performance_data, status=status.HTTP_200_OK)

class MatchListView(generics.ListAPIView):
    """
    List matches, filterable by tournament and/or completion status (anyone).
    """
    serializer_class = MatchSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Match.objects.all().order_by('scheduled_time')
        tournament_id = self.request.query_params.get('tournament')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)

        completed = self.request.query_params.get('completed')
        if completed is not None:
            is_completed = completed.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(
                home_score__isnull=not is_completed, 
                away_score__isnull=not is_completed
            )

        return queryset

class MatchUpdateView(generics.RetrieveUpdateAPIView):
    """
    Update match scores or scheduling. Accessible by Admins only.
    """
    queryset = Match.objects.all()
    serializer_class = MatchScoreUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
