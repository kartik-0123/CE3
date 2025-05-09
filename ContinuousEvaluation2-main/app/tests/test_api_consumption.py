import requests
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class APIConsumptionTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Flask API base URL
        self.api_base_url = 'http://localhost:5000/api'
        
        # Test data
        self.test_user = {
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'apipass123',
            'city': 'Test City',
            'country': 'Test Country'
        }
        
        self.test_cart_item = {
            'product_name': 'Test Product',
            'price': 99.99,
            'quantity': 2
        }

    def get_api_key(self):
        """Get API key from Flask backend"""
        response = requests.post(
            f'{self.api_base_url}/get-key',
            json={'username': 'testuser', 'password': 'testpass123'}
        )
        if response.status_code == 200:
            return response.json().get('api_key')
        return None

    def test_user_apis(self):
        """Test user-related APIs"""
        api_key = self.get_api_key()
        headers = {'X-API-Key': api_key} if api_key else {}

        # Test GET /users
        response = requests.get(f'{self.api_base_url}/users', headers=headers)
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertIsInstance(users, list)

        # Test POST /users
        response = requests.post(
            f'{self.api_base_url}/users',
            json=self.test_user,
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        new_user = response.json()
        self.assertEqual(new_user['username'], self.test_user['username'])

        # Test GET /users/<id>
        user_id = new_user['id']
        response = requests.get(f'{self.api_base_url}/users/{user_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        user = response.json()
        self.assertEqual(user['username'], self.test_user['username'])

        # Test PUT /users/<id>
        updated_data = {'city': 'Updated City'}
        response = requests.put(
            f'{self.api_base_url}/users/{user_id}',
            json=updated_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        updated_user = response.json()
        self.assertEqual(updated_user['city'], 'Updated City')

        # Test DELETE /users/<id>
        response = requests.delete(f'{self.api_base_url}/users/{user_id}', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_cart_apis(self):
        """Test cart-related APIs"""
        api_key = self.get_api_key()
        headers = {'X-API-Key': api_key} if api_key else {}

        # Test GET /cart
        response = requests.get(f'{self.api_base_url}/cart', headers=headers)
        self.assertEqual(response.status_code, 200)
        cart_items = response.json()
        self.assertIsInstance(cart_items, list)

        # Test POST /cart
        response = requests.post(
            f'{self.api_base_url}/cart',
            json=self.test_cart_item,
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        new_item = response.json()
        self.assertEqual(new_item['product_name'], self.test_cart_item['product_name'])

        # Test GET /cart/<id>
        item_id = new_item['id']
        response = requests.get(f'{self.api_base_url}/cart/{item_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        item = response.json()
        self.assertEqual(item['product_name'], self.test_cart_item['product_name'])

        # Test PUT /cart/<id>
        updated_data = {'quantity': 3}
        response = requests.put(
            f'{self.api_base_url}/cart/{item_id}',
            json=updated_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        updated_item = response.json()
        self.assertEqual(updated_item['quantity'], 3)

        # Test DELETE /cart/<id>
        response = requests.delete(f'{self.api_base_url}/cart/{item_id}', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_search_api(self):
        """Test search API"""
        api_key = self.get_api_key()
        headers = {'X-API-Key': api_key} if api_key else {}

        # Test search with query parameter
        response = requests.get(
            f'{self.api_base_url}/search',
            params={'query': 'test'},
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertIsInstance(results, dict)
        self.assertIn('users', results)
        self.assertIn('cart_items', results) 