"""
Test suite for the auth_app.

Covers:
- User registration (success, validation errors, duplicate email).
- User login (success, invalid credentials, missing fields).
- Email check endpoint (existing, non-existing, missing parameter, authentication).
- User model string representation.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from auth_app.models import User


class RegistrationTests(TestCase):
    """Tests for user registration endpoint and serializer validation."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('registration')

    def test_registration_successful(self):
        data = {
            'fullname': 'Test User',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'repeated_password': 'TestPass123'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(User.objects.count(), 1)

    def test_registration_password_mismatch(self):
        data = {
            'fullname': 'Test User',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'repeated_password': 'DifferentPass123'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_registration_missing_email(self):
        data = {
            'fullname': 'Test User',
            'password': 'TestPass123',
            'repeated_password': 'TestPass123'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email(self):
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='pass123'
        )
        data = {
            'fullname': 'Test User',
            'email': 'existing@example.com',
            'password': 'TestPass123',
            'repeated_password': 'TestPass123'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(TestCase):
    """Tests for user login via email and password authentication."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('login')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPass123',
            fullname='Test User'
        )

    def test_login_successful(self):
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['fullname'], 'Test User')

    def test_login_wrong_password(self):
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_email(self):
        data = {
            'email': 'nonexistent@example.com',
            'password': 'TestPass123'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_credentials(self):
        response = self.client.post(self.url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url, {'password': 'TestPass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailCheckTests(TestCase):
    """Tests for the email-check endpoint requiring authentication."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('email-check')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='TestPass123',
            fullname='Test User'
        )
        self.client.force_authenticate(user=self.user)

    def test_email_check_exists(self):
        response = self.client.get(
            self.url,
            {'email': 'test@example.com'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['fullname'], 'Test User')
        self.assertIn('id', response.data)

    def test_email_check_not_exists(self):
        response = self.client.get(
            self.url,
            {'email': 'nonexistent@example.com'}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_email_check_missing_parameter(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_check_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            self.url,
            {'email': 'test@example.com'}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserModelTests(TestCase):
    """Tests for the custom User model string representation (__str__)."""

    def test_user_str_with_fullname(self):
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            fullname='Test User'
        )
        self.assertEqual(str(user), 'Test User')

    def test_user_str_without_fullname(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.assertEqual(str(user), 'testuser')
