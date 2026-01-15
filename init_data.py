"""
Sample Data Initialization Script
Populates the database with example products for testing.

Usage: python init_data.py
"""

from app import app, db
from models import Product

def init_sample_data():
    """Add sample products to database"""
    with app.app_context():
        # Clear existing products (optional)
        # Product.query.delete()
        
        # Sample products
        products = [
            Product(
                name="Small Storage Basket",
                description="Perfect for organizing small items. Handwoven with love using recycled materials. Great for desks, shelves, or bathroom storage.",
                price=12.99,
                availability="available",
                size="Small (20cm)",
                color="Natural"
            ),
            Product(
                name="Medium Gift Basket",
                description="Beautiful gift basket ideal for presents. Sturdy construction, eco-friendly materials, and a rustic charm that makes every gift special.",
                price=24.99,
                availability="available",
                size="Medium (30cm)",
                color="Brown"
            ),
            Product(
                name="Large Laundry Basket",
                description="Spacious basket for storing clothes, blankets, or laundry. Durable weave, comfortable handles, and timeless design.",
                price=34.99,
                availability="available",
                size="Large (40cm)",
                color="Natural"
            ),
            Product(
                name="Decorative Wall Basket",
                description="Add charm to your walls! This decorative basket is perfect for storing plants or as wall art. Eco-conscious craftsmanship.",
                price=18.50,
                availability="available",
                size="Medium (28cm)",
                color="Beige"
            ),
            Product(
                name="Picnic Basket with Handles",
                description="Perfect for outdoor adventures. Spacious, lightweight, and beautifully designed. Made from sustainable materials.",
                price=45.00,
                availability="made_to_order",
                size="Large (35cm)",
                color="Natural"
            ),
            Product(
                name="Pet Bed Basket",
                description="Comfortable and cozy pet bed. Your furry friend will love this handcrafted basket. Easy to clean and maintain.",
                price=29.99,
                availability="available",
                size="Medium (32cm)",
                color="Brown"
            ),
        ]
        
        # Add to database
        for product in products:
            # Check if product already exists
            if not Product.query.filter_by(name=product.name).first():
                db.session.add(product)
                print(f"✓ Added: {product.name}")
        
        db.session.commit()
        print("\n✅ Sample data initialized successfully!")
        print(f"📦 Total products in database: {Product.query.count()}")

if __name__ == "__main__":
    init_sample_data()
