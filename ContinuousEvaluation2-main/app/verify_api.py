import requests
import json
from datetime import datetime

def test_api_connection():
    print("🔍 Testing API Connections...")
    print("=" * 50)
    
    # Flask API base URL
    api_url = 'http://localhost:5000/api'
    
    # Test endpoints
    endpoints = {
        'Users API': '/users',
        'Cart API': '/cart',
        'API Key Generation': '/get-key'
    }
    
    # Test data
    test_user = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'city': 'Test City',
        'country': 'Test Country'
    }
    
    test_cart_item = {
        'product_name': 'Test Product',
        'price': 99.99,
        'quantity': 1
    }
    
    # Get API key first
    try:
        print("\n🔑 Getting API Key...")
        key_response = requests.post(
            f'{api_url}/get-key',
            json={'username': 'testuser', 'password': 'testpass123'}
        )
        
        if key_response.status_code == 200:
            api_key = key_response.json()['api_key']
            print("✅ API Key obtained successfully")
        else:
            print("❌ Failed to get API key")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return
    
    # Headers for API requests
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Test each endpoint
    for name, endpoint in endpoints.items():
        print(f"\n📡 Testing {name}...")
        try:
            if endpoint == '/get-key':
                response = requests.post(f'{api_url}{endpoint}', json=test_user)
            else:
                response = requests.get(f'{api_url}{endpoint}', headers=headers)
            
            if response.status_code in [200, 201]:
                print(f"✅ {name} is working")
                if response.content:
                    data = response.json()
                    print(f"📊 Response data: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ {name} returned status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error testing {name}: {e}")
    
    # Test creating a user
    print("\n👤 Testing User Creation...")
    try:
        response = requests.post(
            f'{api_url}/users',
            headers=headers,
            json=test_user
        )
        if response.status_code == 201:
            print("✅ User created successfully")
        else:
            print(f"❌ Failed to create user: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating user: {e}")
    
    # Test creating a cart item
    print("\n🛒 Testing Cart Item Creation...")
    try:
        response = requests.post(
            f'{api_url}/cart',
            headers=headers,
            json=test_cart_item
        )
        if response.status_code == 201:
            print("✅ Cart item created successfully")
        else:
            print(f"❌ Failed to create cart item: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating cart item: {e}")
    
    print("\n" + "=" * 50)
    print("✨ API Connection Test Complete")

if __name__ == '__main__':
    test_api_connection() 