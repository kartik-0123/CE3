import requests
import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

class APIConnectionTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Flask API base URL
        self.flask_api_url = 'http://localhost:5000/api'
        
        # Get API key
        self.api_key = self.get_api_key()

    def get_api_key(self):
        """Get API key from Flask backend"""
        try:
            response = requests.post(
                f'{self.flask_api_url}/get-key',
                json={'username': 'testuser', 'password': 'testpass123'}
            )
            if response.status_code == 200:
                return response.json()['api_key']
        except requests.exceptions.RequestException as e:
            print(f"Error getting API key: {e}")
        return None

    def test_api_key_generation(self):
        """Test if we can get an API key"""
        self.assertIsNotNone(self.api_key, "Failed to get API key")

    def test_users_api(self):
        """Test users API endpoint"""
        headers = {'X-API-Key': self.api_key}
        try:
            response = requests.get(f'{self.flask_api_url}/users', headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
        except requests.exceptions.RequestException as e:
            self.fail(f"Users API test failed: {e}")

    def test_cart_api(self):
        """Test cart API endpoint"""
        headers = {'X-API-Key': self.api_key}
        try:
            response = requests.get(f'{self.flask_api_url}/cart', headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
        except requests.exceptions.RequestException as e:
            self.fail(f"Cart API test failed: {e}")

    def test_create_user(self):
        """Test user creation API"""
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        test_user = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'city': 'Test City',
            'country': 'Test Country'
        }
        try:
            response = requests.post(
                f'{self.flask_api_url}/users',
                headers=headers,
                json=test_user
            )
            self.assertEqual(response.status_code, 201)
        except requests.exceptions.RequestException as e:
            self.fail(f"Create user API test failed: {e}")

    def test_create_cart_item(self):
        """Test cart item creation API"""
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        test_item = {
            'product_name': 'Test Product',
            'price': 99.99,
            'quantity': 1
        }
        try:
            response = requests.post(
                f'{self.flask_api_url}/cart',
                headers=headers,
                json=test_item
            )
            self.assertEqual(response.status_code, 201)
        except requests.exceptions.RequestException as e:
            self.fail(f"Create cart item API test failed: {e}")

if __name__ == '__main__':
    import unittest
    unittest.main() 