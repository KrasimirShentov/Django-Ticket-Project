"""
Tests for the User API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


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
        
        """

    def test_register_user_with_short_password_fails(self):
        """
        
        """

    def test_create_token_for_user(self):
        """
        
        """

    def test_create_token_invalid_credentials(self):
        """
        
        """

    def test_retrieve_user_unathorized(self):
        """
        
        """


class PrivateUserApiTests(TestCase):
    """
    Test API requests that require authentication.
    """