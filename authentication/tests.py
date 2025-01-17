from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user_data = {"email": "test@example.com", "password": "testpass123"}
        self.user = User.objects.create_user(**self.user_data)

    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse("register")
        data = {"email": "newuser@example.com", "password": "newpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data["email"], "newuser@example.com")

    def test_user_login(self):
        """Test user login endpoint"""
        url = reverse("login")
        response = self.client.post(url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_token_refresh(self):
        """Test token refresh endpoint"""
        login_url = reverse("login")
        login_response = self.client.post(login_url, self.user_data, format="json")
        refresh_token = login_response.data["refresh_token"]

        refresh_url = reverse("refresh")
        response = self.client.post(
            refresh_url, {"refresh_token": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_user_logout(self):
        """Test user logout endpoint"""
        login_url = reverse("login")
        login_response = self.client.post(login_url, self.user_data, format="json")
        refresh_token = login_response.data["refresh_token"]

        logout_url = reverse("logout")
        response = self.client.post(
            logout_url, {"refresh_token": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], "User logged out.")

    def test_get_user_info(self):
        """Test getting user info endpoint"""

        login_url = reverse("login")
        login_response = self.client.post(login_url, self.user_data, format="json")
        access_token = login_response.data["access_token"]

        url = reverse("me")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_update_user_info(self):
        """Test updating user info endpoint"""
        login_url = reverse("login")
        login_response = self.client.post(login_url, self.user_data, format="json")
        access_token = login_response.data["access_token"]

        url = reverse("me")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        update_data = {"username": "John Smith"}
        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "John Smith")
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        url = reverse("login")
        data = {"email": "test@example.com", "password": "wrongpass"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_refresh_token(self):
        """Test refresh with invalid token"""
        url = reverse("refresh")
        data = {"refresh_token": "00000000-0000-0000-0000-000000000000"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        url = reverse("me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
