from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from models import db, Product, CustomOrder, Admin, Settings
import json
from config import *
from whatsapp_service import send_custom_order_notification, send_order_confirmation

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    # Create default admin if not exists
    if not Admin.query.filter_by(username='Nakha').first():
        admin = Admin(username='Nakha', password_hash=generate_password_hash('123456'))
        db.session.add(admin)
        db.session.commit()
    
    # Create default settings if not exists
    if not Settings.query.first():
        settings = Settings(whatsapp_number=os.getenv('WHATSAPP_NUMBER', WHATSAPP_NUMBER))
        db.session.add(settings)
        db.session.commit()

def get_whatsapp_number():
    """Get WhatsApp number from database settings"""
    settings = Settings.query.first()
    if settings:
        return settings.whatsapp_number
    return os.getenv('WHATSAPP_NUMBER', WHATSAPP_NUMBER)

@app.route('/')
def home():
    products = Product.query.filter_by(availability='available').limit(4).all()
    whatsapp_number = get_whatsapp_number()
    return render_template('home.html', products=products, whatsapp_number=whatsapp_number)


@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    products = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            products.append({'product': product, 'quantity': qty})
            total += product.price * qty
    whatsapp_number = get_whatsapp_number()
    return render_template('cart.html', products=products, total=total, whatsapp_number=whatsapp_number)

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    cart = session.get('cart', {})
    cart[str(id)] = cart.get(str(id), 0) + 1
    session['cart'] = cart
    flash('Product added to cart!')
    return redirect(url_for('products'))

@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):
    cart = session.get('cart', {})
    if str(id) in cart:
        del cart[str(id)]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/custom_order', methods=['GET', 'POST'])
def custom_order():
    if request.method == 'POST':
        order = CustomOrder(
            product_type=request.form['product_type'],
            material=request.form.get('material'),
            color=request.form.get('color'),
            occasion=request.form.get('occasion'),
            size=request.form.get('size'),
            notes=request.form.get('notes'),
            name=request.form['name'],
            phone=request.form['phone']
        )
        db.session.add(order)
        db.session.commit()
        
        # Generate WhatsApp link and redirect directly
        order_details = {
            'product_type': request.form['product_type'],
            'material': request.form.get('material'),
            'color': request.form.get('color'),
            'occasion': request.form.get('occasion'),
            'size': request.form.get('size'),
            'notes': request.form.get('notes'),
            'name': request.form['name'],
            'phone': request.form['phone']
        }
        
        # Get WhatsApp link for owner and redirect user directly
        whatsapp_link = send_custom_order_notification(order_details)
        
        # Redirect directly to WhatsApp chat with pre-filled message
        return redirect(whatsapp_link)
    return render_template('custom_order.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    whatsapp_number = get_whatsapp_number()
    return render_template('contact.html', whatsapp_number=whatsapp_number)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    products = Product.query.all()
    orders = CustomOrder.query.all()
    return render_template('admin_dashboard.html', products=products, orders=orders)

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    settings = Settings.query.first()
    
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        # Handle WhatsApp number update
        if form_type == 'whatsapp':
            new_number = request.form['whatsapp_number']
            if settings:
                settings.whatsapp_number = new_number
            else:
                settings = Settings(whatsapp_number=new_number)
                db.session.add(settings)
            db.session.commit()
            flash('WhatsApp number updated successfully!')
            
        # Handle account settings update
        elif form_type == 'account':
            admin = Admin.query.filter_by(username='admin').first()
            current_password = request.form['current_password']
            
            # Verify current password
            if not admin or not check_password_hash(admin.password_hash, current_password):
                flash('Current password is incorrect!')
                return redirect(url_for('admin_settings'))
            
            # Update username if provided
            new_username = request.form.get('new_username', '').strip()
            if new_username and new_username != admin.username:
                existing = Admin.query.filter_by(username=new_username).first()
                if existing:
                    flash('Username already exists!')
                    return redirect(url_for('admin_settings'))
                admin.username = new_username
                flash(f'Username updated to: {new_username}')
            
            # Update password if provided
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            if new_password:
                if new_password != confirm_password:
                    flash('Passwords do not match!')
                    return redirect(url_for('admin_settings'))
                if len(new_password) < 6:
                    flash('Password must be at least 6 characters long!')
                    return redirect(url_for('admin_settings'))
                admin.password_hash = generate_password_hash(new_password)
                flash('Password updated successfully!')
            
            db.session.commit()
        
        return redirect(url_for('admin_dashboard'))
    
    current_number = settings.whatsapp_number if settings else ''
    return render_template('admin_settings.html', current_number=current_number)

@app.route('/admin/product/new', methods=['GET', 'POST'])
def admin_new_product():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        file = request.files.get('image')
        filename = None
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        product = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            image=filename,
            availability=request.form['availability'],
            size=request.form.get('size'),
            color=request.form.get('color')
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_product_form.html', product=None)

@app.route('/admin/product/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_product(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.availability = request.form['availability']
        product.size = request.form.get('size')
        product.color = request.form.get('color')
        file = request.files.get('image')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_product_form.html', product=product)

@app.route('/admin/product/delete/<int:id>')
def admin_delete_product(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    product = Product.query.get_or_404(id)
    if product.image:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=False)