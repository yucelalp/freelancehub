# FreelanceHub - Freelance Marketplace Platform

A modern freelance marketplace platform similar to Fiverr and Bionluk, built with Python Flask. This application allows freelancers to offer services and clients to hire them for various projects.

## Features

### For Clients
- Browse services by category
- Search for specific services
- View detailed service information
- Place orders with detailed requirements
- Track order status
- Review freelancers

### For Freelancers
- Create and manage services
- Set pricing and delivery times
- Receive orders from clients
- Manage order status
- Build portfolio and reputation

### Platform Features
- User authentication and registration
- Service categorization
- Search and filtering
- Responsive modern UI
- Real-time order tracking
- Review and rating system

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (with SQLAlchemy ORM)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login
- **Icons**: Font Awesome

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd freelance-marketplace
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:5000`

## Usage

### Getting Started

1. **Register an Account**
   - Visit the homepage and click "Join Now"
   - Choose between "Client" or "Freelancer" account type
   - Fill in your details and create your account

2. **For Clients**
   - Browse services by category or search for specific services
   - Click on a service to view details
   - Place an order with your requirements
   - Track your orders in your profile

3. **For Freelancers**
   - Create services with detailed descriptions
   - Set competitive pricing and delivery times
   - Receive and manage orders
   - Build your reputation through quality work

### Key Pages

- **Homepage** (`/`): Landing page with featured services and categories
- **Services** (`/services`): Browse all available services with search and filtering
- **Service Detail** (`/service/<id>`): Detailed view of a specific service
- **Profile** (`/profile`): User dashboard with orders/services management
- **Create Service** (`/create_service`): Form for freelancers to create new services
- **Place Order** (`/order/<id>`): Form for clients to place orders

## Database Schema

### Users
- Basic user information (username, email, password)
- Account type (client/freelancer)
- Profile information (bio, skills, hourly rate)

### Services
- Service details (title, description, category)
- Pricing and delivery information
- Freelancer association

### Orders
- Order details and requirements
- Status tracking (pending, in_progress, completed)
- Client and freelancer associations

### Reviews
- Rating and comment system
- Order-based reviews

## Customization

### Adding New Categories
Edit the categories list in `app.py`:
```python
categories = ['Web Development', 'Graphic Design', 'Digital Marketing', 'Writing', 'Video & Animation', 'Music & Audio', 'Your New Category']
```

### Styling
The application uses Bootstrap 5 with custom CSS variables. Modify the styles in `templates/base.html` to change the appearance.

### Database
The application uses SQLite by default. To use a different database, update the `SQLALCHEMY_DATABASE_URI` in `app.py`.

## Security Features

- Password hashing with Werkzeug
- User session management
- Form validation
- SQL injection protection through SQLAlchemy
- CSRF protection (can be added with Flask-WTF)

## Future Enhancements

- Payment integration (Stripe, PayPal)
- Real-time messaging system
- File upload for service images
- Advanced search filters
- Email notifications
- Mobile app
- API endpoints for mobile integration
- Dispute resolution system
- Escrow payment system

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions, please open an issue in the repository.

---

**Note**: This is a demonstration application. For production use, consider implementing additional security measures, payment processing, and proper deployment configurations. 