"""
Tests for the User API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token


REGISTER_USER_URL = reverse('users:register')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
ME_URL = reverse('users:me')


def create_user(**params):
    """
    Create and return a new user.
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test the public features of the user API.
    """
    def setUp(self):
        self.client = APIClient()

    def test_register_valid_user_success(self):
        """
        Test registering a user with valid payload is successful.
        """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        response = self.client.post(REGISTER_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertEqual(user.name, payload['name'])
        self.assertNotIn('password', response.data)

    def test_register_user_with_existing_email_fails(self):
        """
        Test registering a user with an exisiting email fails..
        """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        create_user(**payload)
        response = self.client.post(REGISTER_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_short_password_fails(self):
        """
        Test registering a user with a short password fails.
        """
        payload = {
            'email': 'test@example.com',
            'password': '123',
            'name': 'Test User'
        }

        response = self.client.post(REGISTER_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """
        Test token creation for a user is successful.
        """
        user_details = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        response = self.client.post(LOGIN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Test token creation fails if credentials are invalid.
        """
        create_user(
            email='test@example.com',
            password='testpass123'
        )

        payload = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unathorized(self):
        """
        Test that authentication is required for users.
        """
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test API requests that require authentication.
    """
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test retrieving profile for the authenticated user.
        """
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': str(self.user.id),
            'email': self.user.email,
            'name': self.user.name,
            'role': self.user.role,
        })

    def test_post_me_not_allowed(self):
        """
        Test that POST is not allowed on the me/ endpoint.
        """
        response = self.client.post(ME_URL, {})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        Test updating the authenticated user's profile.
        """
        payload = {
            'name': 'Updated Name',
            'password': 'newpass123'
        }

        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_user_success(self):
        """
        Test logging out deletes the token and invalidates further requests.
        """
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        res = self.client.post(LOGOUT_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        token_exists = Token.objects.filter(user=self.user).exists()
        self.assertFalse(token_exists)

        me_res = self.client.get(ME_URL)
        self.assertEqual(me_res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_unauthenticated_fails(self):
        """
        Test logging out without credentials returns 401 Unauthorized.
        """
        self.client.credentials()
        res = self.client.post(LOGOUT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
