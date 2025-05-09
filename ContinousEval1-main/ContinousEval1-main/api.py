from flask import Blueprint, jsonify, request, current_app
from models import db, User, Cart1
from flask_login import login_required, current_user
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps

api = Blueprint('api', __name__)
bcrypt = Bcrypt()

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Authentication APIs
@api.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already registered'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    # Create new user
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        city=data.get('city', ''),
        country=data.get('country', '')
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")  # Add logging
        return jsonify({'message': str(e)}), 500

@api.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, current_app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.username} {user.surname}" if user.surname else user.username
            }
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

# User CRUD APIs
@api.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'city': user.city,
        'country': user.country
    } for user in users])

@api.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'city': user.city,
        'country': user.country
    })

@api.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        city=data.get('city', ''),
        country=data.get('country', '')
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'id': new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@api.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.city = data.get('city', user.city)
    user.country = data.get('country', user.country)
    if 'password' in data:
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    try:
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@api.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Cart CRUD APIs
@api.route('/api/cart', methods=['GET'])
@token_required
def get_cart_items(current_user):
    cart_items = Cart1.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': item.id,
        'product_name': item.product_name,
        'price': item.price,
        'quantity': item.quantity
    } for item in cart_items])

@api.route('/api/cart/user/<int:user_id>', methods=['GET'])
def get_user_cart_items(user_id):
    try:
        cart_items = Cart1.query.filter_by(user_id=user_id).all()
        print(f"Fetched {len(cart_items)} cart items for user ID {user_id}")
        return jsonify([{
            'id': item.id,
            'product_name': item.product_name,
            'price': item.price,
            'quantity': item.quantity
        } for item in cart_items])
    except Exception as e:
        print(f"❌ Error fetching cart items for user {user_id}: {str(e)}")
        return jsonify({'message': str(e)}), 500

@api.route('/api/cart/<int:item_id>', methods=['GET'])
@token_required
def get_cart_item(current_user, item_id):
    item = Cart1.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    return jsonify({
        'id': item.id,
        'product_name': item.product_name,
        'price': item.price,
        'quantity': item.quantity
    })

@api.route('/api/cart', methods=['POST'])
@token_required
def create_cart_item(current_user):
    try:
        data = request.get_json()
        print("Received cart item data:", data)

        # Create and save cart item
        new_item = Cart1(
            user_id=current_user.id,
            product_name=data['product_name'],
            price=float(data['price']),
            quantity=int(data.get('quantity', 1))
        )
        
        db.session.add(new_item)
        db.session.commit()
        print(f"✅ Cart item added for user {current_user.username}: {new_item.id}")
        
        return jsonify({
            'message': 'Cart item created successfully',
            'id': new_item.id,
            'product_name': new_item.product_name,
            'price': new_item.price,
            'quantity': new_item.quantity
        }), 201
    except Exception as e:
        db.session.rollback()
        print("❌ Error adding cart item:", str(e))
        return jsonify({'message': str(e)}), 500

@api.route('/api/cart/<int:item_id>', methods=['PUT'])
@token_required
def update_cart_item(current_user, item_id):
    item = Cart1.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    item.product_name = data.get('product_name', item.product_name)
    item.price = data.get('price', item.price)
    item.quantity = data.get('quantity', item.quantity)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Cart item updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@api.route('/api/cart/<int:item_id>', methods=['DELETE'])
@token_required
def delete_cart_item(current_user, item_id):
    item = Cart1.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Cart item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500 