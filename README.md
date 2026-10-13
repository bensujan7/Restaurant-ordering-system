Restaurant Ordering System
A lightweight Django-based Point of Sale (POS) and table management system designed for restaurants, featuring local currency formatting (Rs.),
real-time table occupancy tracking, and a clean Tailwind CSS user interface.

Project Structure:

Restaurant Ordering System/
│
├── env/                 # Python virtual environment
├── media/               # Uploaded images (menu items)
├── orders/              # Main app (models, views, forms, templates)
├── restaurant/          # Project configuration (settings, main urls)
├── db.sqlite3           # SQLite database
└── manage.py            # Django management script


Features:
Table Management: Real-time table capacity and status monitoring (Available, Partially Occupied, Full)
POS & Orders: Streamlined order placement with item quantities and special notes.
Menu & Category Administration: Easy-to-use CRUD interfaces with image uploads and local Rs. pricing.
Tailwind UI: Modern, responsive styling across all pages.

Getting Started
Follow these steps to run the project locally:

1. Clone or Open Project
Navigate to your project root folder in your terminal.

2. Activate the Virtual Environment
Windows:
env\Scripts\activate

macOS/Linux:
source env/bin/activate

3. Run Migrations
Ensure your database is up to date:
python manage.py migrate

4. Create a Superuser (Optional)

To access admin features:
python manage.py createsuperuser

5. Run the Server
python manage.py runserver

Open your browser and visit: http://127.0.0.1:8000/
