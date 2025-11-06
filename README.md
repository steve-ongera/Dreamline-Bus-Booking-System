# Dreamline Bus Booking System

A comprehensive online bus ticket booking platform built with Django, featuring real-time seat selection, M-Pesa payment integration, and a modern user interface.

##  Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## ✨ Features

### Customer Features
- 🔍 **Advanced Search**: Search for trips by origin, destination, and date
- 💺 **Interactive Seat Selection**: Real-time seat availability with visual seat map
- 🔒 **Seat Locking**: Temporary seat reservation during booking process
- 📍 **Boarding Points**: Select pickup and drop-off locations
- 💳 **M-Pesa Integration**: Secure payment via M-Pesa STK Push
- 📧 **Email Notifications**: Booking confirmations and ticket delivery
- 📱 **Responsive Design**: Mobile-friendly interface
- ⭐ **Rating System**: View bus ratings and reviews
- 🎫 **Digital Tickets**: QR code-based tickets for easy verification

### Admin Features
- 🚌 **Bus Management**: Add, edit, and manage bus fleet
- 🛣️ **Route Management**: Configure routes with multiple stops
- 🕐 **Trip Scheduling**: Create and manage trip schedules
- 💰 **Pricing Control**: Set different prices for seat classes (Normal, Business, VIP)
- 📊 **Booking Management**: View and manage all bookings
- 👥 **Passenger Management**: Customer information and history
- 💸 **Payment Tracking**: Monitor payment status and transactions
- 📈 **Reports & Analytics**: Revenue reports and booking statistics

### Advanced Features
- 🔄 **Real-time Updates**: Live seat availability updates
- 🎨 **Amenities Display**: Show bus facilities (WiFi, AC, USB charging, etc.)
- 🏷️ **Seat Classes**: Multiple seat categories with different pricing
- ⏱️ **Departure Reminders**: Automated notifications before departure
- 🎫 **Booking History**: Track past and upcoming trips
- 🔐 **Secure Authentication**: User registration and login system

## 🛠️ Technologies Used

### Backend
- **Django 4.2+**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database (can use SQLite for development)
- **Celery**: Asynchronous task processing
- **Redis**: Caching and message broker

### Frontend
- **HTML5/CSS3**: Structure and styling
- **Bootstrap 5**: Responsive UI framework
- **jQuery**: DOM manipulation and AJAX
- **Bootstrap Icons**: Icon library

### Payment Integration
- **Daraja API**: M-Pesa payment gateway
- **Safaricom M-Pesa**: Mobile money integration

### Additional Tools
- **Pillow**: Image processing
- **ReportLab**: PDF generation for tickets
- **QR Code**: Ticket verification
- **Python-decouple**: Environment variable management

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package installer)
- PostgreSQL (optional, SQLite works for development)
- Redis (for production with Celery)
- Git

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bus-booking-system.git
cd bus-booking-system
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=bus_booking_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# M-Pesa Daraja API
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback/

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Site URL
SITE_URL=http://localhost:8000
```

### 5. Database Setup

```bash
# Create database (PostgreSQL)
createdb bus_booking_db

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Load Sample Data (Optional)

```bash
python manage.py loaddata initial_data.json
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## ⚙️ Configuration

### M-Pesa Setup

1. **Register for Daraja API**:
   - Visit [Safaricom Daraja Portal](https://developer.safaricom.co.ke)
   - Create an account and generate API credentials

2. **Configure STK Push**:
   - Get your Consumer Key and Consumer Secret
   - Set up callback URL for payment notifications
   - Use sandbox for testing

3. **Update Settings**:
   ```python
   # settings.py
   MPESA_CONFIG = {
       'CONSUMER_KEY': os.getenv('MPESA_CONSUMER_KEY'),
       'CONSUMER_SECRET': os.getenv('MPESA_CONSUMER_SECRET'),
       'SHORTCODE': os.getenv('MPESA_SHORTCODE'),
       'PASSKEY': os.getenv('MPESA_PASSKEY'),
   }
   ```

### Email Configuration

For Gmail:
1. Enable 2-factor authentication
2. Generate an app password
3. Use app password in EMAIL_HOST_PASSWORD

### Celery Setup (Production)

```bash
# Start Redis
redis-server

# Start Celery worker
celery -A your_project_name worker -l info

