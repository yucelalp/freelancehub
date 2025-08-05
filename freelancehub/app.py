from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import json
import requests
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///freelance_marketplace.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize SocketIO for real-time features
socketio = SocketIO(app, cors_allowed_origins="*")

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

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # credit_card, paypal, etc.
    card_last4 = db.Column(db.String(4))  # Last 4 digits of card
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    transaction_id = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationship
    order = db.relationship('Order', backref='payments', lazy=True)

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

# New Dynamic API Endpoints
@app.route('/api/trending_services')
def trending_services():
    """Get trending services based on recent orders"""
    recent_orders = Order.query.filter(
        Order.created_at >= datetime.utcnow() - timedelta(days=7)
    ).all()
    
    service_counts = {}
    for order in recent_orders:
        service_counts[order.service_id] = service_counts.get(order.service_id, 0) + 1
    
    trending_service_ids = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    
    trending_services = []
    for service_id, count in trending_service_ids:
        service = Service.query.get(service_id)
        if service and service.is_active:
            trending_services.append({
                'id': service.id,
                'title': service.title,
                'price': service.price,
                'freelancer': service.freelancer.username,
                'order_count': count
            })
    
    return jsonify(trending_services)

@app.route('/api/user_stats/<int:user_id>')
def user_stats(user_id):
    """Get user statistics"""
    user = User.query.get_or_404(user_id)
    
    if user.is_freelancer:
        services_count = Service.query.filter_by(freelancer_id=user_id, is_active=True).count()
        orders_received = Order.query.filter_by(freelancer_id=user_id).count()
        completed_orders = Order.query.filter_by(freelancer_id=user_id, status='completed').count()
        total_earnings = db.session.query(db.func.sum(Order.total_amount)).filter_by(
            freelancer_id=user_id, status='completed'
        ).scalar() or 0
        
        return jsonify({
            'services_count': services_count,
            'orders_received': orders_received,
            'completed_orders': completed_orders,
            'total_earnings': total_earnings,
            'completion_rate': (completed_orders / orders_received * 100) if orders_received > 0 else 0
        })
    else:
        orders_placed = Order.query.filter_by(client_id=user_id).count()
        completed_orders = Order.query.filter_by(client_id=user_id, status='completed').count()
        total_spent = db.session.query(db.func.sum(Order.total_amount)).filter_by(
            client_id=user_id, status='completed'
        ).scalar() or 0
        
        return jsonify({
            'orders_placed': orders_placed,
            'completed_orders': completed_orders,
            'total_spent': total_spent
        })

@app.route('/api/notifications')
@login_required
def get_notifications():
    """Get user notifications"""
    # Simulate notifications based on user activity
    notifications = []
    
    if current_user.is_freelancer:
        pending_orders = Order.query.filter_by(freelancer_id=current_user.id, status='pending').count()
        if pending_orders > 0:
            notifications.append({
                'type': 'order',
                'message': f'You have {pending_orders} pending order(s)',
                'timestamp': datetime.utcnow().isoformat()
            })
    
    recent_orders = Order.query.filter(
        Order.client_id == current_user.id,
        Order.created_at >= datetime.utcnow() - timedelta(days=1)
    ).count()
    
    if recent_orders > 0:
        notifications.append({
            'type': 'activity',
            'message': f'You placed {recent_orders} order(s) recently',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return jsonify(notifications)

# Real-time Socket.IO events
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        emit('user_connected', {'user_id': current_user.id})

@socketio.on('join_room')
def handle_join_room(data):
    if current_user.is_authenticated:
        room = f"user_{current_user.id}"
        emit('room_joined', {'room': room})

def send_notification(user_id, message, notification_type='info'):
    """Send real-time notification to user"""
    room = f"user_{user_id}"
    socketio.emit('notification', {
        'message': message,
        'type': notification_type,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)

# Enhanced order creation with notifications
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
        
        # Send real-time notification to freelancer
        send_notification(
            service.freelancer_id,
            f'New order received for "{service.title}"',
            'order'
        )
        
        flash('Order created! Please complete payment to confirm your order.')
        return redirect(url_for('payment_page', order_id=order.id))
    
    return render_template('create_order.html', service=service)

# Live chat functionality
@app.route('/api/chat/<int:order_id>')
@login_required
def get_chat_messages(order_id):
    """Get chat messages for an order"""
    order = Order.query.get_or_404(order_id)
    
    # Check if user is part of this order
    if current_user.id not in [order.client_id, order.freelancer_id]:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # For now, return empty messages (you can add a ChatMessage model later)
    return jsonify({'messages': []})

@socketio.on('send_message')
def handle_message(data):
    """Handle real-time chat messages"""
    order_id = data.get('order_id')
    message = data.get('message')
    
    if current_user.is_authenticated and order_id and message:
        # Emit message to both client and freelancer
        order = Order.query.get(order_id)
        if order and current_user.id in [order.client_id, order.freelancer_id]:
            room = f"order_{order_id}"
            socketio.emit('new_message', {
                'user_id': current_user.id,
                'username': current_user.username,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room)

# Payment System Routes
@app.route('/payment/<int:order_id>', methods=['GET', 'POST'])
@login_required
def payment_page(order_id):
    """Payment page for completing order payment"""
    order = Order.query.get_or_404(order_id)
    
    # Check if user is the client for this order
    if order.client_id != current_user.id:
        flash('You are not authorized to pay for this order.')
        return redirect(url_for('profile'))
    
    # Check if payment already exists
    existing_payment = Payment.query.filter_by(order_id=order_id).first()
    if existing_payment and existing_payment.status == 'completed':
        flash('Payment already completed for this order.')
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        # Get payment details from form
        card_number = request.form.get('card_number', '').replace(' ', '')
        card_cvv = request.form.get('card_cvv')
        card_expiry = request.form.get('card_expiry')
        card_holder = request.form.get('card_holder')
        
        # Basic validation
        if not all([card_number, card_cvv, card_expiry, card_holder]):
            flash('Please fill in all payment details.')
            return render_template('payment.html', order=order)
        
        if len(card_number) < 13 or len(card_number) > 19:
            flash('Invalid card number.')
            return render_template('payment.html', order=order)
        
        if len(card_cvv) < 3 or len(card_cvv) > 4:
            flash('Invalid CVV.')
            return render_template('payment.html', order=order)
        
        # Simulate payment processing (in real app, integrate with Stripe/PayPal)
        import uuid
        transaction_id = str(uuid.uuid4())
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method='credit_card',
            card_last4=card_number[-4:],
            status='completed',
            transaction_id=transaction_id,
            completed_at=datetime.utcnow()
        )
        
        # Update order status
        order.status = 'paid'
        
        db.session.add(payment)
        db.session.commit()
        
        # Send notification to freelancer
        send_notification(
            order.freelancer_id,
            f'Payment received for order #{order.id} - ${order.total_amount}',
            'payment'
        )
        
        flash('Payment completed successfully! Your order has been confirmed.')
        return redirect(url_for('profile'))
    
    return render_template('payment.html', order=order)

@app.route('/payment/success/<int:order_id>')
@login_required
def payment_success(order_id):
    """Payment success page"""
    order = Order.query.get_or_404(order_id)
    payment = Payment.query.filter_by(order_id=order_id).first()
    
    if not payment or payment.status != 'completed':
        flash('Payment not found or not completed.')
        return redirect(url_for('profile'))
    
    return render_template('payment_success.html', order=order, payment=payment)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True) 