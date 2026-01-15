"""
Configuration file for Handcrafted Baskets Flask app.
Customize these settings as needed.
"""

import os

# Flask Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///baskets.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Upload Settings
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

# WhatsApp
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', '9863824320')  # Replace with actual number

# Twilio Configuration for WhatsApp
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')  # Get from https://console.twilio.com
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')  # Get from https://console.twilio.com
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')  # Twilio WhatsApp sandbox number

# Admin Settings
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
