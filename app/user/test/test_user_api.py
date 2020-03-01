from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        # Every single test that runs will refresh db
        self.client = APIClient()
        self.payload = {
            'email': 'test@lucie.com',
            'password': 'testpass',
            'name': 'Test name'
        }

    def test_create_vali_user_success(self):
        """Test creating user with valid payload is successful"""
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Check in db is user has been created
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(self.payload['password']))
        # Do not return password in request
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating uset that already exists fails"""
        create_user(**self.payload)
        res = self.client.post(CREATE_USER_URL, self.payload)
        # Expect 400 bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password is more than 5 characters"""
        self.payload['password'] = 'pw'
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=self.payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        create_user(**self.payload)
        res = self.client.post(TOKEN_URL, self.payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(**self.payload)
        self.payload['password'] = 'wrongpass'
        res = self.client.post(TOKEN_URL, self.payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created is user does not exist"""
        res = self.client.post(TOKEN_URL, self.payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        self.payload['password'] = ''
        res = self.client.post(TOKEN_URL, self.payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
