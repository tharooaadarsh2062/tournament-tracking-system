from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from users.permissions import IsAdmin, IsManager, IsSpectator
from unittest.mock import Mock

User = get_user_model()

class AuthenticationTests(APITestCase):

    def setUp(self):
        # Clear out existing users just in case
        User.objects.all().delete()
        
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.profile_url = reverse('profile')

    def test_user_registration_default_role(self):
        """Test registering a user with default spectator role."""
        data = {
            'username': 'testspec',
            'email': 'testspec@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'testspec')
        self.assertEqual(response.data['role'], 'spectator')
        self.assertNotIn('password', response.data)

        # Check in DB
        user = User.objects.get(username='testspec')
        self.assertTrue(user.check_password('password123'))

    def test_user_registration_admin_role(self):
        """Test registering a user with custom admin role."""
        data = {
            'username': 'testadmin',
            'email': 'testadmin@example.com',
            'password': 'password123',
            'role': 'admin'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'admin')

    def test_login_returns_jwt_and_metadata(self):
        """Test logging in returns access/refresh tokens and user details."""
        # Create user
        User.objects.create_user(
            username='loginuser',
            password='password123',
            role='manager',
            email='manager@example.com'
        )

        data = {
            'username': 'loginuser',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'loginuser')
        self.assertEqual(response.data['user']['role'], 'manager')
        self.assertEqual(response.data['user']['email'], 'manager@example.com')

    def test_profile_endpoint_requires_auth(self):
        """Test profile endpoint rejects unauthenticated requests and permits authenticated requests."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Auth test
        user = User.objects.create_user(
            username='authuser',
            password='password123',
            role='spectator'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'authuser')
        self.assertEqual(response.data['role'], 'spectator')


class PermissionTests(APITestCase):

    def test_role_permissions(self):
        admin_user = User.objects.create_user(username='admin', password='123', role='admin')
        manager_user = User.objects.create_user(username='manager', password='123', role='manager')
        spectator_user = User.objects.create_user(username='spectator', password='123', role='spectator')
        anonymous_user = Mock(is_authenticated=False)

        # Mock request & view
        request_admin = Mock(user=admin_user)
        request_manager = Mock(user=manager_user)
        request_spectator = Mock(user=spectator_user)
        request_anonymous = Mock(user=anonymous_user)

        view = Mock()

        # IsAdmin checks
        admin_perm = IsAdmin()
        self.assertTrue(admin_perm.has_permission(request_admin, view))
        self.assertFalse(admin_perm.has_permission(request_manager, view))
        self.assertFalse(admin_perm.has_permission(request_spectator, view))
        self.assertFalse(admin_perm.has_permission(request_anonymous, view))

        # IsManager checks
        manager_perm = IsManager()
        self.assertFalse(manager_perm.has_permission(request_admin, view))
        self.assertTrue(manager_perm.has_permission(request_manager, view))
        self.assertFalse(manager_perm.has_permission(request_spectator, view))
        self.assertFalse(manager_perm.has_permission(request_anonymous, view))

        # IsSpectator checks
        spectator_perm = IsSpectator()
        self.assertFalse(spectator_perm.has_permission(request_admin, view))
        self.assertFalse(spectator_perm.has_permission(request_manager, view))
        self.assertTrue(spectator_perm.has_permission(request_spectator, view))
        self.assertFalse(spectator_perm.has_permission(request_anonymous, view))
