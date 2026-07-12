from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from tournaments.models import Tournament

User = get_user_model()

class TournamentTests(APITestCase):

    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
            email='admin@example.com'
        )
        self.manager_user = User.objects.create_user(
            username='manager_user',
            password='password123',
            role='manager',
            email='manager@example.com'
        )
        self.spectator_user = User.objects.create_user(
            username='spectator_user',
            password='password123',
            role='spectator',
            email='spectator@example.com'
        )

        self.list_create_url = reverse('tournament-list-create')

    def test_admin_can_create_tournament_with_sport_and_format(self):
        """Verify Admin role can create a tournament selecting sport and format."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Epic Football Cup',
            'description': 'Main football tournament',
            'sport': 'football',
            'format': 'knockout'
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Epic Football Cup')
        self.assertEqual(response.data['sport'], 'football')
        self.assertEqual(response.data['format'], 'knockout')
        self.assertEqual(response.data['created_by'], self.admin_user.id)

    def test_admin_can_create_tournament_with_custom_esport(self):
        """Verify Admin can create an esports tournament (e.g. Valorant, Free Fire)."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Free Fire Grand League',
            'description': 'Esport event',
            'sport': 'Free Fire',
            'format': 'knockout'
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Free Fire Grand League')
        self.assertEqual(response.data['sport'], 'Free Fire')
        self.assertEqual(response.data['format'], 'knockout')

    def test_non_admin_cannot_create_tournament(self):
        """Verify managers and spectators are denied creation permissions."""
        # Test Manager
        self.client.force_authenticate(user=self.manager_user)
        data = {
            'name': 'Manager Cup',
            'sport': 'cricket',
            'format': 'round_robin'
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test Spectator
        self.client.force_authenticate(user=self.spectator_user)
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anyone_can_list_tournaments(self):
        """Verify list endpoint allows unauthenticated/spectator lookups."""
        Tournament.objects.create(
            name='Public Cup',
            created_by=self.admin_user,
            sport='basketball',
            format='round_robin'
        )

        # Unauthenticated
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Spectator
        self.client.force_authenticate(user=self.spectator_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Public Cup')

    def test_admin_can_edit_and_delete_tournament(self):
        """Verify Admin can edit and delete existing tournaments."""
        tournament = Tournament.objects.create(
            name='Original Name',
            created_by=self.admin_user,
            sport='football',
            format='round_robin'
        )
        detail_url = reverse('tournament-detail', kwargs={'pk': tournament.pk})

        # Test Edit (Update)
        self.client.force_authenticate(user=self.admin_user)
        update_data = {
            'name': 'Updated Name',
            'sport': 'tennis',
            'format': 'knockout'
        }
        response = self.client.put(detail_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')
        self.assertEqual(response.data['sport'], 'tennis')
        self.assertEqual(response.data['format'], 'knockout')

        # Test Delete (Destroy)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tournament.objects.filter(pk=tournament.pk).count(), 0)

    def test_non_admin_cannot_edit_or_delete_tournament(self):
        """Verify Manager or Spectator cannot edit or delete tournaments."""
        tournament = Tournament.objects.create(
            name='Secure Cup',
            created_by=self.admin_user,
            sport='football',
            format='round_robin'
        )
        detail_url = reverse('tournament-detail', kwargs={'pk': tournament.pk})

        # Manager edit attempt
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.put(detail_url, {'name': 'Hacked Cup'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Manager delete attempt
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_register_team_but_spectator_cannot(self):
        """Verify team registration permissions."""
        tournament = Tournament.objects.create(
            name='Championship',
            created_by=self.admin_user,
            sport='football',
            format='round_robin'
        )
        url = reverse('team-list-create')
        
        # Test Manager
        self.client.force_authenticate(user=self.manager_user)
        data = {
            'name': 'Real Madrid',
            'tournament': tournament.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Real Madrid')
        self.assertEqual(response.data['manager'], self.manager_user.id)

        # Manager trying to register a second team in the same tournament should fail
        response_dup = self.client.post(url, {'name': 'Barcelona', 'tournament': tournament.id})
        self.assertEqual(response_dup.status_code, status.HTTP_400_BAD_REQUEST)

        # Test Spectator
        self.client.force_authenticate(user=self.spectator_user)
        response_spec = self.client.post(url, {'name': 'Spectator Team', 'tournament': tournament.id})
        self.assertEqual(response_spec.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_generate_fixtures_but_manager_cannot(self):
        """Verify fixture generation permissions and functionality."""
        tournament = Tournament.objects.create(
            name='Premier League',
            created_by=self.admin_user,
            sport='football',
            format='round_robin'
        )
        from tournaments.models import Team
        # Create at least 2 teams
        Team.objects.create(name='Arsenal', tournament=tournament, manager=self.manager_user)
        Team.objects.create(name='Chelsea', tournament=tournament, manager=self.admin_user)
        
        gen_url = reverse('tournament-generate-fixtures', kwargs={'pk': tournament.pk})

        # Test Manager (should fail)
        self.client.force_authenticate(user=self.manager_user)
        response_mgr = self.client.post(gen_url)
        self.assertEqual(response_mgr.status_code, status.HTTP_403_FORBIDDEN)

        # Test Admin (should succeed)
        self.client.force_authenticate(user=self.admin_user)
        response_admin = self.client.post(gen_url)
        self.assertEqual(response_admin.status_code, status.HTTP_201_CREATED)
        # 2 teams -> 1 round robin match
        self.assertEqual(tournament.matches.count(), 1)

    def test_standings_calculation_and_results_endpoint(self):
        """Verify standings and results calculations."""
        tournament = Tournament.objects.create(
            name='World Cup',
            created_by=self.admin_user,
            sport='football',
            format='round_robin'
        )
        from tournaments.models import Team, Match
        from django.utils import timezone
        team_a = Team.objects.create(name='Argentina', tournament=tournament)
        team_b = Team.objects.create(name='Brazil', tournament=tournament)
        
        # Match played: Argentina 2 - 1 Brazil
        Match.objects.create(
            tournament=tournament,
            home_team=team_a,
            away_team=team_b,
            home_score=2,
            away_score=1,
            scheduled_time=timezone.now()
        )

        standings_url = reverse('tournament-standings', kwargs={'pk': tournament.pk})
        response = self.client.get(standings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Argentina should be first
        self.assertEqual(response.data[0]['team_name'], 'Argentina')
        self.assertEqual(response.data[0]['points'], 3)
        self.assertEqual(response.data[0]['played'], 1)
        self.assertEqual(response.data[0]['won'], 1)
        self.assertEqual(response.data[0]['goal_difference'], 1)

        # Brazil should be second
        self.assertEqual(response.data[1]['team_name'], 'Brazil')
        self.assertEqual(response.data[1]['points'], 0)
        self.assertEqual(response.data[1]['played'], 1)
        self.assertEqual(response.data[1]['lost'], 1)
        self.assertEqual(response.data[1]['goal_difference'], -1)

    def test_team_performance_endpoint(self):
        """Verify the team performance/tracking metrics."""
        tournament = Tournament.objects.create(
            name='Copa America',
            created_by=self.admin_user,
            sport='football',
            format='round_robin'
        )
        from tournaments.models import Team, Match
        from django.utils import timezone
        team = Team.objects.create(name='Uruguay', tournament=tournament, manager=self.manager_user)
        opponent = Team.objects.create(name='Colombia', tournament=tournament)

        # Create a match
        Match.objects.create(
            tournament=tournament,
            home_team=team,
            away_team=opponent,
            home_score=3,
            away_score=0,
            scheduled_time=timezone.now()
        )

        perf_url = reverse('team-performance', kwargs={'pk': team.pk})
        response = self.client.get(perf_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['played'], 1)
        self.assertEqual(response.data['won'], 1)
        self.assertEqual(response.data['points'], 3)
        self.assertEqual(response.data['recent_form'], ['W'])
