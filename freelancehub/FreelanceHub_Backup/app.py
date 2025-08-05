from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///freelance_marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_freelancer = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(200))
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)
    hourly_rate = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    services = db.relationship('Service', backref='freelancer', lazy=True)
    orders_as_client = db.relationship('Order', foreign_keys='Order.client_id', backref='client', lazy=True)
    orders_as_freelancer = db.relationship('Order', foreign_keys='Order.freelancer_id', backref='freelancer', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_time = db.Column(db.Integer, nullable=False)  # in days
    freelancer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    orders = db.relationship('Order', backref='service', lazy=True)
    images = db.relationship('ServiceImage', backref='service', lazy=True)

class ServiceImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    requirements = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    categories = ['Web Development', 'Graphic Design', 'Digital Marketing', 'Writing', 'Video & Animation', 'Music & Audio']
    featured_services = Service.query.filter_by(is_active=True).limit(8).all()
    return render_template('index.html', categories=categories, featured_services=featured_services)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_freelancer = 'is_freelancer' in request.form
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_freelancer=is_freelancer
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/services')
def services():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Service.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Service.title.contains(search) | Service.description.contains(search))
    
    services = query.order_by(Service.created_at.desc()).all()
    categories = ['Web Development', 'Graphic Design', 'Digital Marketing', 'Writing', 'Video & Animation', 'Music & Audio']
    
    return render_template('services.html', services=services, categories=categories, current_category=category, search=search)

@app.route('/service/<int:service_id>')
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    return render_template('service_detail.html', service=service)

@app.route('/create_service', methods=['GET', 'POST'])
@login_required
def create_service():
    if not current_user.is_freelancer:
        flash('Only freelancers can create services!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        price = float(request.form['price'])
        delivery_time = int(request.form['delivery_time'])
        
        service = Service(
            title=title,
            description=description,
            category=category,
            price=price,
            delivery_time=delivery_time,
            freelancer_id=current_user.id
        )
        db.session.add(service)
        db.session.commit()
        
        flash('Service created successfully!')
        return redirect(url_for('profile'))
    
    categories = ['Web Development', 'Graphic Design', 'Digital Marketing', 'Writing', 'Video & Animation', 'Music & Audio']
    return render_template('create_service.html', categories=categories)

@app.route('/order/<int:service_id>', methods=['GET', 'POST'])
@login_required
def create_order(service_id):
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        requirements = request.form['requirements']
        
        order = Order(
            client_id=current_user.id,
            service_id=service.id,
            freelancer_id=service.freelancer_id,
            total_amount=service.price,
            requirements=requirements
        )
        db.session.add(order)
        db.session.commit()
        
        flash('Order created successfully!')
        return redirect(url_for('profile'))
    
    return render_template('create_order.html', service=service)

@app.route('/api/search_services')
def search_services():
    query = request.args.get('q', '')
    services = Service.query.filter(
        Service.title.contains(query) | Service.description.contains(query)
    ).filter_by(is_active=True).limit(10).all()
    
    results = []
    for service in services:
        results.append({
            'id': service.id,
            'title': service.title,
            'price': service.price,
            'freelancer': service.freelancer.username
        })
    
    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 