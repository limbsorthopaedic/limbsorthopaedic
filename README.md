# LIMBS Orthopaedic Website

A comprehensive Django-powered orthopaedic clinic platform with advanced features for patient care and staff management.

## Core Features

### 🏥 Patient Care
- Online appointment booking
- Service and product catalogs
- Patient profiles and history
- Feedback surveys
- AI-powered chatbot assistance

### 👨‍⚕️ Staff Management
- Real-time staff chat system
- Doctor dashboards
- Appointment management
- Internal notifications
- File sharing capabilities

### 📊 Administration
- Custom admin dashboard
- Content management system
- Analytics and reporting
- Patient feedback tracking
- Dynamic content editing

### 📱 User Experience
- Responsive design
- WhatsApp integration
- Email notifications
- Rich media support
- Accessibility features


## Technical Stack

- **Framework**: Django 5.1+
- **Database**: PostgreSQL
- **Frontend**: Tailwind CSS, JavaScript
- **Media**: Image processing and storage
- **Email**: SMTP integration
- **Real-time**: WebSocket for chat
- **Security**: Django's built-in security

## Quick Start

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables by creating a `.env` file:
   ```
   DJANGO_SECRET_KEY=your_secure_secret_key
   PGDATABASE=limbs_orthopaedic
   PGUSER=postgres
   PGPASSWORD=your_database_password
   PGHOST=localhost
   PGPORT=5432
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create admin user:
   ```bash
   python create_superuser.py
   ```

6. Start the server:
   ```bash
   python manage.py runserver 0.0.0.0:5000
   ```

## Project Structure

The project follows a modular Django structure with multiple apps:

- **core**: Base functionality and general pages
- **accounts**: User authentication with separate patient and doctor profiles
- **services**: Orthopaedic services catalog
- **products**: Medical products catalog
- **appointments**: Appointment booking system
- **blog**: Blog articles with CKEditor integration for rich text
- **testimonials**: Patient testimonials and success stories
- **content_manager**: Dynamic content management system with template tags
- **chatbot**: AI-powered patient assistance system

Each app contains its models, views, forms, and templates specific to its functionality.

For more detailed information about the project structure, please refer to the [STRUCTURE.md](STRUCTURE.md) file.

For a comprehensive guide on using the website, including all available URLs and user roles, please see the [USAGE.md](USAGE.md) file.


## Contact

- Email: LimbsOrthopaedic@gmail.com
- Phone: +254 719 628 276 / +254 714 663 594
- Location: ICIPE Road, Kasarani, Nairobi, Kenya

For deployment and production setup details, please refer to the [DEPLOYMENTPROCEDURE.md](DEPLOYMENTPROCEDURE.md) file.