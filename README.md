# Handcrafted Baskets - Mobile-First E-Commerce Website

A lightweight, production-ready handicraft selling website built with Flask and minimal frontend dependencies.

## Features

✅ **Mobile-First Design** - Optimized for phone screens first, responsive on all devices
✅ **Product Management** - Browse, view details, add to cart
✅ **Shopping Cart** - Session-based cart with WhatsApp integration
✅ **WhatsApp Ordering** - One-click WhatsApp integration with auto-formatted messages
✅ **Custom Orders** - Special request form for gifts and custom items
✅ **Admin Panel** - Secure admin panel to manage products and orders
✅ **Lightweight** - Minimal CSS/JS, no heavy frameworks
✅ **SQLite Database** - Simple, self-contained database
✅ **Production-Ready** - Clean code, error handling, input validation

## Project Structure

```
baskets/
├── app.py                 # Flask application & routes
├── models.py             # Database models
├── config.py             # Configuration (create as needed)
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── home.html        # Homepage
│   ├── products.html    # Products listing
│   ├── product_detail.html
│   ├── cart.html        # Shopping cart
│   ├── custom_order.html # Custom order form
│   ├── about.html       # About page
│   ├── contact.html     # Contact page
│   ├── admin_login.html # Admin login
│   ├── admin_dashboard.html
│   └── admin_product_form.html
├── static/              # CSS, JS, images
│   ├── style.css       # Mobile-first styles
│   └── script.js       # Minimal JavaScript
├── uploads/            # Product images
└── baskets.db          # SQLite database (auto-created)
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install Flask Flask-SQLAlchemy Werkzeug
```

### 2. Initialize Database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 3. Configure WhatsApp Number

Edit `app.py` and update the `WHATSAPP_NUMBER` variable:

```python
WHATSAPP_NUMBER = 'your-actual-whatsapp-number'  # e.g., '919876543210'
```

### 4. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Default Admin Credentials

- **Username:** admin
- **Password:** password

⚠️ **IMPORTANT:** Change these immediately in production!

To change password:
```python
python -c "
from app import app, db
from models import Admin
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = Admin.query.filter_by(username='admin').first()
    if admin:
        admin.password_hash = generate_password_hash('your-new-password')
        db.session.commit()
        print('Password updated!')
"
```

## Admin Panel

1. Navigate to `http://localhost:5000/admin/login`
2. Login with default credentials
3. Dashboard features:
   - Add new products with images
   - Edit product details (name, price, description, availability)
   - Delete products
   - View custom orders list
   - Manage inventory status (Available/Out of Stock/Made to Order)

## How It Works

### Product Management
- Admin uploads products with images, descriptions, and prices
- Products stored in SQLite database
- Images uploaded to `/uploads` folder

### Shopping Cart
- Cart stored in browser session (no user login required)
- Persistent during session
- Add/remove items easily

### WhatsApp Integration
- Clicking "Order via WhatsApp" opens WhatsApp
- Auto-fills message with:
  - Product names and quantities
  - Prices and total
  - User-editable message

### Custom Orders
- Customers submit special requests
- Admin views all custom orders in dashboard
- Admin can contact customer for details

## Features & Pages

| Page | Purpose |
|------|---------|
| Home | Hero section, featured products, CTAs |
| Products | Grid of all products |
| Product Detail | Full product info, add to cart |
| Cart | Review items, order via WhatsApp |
| Custom Order | Special requests form |
| About | Story about artisan, eco-friendly focus |
| Contact | WhatsApp, phone, hours, location |
| Admin Login | Secure admin access |
| Admin Dashboard | Manage products & orders |

## Configuration

Edit these in `app.py`:

```python
# WhatsApp number (required)
WHATSAPP_NUMBER = '919876543210'

# Secret key for sessions (change in production!)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baskets.db'

# Upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
```

## Database Schema

### Products Table
- id (Primary Key)
- name
- description
- price
- image (filename)
- availability (available/out_of_stock/made_to_order)
- size
- color

### CustomOrders Table
- id (Primary Key)
- product_type
- material
- color
- occasion
- size
- notes
- name (customer)
- phone (customer)
- created_at

### Admin Table
- id (Primary Key)
- username
- password_hash

## Design Principles

✅ **Mobile-First** - Thumb-friendly buttons, readable fonts (16px minimum)
✅ **Minimal** - No heavy frameworks, clean CSS only
✅ **Fast** - Optimized images, minimal dependencies
✅ **Trustworthy** - Clean, professional design
✅ **Handcrafted Feel** - Earthy colors (greens/browns), minimal animations

### Color Palette
- **Primary:** #8B7355 (Brown)
- **Accent:** #25D366 (WhatsApp Green)
- **Background:** #f9f9f9 (Off-white)
- **Text:** #333 (Dark Gray)

## Deployment (Production)

### For Small Scale / Low Traffic:

Use Gunicorn:
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

### Security Checklist:

- [ ] Change admin password
- [ ] Change `SECRET_KEY` in app.py
- [ ] Set `DEBUG=False`
- [ ] Use environment variables for sensitive data
- [ ] Add HTTPS support
- [ ] Implement proper file upload validation
- [ ] Add rate limiting for forms
- [ ] Regular database backups

### Environment Variables (.env file):

```
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key
WHATSAPP_NUMBER=your-number
DATABASE_URL=sqlite:///baskets.db
```

Then update app.py to use these:
```python
import os
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER')
```

## Troubleshooting

### Images not uploading?
- Check `/uploads` folder permissions
- Ensure file size < 16MB
- Use common formats (jpg, png, webp)

### Cart not working?
- Ensure cookies are enabled
- Check browser session storage
- Clear browser cache

### WhatsApp link not opening?
- Verify WhatsApp number format (country code + number)
- Test: `https://wa.me/1234567890`

### Admin login fails?
- Verify username/password
- Check database exists (`baskets.db`)
- Recreate admin user if needed

## Future Enhancements

Optional features not included in basic version:

- [ ] Email notifications for orders
- [ ] Product search/filter
- [ ] Image gallery per product
- [ ] User reviews/ratings
- [ ] Bulk product import
- [ ] PDF order receipts
- [ ] Email backup of orders
- [ ] Multi-language support
- [ ] Analytics dashboard

## License

Built for local artisans. Use and modify freely.

---

**Questions?** Keep it simple. This is a lightweight solution for local businesses, not a complex e-commerce platform.