"""
WhatsApp Service Module - Simple & Lightweight
Generates WhatsApp links for sending messages without any third-party APIs
Uses WhatsApp Click-to-Chat feature
"""

from urllib.parse import quote
from config import WHATSAPP_NUMBER

def format_phone_number(phone):
    """
    Format phone number to WhatsApp format (with country code)
    Assumes Indian numbers if no country code provided
    """
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # If number starts with 0, remove it and add country code
    if phone.startswith('0'):
        phone = phone[1:]
    
    # If number doesn't have country code, add +91 for India
    if not phone.startswith('+'):
        if len(phone) == 10:  # Indian mobile number
            phone = '+91' + phone
        elif len(phone) < 10:
            phone = '+91' + phone
        else:
            phone = '+' + phone
    
    return phone.replace('+', '')  # WhatsApp API doesn't need + prefix for wa.me

def generate_whatsapp_link(phone_number, message):
    """
    Generate a WhatsApp click-to-chat link
    
    Args:
        phone_number (str): Phone number (with or without country code)
        message (str): Message to send
    
    Returns:
        str: WhatsApp link URL
    """
    formatted_phone = format_phone_number(phone_number)
    encoded_message = quote(message)
    return f"https://wa.me/{formatted_phone}?text={encoded_message}"

def send_custom_order_notification(order_details):
    """
    Generate WhatsApp notification link for custom order
    
    Args:
        order_details (dict): Dictionary containing order information
            - product_type: Type of product
            - material: Material selected
            - color: Color preference
            - occasion: Occasion for order
            - size: Size preference
            - notes: Additional notes
            - name: Customer name
            - phone: Customer phone number
    
    Returns:
        str: WhatsApp link URL for owner
    """
    
    # Build message
    message_body = f"""🎁 NEW CUSTOM ORDER 🎁

📋 Order Details:
• Product Type: {order_details.get('product_type', 'N/A')}
• Material: {order_details.get('material', 'Not specified')}
• Color: {order_details.get('color', 'Not specified')}
• Occasion: {order_details.get('occasion', 'Not specified')}
• Size: {order_details.get('size', 'Not specified')}
• Notes: {order_details.get('notes', 'None')}

👤 Customer Info:
• Name: {order_details.get('name', 'N/A')}
• Phone: {order_details.get('phone', 'N/A')}

Please contact the customer to confirm the order."""
    
    # Generate link for owner's WhatsApp
    return generate_whatsapp_link(WHATSAPP_NUMBER, message_body)

def send_order_confirmation(customer_phone, order_id, product_type):
    """
    Generate WhatsApp confirmation link for customer
    
    Args:
        customer_phone (str): Customer's phone number
        order_id (int): Order ID
        product_type (str): Type of product ordered
    
    Returns:
        str: WhatsApp link URL for customer
    """
    
    # Build confirmation message
    message_body = f"""Thank you for your custom order! 🎉

Your Order ID: {order_id}
Product Type: {product_type}

We have received your order and will contact you shortly to confirm the details and discuss pricing.

Thank you for choosing us! 🧺"""
    
    # Generate link for customer's WhatsApp
    return generate_whatsapp_link(customer_phone, message_body)
