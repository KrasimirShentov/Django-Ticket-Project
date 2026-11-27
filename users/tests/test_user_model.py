"""
Tests for the User Model.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class UserModelTests(TestCase):
    """
    Test User Model.
    """
    def test_create_user_with_email_successful(self):
        """
        Test creating a user with email is successful.
        """
        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normilized(self):
        """
        Test email is normilized for new users.
        """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'testpass123')

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """
        Test creating a user without an email raises a ValueError.
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass123')

    def test_new_user_invalid_email_raises_error(self):
        """
        Test creating a user with invalid email raises a ValidationError.
        """
        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user('not-real-email', 'testpass123')

    def test_new_user_no_password_raises_error(self):
        """
        Test creating a user without a password raises a ValueError
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('test@example.com', '')

    def test_create_admin(self):
        """
        Test creating an admin.
        """
        user = get_user_model().objects.create_admin(
            'test@example.com',
            'testpass123'
        )

        self.assertTrue(user.is_staff)

    def test_create_superuser(self):
        """
        Test creating a superuser.
        """
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
