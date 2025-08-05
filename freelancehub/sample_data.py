from app import app, db, User, Service
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_sample_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create sample users
        users = [
            User(
                username='john_developer',
                email='john@example.com',
                password_hash=generate_password_hash('password123'),
                is_freelancer=True,
                bio='Experienced web developer with 5+ years of experience in modern web technologies.',
                skills='Python, Django, React, JavaScript, HTML, CSS',
                hourly_rate=50.0
            ),
            User(
                username='sarah_designer',
                email='sarah@example.com',
                password_hash=generate_password_hash('password123'),
                is_freelancer=True,
                bio='Creative graphic designer specializing in brand identity and UI/UX design.',
                skills='Photoshop, Illustrator, Figma, Brand Design, UI/UX',
                hourly_rate=45.0
            ),
            User(
                username='mike_writer',
                email='mike@example.com',
                password_hash=generate_password_hash('password123'),
                is_freelancer=True,
                bio='Professional content writer with expertise in SEO and marketing copy.',
                skills='Content Writing, SEO, Copywriting, Blog Writing',
                hourly_rate=35.0
            ),
            User(
                username='client_alice',
                email='alice@example.com',
                password_hash=generate_password_hash('password123'),
                is_freelancer=False
            ),
            User(
                username='client_bob',
                email='bob@example.com',
                password_hash=generate_password_hash('password123'),
                is_freelancer=False
            )
        ]
        
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        # Get user objects for creating services
        john = User.query.filter_by(username='john_developer').first()
        sarah = User.query.filter_by(username='sarah_designer').first()
        mike = User.query.filter_by(username='mike_writer').first()
        
        # Create sample services
        services = [
            Service(
                title='Professional Website Development',
                description='I will create a modern, responsive website using the latest technologies. Includes design, development, and deployment. Perfect for businesses looking to establish their online presence.',
                category='Web Development',
                price=500.0,
                delivery_time=7,
                freelancer_id=john.id
            ),
            Service(
                title='E-commerce Website with Payment Integration',
                description='Complete e-commerce solution with shopping cart, payment gateway integration (Stripe/PayPal), and admin panel. Mobile-responsive design included.',
                category='Web Development',
                price=800.0,
                delivery_time=14,
                freelancer_id=john.id
            ),
            Service(
                title='Logo Design and Brand Identity',
                description='Professional logo design with brand guidelines. Includes multiple concepts, revisions, and final files in all formats (AI, EPS, PNG, JPG).',
                category='Graphic Design',
                price=150.0,
                delivery_time=3,
                freelancer_id=sarah.id
            ),
            Service(
                title='Complete Brand Identity Package',
                description='Full brand identity design including logo, business cards, letterhead, social media templates, and brand guidelines. Perfect for startups and small businesses.',
                category='Graphic Design',
                price=300.0,
                delivery_time=5,
                freelancer_id=sarah.id
            ),
            Service(
                title='Website Content Writing',
                description='Professional content writing for your website. Includes homepage, about page, services page, and blog posts. SEO-optimized content that converts visitors into customers.',
                category='Writing',
                price=200.0,
                delivery_time=4,
                freelancer_id=mike.id
            ),
            Service(
                title='SEO Blog Articles (10 articles)',
                description='High-quality, SEO-optimized blog articles that will improve your search engine rankings. Includes keyword research and on-page optimization.',
                category='Writing',
                price=250.0,
                delivery_time=5,
                freelancer_id=mike.id
            ),
            Service(
                title='React.js Frontend Development',
                description='Custom React.js application with modern UI/UX design. Includes component development, state management, and API integration.',
                category='Web Development',
                price=600.0,
                delivery_time=10,
                freelancer_id=john.id
            ),
            Service(
                title='Social Media Design Package',
                description='Complete social media design package including profile pictures, cover photos, post templates, and story templates for Instagram, Facebook, and Twitter.',
                category='Graphic Design',
                price=120.0,
                delivery_time=3,
                freelancer_id=sarah.id
            )
        ]
        
        for service in services:
            db.session.add(service)
        db.session.commit()
        
        print("Sample data created successfully!")
        print(f"Created {len(users)} users and {len(services)} services")
        print("\nSample login credentials:")
        print("Username: john_developer, Password: password123 (Freelancer)")
        print("Username: sarah_designer, Password: password123 (Freelancer)")
        print("Username: mike_writer, Password: password123 (Freelancer)")
        print("Username: client_alice, Password: password123 (Client)")
        print("Username: client_bob, Password: password123 (Client)")

if __name__ == '__main__':
    create_sample_data() 