# Start Celery beat (for scheduled tasks)
celery -A your_project_name beat -l info
```

## 📖 Usage

### For Customers

1. **Search for Trips**:
   - Select origin and destination
   - Choose travel date
   - Click "Search Buses"

2. **Select Seats**:
   - Click "View Seats" on desired trip
   - Click on available seats to select
   - Choose boarding and dropping points

3. **Complete Booking**:
   - Fill in passenger details
   - Enter M-Pesa number
   - Complete payment via STK Push
   - Receive ticket via email

### For Administrators

1. **Access Admin Panel**:
   - Navigate to `/admin`
   - Login with superuser credentials

2. **Add Buses**:
   - Go to "Buses" section
   - Add bus details (name, number plate, capacity)
   - Configure seat layout

3. **Create Routes**:
   - Define origin and destination
   - Add intermediate stops with timings

4. **Schedule Trips**:
   - Select bus and route
   - Set departure time and date
   - Configure pricing for different seat classes

## 🔌 API Endpoints

### Public Endpoints

```
GET  /api/search-trips/              # Search available trips
GET  /api/trips/{id}/seats/          # Get seat availability
POST /api/seats/{id}/lock/           # Lock seat temporarily
POST /api/seats/{id}/unlock/         # Unlock seat
GET  /api/trips/{id}/boarding-points/ # Get boarding/dropping points
POST /api/create-booking/            # Create new booking
```

### Admin Endpoints

```
GET    /api/bookings/                # List all bookings
GET    /api/bookings/{id}/           # Booking details
PATCH  /api/bookings/{id}/           # Update booking
DELETE /api/bookings/{id}/           # Cancel booking
POST   /api/mpesa/callback/          # M-Pesa payment callback
```

### Example Request

```javascript
// Search trips
fetch('/api/search-trips/?origin=1&destination=2&date=2025-11-08')
  .then(response => response.json())
  .then(data => console.log(data));

// Create booking
fetch('/api/create-booking/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    trip_id: 1,
    seat_ids: [15, 16],
    boarding_point_id: 1,
    dropping_point_id: 3,
    full_name: 'John Doe',
    id_number: '12345678',
    email: 'john@example.com',
    phone: '0712345678'
  })
})
```

## 📁 Project Structure

```
bus-booking-system/
├── booking_system/           # Main project directory
│   ├── settings.py          # Project settings
│   ├── urls.py              # URL configuration
│   └── wsgi.py              # WSGI configuration
├── website_application/      # Main app
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── serializers.py       # DRF serializers
│   ├── admin.py             # Admin configuration
│   └── urls.py              # App URLs
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── home.html           # Homepage
│   └── search_results.html # Search results
├── static/                  # Static files
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Images
├── media/                   # User uploads
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
└── README.md               # This file
```

## 📸 Screenshots

### Homepage
*Search interface for finding available trips*

### Search Results
*List of available trips with details*

### Seat Selection
*Interactive seat map for choosing seats*

### Booking Confirmation
*Passenger details and payment*

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide for Python code
- Write meaningful commit messages
- Add comments for complex logic
- Update documentation as needed
- Write tests for new features

## 🐛 Known Issues

- Seat lock timeout may need adjustment based on payment processing time
- M-Pesa callback URL requires HTTPS in production
- Large seat maps (50+ seats) may need pagination

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Return trip booking
- [ ] Loyalty program
- [ ] Mobile app (React Native/Flutter)
- [ ] Real-time GPS tracking
- [ ] Chat support integration
- [ ] Discount codes and promotions
- [ ] Social media login
- [ ] Export reports to PDF/Excel
- [ ] SMS notifications
- [ ] Bus operator dashboard
- [ ] Advanced analytics

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Contact

**Steve Ongera**

- 📧 Email: steveongera001@gmail.com
- 📱 Phone (M-Pesa Support): +254 757 790 687
- 💼 GitHub: [@steveongera](https://github.com/steveongera)
- 🔗 LinkedIn: [Steve Ongera](https://linkedin.com/in/steveongera)

### Support

For technical support or M-Pesa integration assistance:
- Email: steveongera001@gmail.com
- WhatsApp: +254 757 790 687

### Hire the Developer

Available for:
- Custom feature development
- M-Pesa integration services
- Django web applications
- Full-stack development projects
- Technical consultation

---

## 🙏 Acknowledgments

- Bootstrap team for the excellent UI framework
- Django community for comprehensive documentation
- Safaricom for M-Pesa Daraja API
- All contributors and testers

## 📊 Project Status

**Current Version**: 1.0.0  
**Status**: Active Development  
**Last Updated**: November 2025

---

⭐ If you find this project helpful, please give it a star!

**Built with ❤️ by Steve Ongera**