from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from flask_migrate import Migrate
import os
import secrets
from datetime import datetime, timedelta
from models import db, User, Cart1, APIKey
import jwt

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# Configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.urandom(24)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
app.config['API_KEY_EXPIRY'] = timedelta(days=1)

# Initialize extensions
db.init_app(app)                         
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import and register the API blueprint
from api import api
app.register_blueprint(api)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    username = request.args.get('username')
    return render_template('index.html', username=username, current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        surname = request.form.get('surname')
        country = request.form.get('country')
        city = request.form.get('city')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Try logging in.', 'danger')
            return redirect(url_for('register'))

        try:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(email=email, username=username, password=hashed_password, surname=surname, country=country, city=city)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('register'))
    return render_template('registration.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.username == "Kartik":
        flash('Welcome to the dashboard, Kartik!', 'success')  # Special message for Kartik
    users = User.query.all()
    return render_template('dashboard.html', username=current_user.username, users=users)

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    country = request.form.get('country')
    city = request.form.get('city')
    surname = request.form.get('surname', 'N/A')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already registered.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password, surname=surname, country=country, city=city)
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/update_user', methods=['POST'])
@login_required
def update_user():
    user_id = request.form.get('user_id')
    user = User.query.get(user_id)

    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('dashboard'))

    user.username = request.form.get('username')
    user.email = request.form.get('email')
    user.country = request.form.get('country')
    user.city = request.form.get('city')

    try:
        db.session.commit()
        flash('User updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('dashboard'))

    if user.id == current_user.id:
        flash('You cannot delete your own account while logged in!', 'danger')
        return redirect(url_for('dashboard'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "Kartik" and password == "123":
            special_user = User.query.filter_by(username="Kartik").first()
            if special_user:
                login_user(special_user)
                flash("Logged in as Kartik!", 'success')
                return redirect(url_for('dashboard'))

            else:
                flash("Special user Kartik not found in database.", "danger")
                return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home', username=user.username))
        else:
            flash('Invalid credentials. Try again.', 'danger')

    return render_template('login.html', current_user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.username != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/cards')
def cards():
    return render_template('cards.html')

@app.route('/cart2')
def cart2():
    return render_template('cart2.html')

@app.route('/cart1')
def cart1():
    return render_template('cart1.html')

@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/display')
def display():
    return render_template('display.html')

# ✅ GET all users (JSON)
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'surname': user.surname,
        'email': user.email,
        'city': user.city,
        'country': user.country
    } for user in users])

# ✅ POST: Create cart item (revised to work correctly)
@app.route('/api/cart', methods=['POST'])
def add_cart_item():
    try:
        data = request.get_json()
        print("Received data:", data)

        # Validation
        required_fields = ['user_id', 'product_name', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Check if user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User ID does not exist'}), 404

        # Create and save cart item
        cart_item = Cart1(
            user_id=data['user_id'],
            product_name=data['product_name'],
            price=float(data['price']),
            quantity=int(data.get('quantity', 1))
        )
        db.session.add(cart_item)
        db.session.commit()

        print("✅ Cart item added:", cart_item.id)
        return jsonify({'message': 'Cart item added', 'item_id': cart_item.id}), 201

    except Exception as e:
        db.session.rollback()
        print("❌ Error adding cart item:", str(e))
        return jsonify({'error': str(e)}), 500

# Other CRUD APIs
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id, 'username': user.username, 'surname': user.surname,
        'email': user.email, 'city': user.city, 'country': user.country
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        username=data['username'],
        surname=data.get('surname'), 
        email=data['email'],
        password=hashed_password,
        city=data['city'],
        country=data['country']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user_api(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.surname = data.get('surname', user.surname)
    user.email = data.get('email', user.email)
    user.city = data.get('city', user.city)
    user.country = data.get('country', user.country)
    db.session.commit()
    return jsonify({'message': 'User updated'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user_api(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user authentication"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Generate API key
        api_key = secrets.token_hex(16)
        expiry = datetime.utcnow() + app.config['API_KEY_EXPIRY']
        
        # Store API key
        key = APIKey(user_id=user.id, key=api_key, expiry=expiry)
        db.session.add(key)
        db.session.commit()

        return jsonify({
            'message': 'Login successful',
            'api_key': api_key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="Kartik").first():
            hashed_password = bcrypt.generate_password_hash("123").decode('utf-8')
            kartik = User(
                username="Kartik",
                surname="Sharma",
                email="kartik@example.com",
                password=hashed_password,
                city="Delhi",
                country="India"
            )
            db.session.add(kartik)
            db.session.commit()
            print("✅ Special user Kartik added.")
    
    app.run(debug=True)
