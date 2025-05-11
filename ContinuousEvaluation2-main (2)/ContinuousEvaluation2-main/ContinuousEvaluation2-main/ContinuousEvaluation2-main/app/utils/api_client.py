import requests
from django.conf import settings
from django.core.cache import cache
import json
from requests.exceptions import RequestException

class APIClient:
    def __init__(self):
        self.base_url = 'http://localhost:5000/api'
        self.api_key = None
        self.backend_available = True

    def check_backend_health(self):
        """Check if backend is available"""
        try:
            response = requests.get(f'{self.base_url}/health')
            self.backend_available = response.status_code == 200
            return self.backend_available
        except RequestException:
            self.backend_available = False
            return False

    def get_api_key(self, username, password):
        """Get API key from Flask backend"""
        if not self.check_backend_health():
            raise ConnectionError("Backend service is unavailable")

        cache_key = f'api_key_{username}'
        api_key = cache.get(cache_key)
        
        if not api_key:
            try:
                response = requests.post(
                    f'{self.base_url}/get-key',
                    json={'username': username, 'password': password}
                )
                if response.status_code == 200:
                    api_key = response.json().get('api_key')
                    cache.set(cache_key, api_key, timeout=3600)  # Cache for 1 hour
            except RequestException:
                raise ConnectionError("Failed to connect to backend service")
        
        self.api_key = api_key
        return api_key

    def _get_headers(self):
        """Get headers with API key"""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers

    def _make_request(self, method, endpoint, **kwargs):
        """Make API request with error handling"""
        if not self.check_backend_health():
            raise ConnectionError("Backend service is unavailable")

        try:
            response = requests.request(
                method,
                f'{self.base_url}/{endpoint}',
                headers=self._get_headers(),
                **kwargs
            )
            return response
        except RequestException:
            raise ConnectionError("Failed to connect to backend service")

    def get_users(self):
        """Get all users"""
        response = self._make_request('GET', 'users')
        return response.json() if response.status_code == 200 else []

    def get_user(self, user_id):
        """Get user by ID"""
        response = self._make_request('GET', f'users/{user_id}')
        return response.json() if response.status_code == 200 else None

    def create_user(self, user_data):
        """Create new user"""
        response = self._make_request('POST', 'users', json=user_data)
        return response.json() if response.status_code == 201 else None

    def update_user(self, user_id, user_data):
        """Update user"""
        response = self._make_request('PUT', f'users/{user_id}', json=user_data)
        return response.json() if response.status_code == 200 else None

    def delete_user(self, user_id):
        """Delete user"""
        response = self._make_request('DELETE', f'users/{user_id}')
        return response.status_code == 200

    def get_cart_items(self):
        """Get all cart items"""
        response = self._make_request('GET', 'cart')
        return response.json() if response.status_code == 200 else []

    def get_cart_item(self, item_id):
        """Get cart item by ID"""
        response = self._make_request('GET', f'cart/{item_id}')
        return response.json() if response.status_code == 200 else None

    def create_cart_item(self, item_data):
        """Create new cart item"""
        response = self._make_request('POST', 'cart', json=item_data)
        return response.json() if response.status_code == 201 else None

    def update_cart_item(self, item_id, item_data):
        """Update cart item"""
        response = self._make_request('PUT', f'cart/{item_id}', json=item_data)
        return response.json() if response.status_code == 200 else None

    def delete_cart_item(self, item_id):
        """Delete cart item"""
        response = self._make_request('DELETE', f'cart/{item_id}')
        return response.status_code == 200

    def search(self, query):
        """Search users and cart items"""
        response = self._make_request('GET', 'search', params={'query': query})
        return response.json() if response.status_code == 200 else {'users': [], 'cart_items': []} 