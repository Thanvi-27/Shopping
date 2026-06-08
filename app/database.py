import sqlite3
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'shop_analytics.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, email TEXT, shop_id TEXT, role TEXT, created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY, customer_id TEXT UNIQUE, shop_id TEXT, entry_time TIMESTAMP, exit_time TIMESTAMP, 
                  entry_zone TEXT, exit_zone TEXT, duration INTEGER, total_spent REAL, created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS customer_zones
                 (id INTEGER PRIMARY KEY, customer_id TEXT, zone_name TEXT, enter_time TIMESTAMP, exit_time TIMESTAMP, duration INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS zones
                 (id INTEGER PRIMARY KEY, shop_id TEXT, name TEXT, description TEXT, x1 INTEGER, y1 INTEGER, x2 INTEGER, y2 INTEGER, enabled BOOLEAN, created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cameras
                 (id INTEGER PRIMARY KEY, shop_id TEXT, name TEXT, rtsp_url TEXT, location TEXT, status TEXT, frame_rate INTEGER, 
                  resolution TEXT, last_frame_time TIMESTAMP, camera_type TEXT, viewing_angle TEXT, brand_model TEXT, 
                  ip_address TEXT, port TEXT, night_vision TEXT, recording_quality TEXT, bitrate TEXT, audio_support TEXT, 
                  storage_location TEXT, recording_enabled BOOLEAN, created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS analytics
                 (id INTEGER PRIMARY KEY, shop_id TEXT, date DATE, hour INTEGER, total_customers INTEGER, avg_spend_time INTEGER, peak_time BOOLEAN, created_at TIMESTAMP)''')
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, shop_id TEXT, product_name TEXT, category TEXT, price REAL, stock_quantity INTEGER, 
                  description TEXT, enabled BOOLEAN, created_at TIMESTAMP)''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY, shop_id TEXT, customer_id TEXT, order_date TIMESTAMP, total_amount REAL, status TEXT, created_at TIMESTAMP)''')
    
    # Order items table
    c.execute('''CREATE TABLE IF NOT EXISTS order_items
                 (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price REAL, 
                  total_price REAL, created_at TIMESTAMP)''')
    
    # Product sales analytics table
    c.execute('''CREATE TABLE IF NOT EXISTS product_analytics
                 (id INTEGER PRIMARY KEY, shop_id TEXT, product_id INTEGER, date DATE, day_of_week TEXT, 
                  units_sold INTEGER, total_revenue REAL, created_at TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    
    # Create demo user if it doesn't exist
    create_demo_user()

def create_demo_user():
    """Create demo user if not exists"""
    conn = get_connection()
    c = conn.cursor()
    try:
        # Check if demo user already exists
        c.execute('SELECT * FROM users WHERE username = ?', ('demo',))
        if not c.fetchone():
            # Create demo user
            c.execute('INSERT INTO users (username, password, email, shop_id, role, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                      ('demo', 'demo123', 'demo@shop.local', 'SHOP001', 'manager', datetime.now()))
            conn.commit()
    except:
        pass
    finally:
        conn.close()

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# User Functions
def add_user(username, password, email, shop_id, role='manager'):
    """Add a new user"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, email, shop_id, role, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                  (username, password, email, shop_id, role, datetime.now()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    """Get user by username"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

# Customer Functions
def add_customer(customer_id, shop_id, entry_zone, entry_time=None):
    """Add a new customer"""
    conn = get_connection()
    c = conn.cursor()
    if entry_time is None:
        entry_time = datetime.now()
    
    try:
        c.execute('INSERT INTO customers (customer_id, shop_id, entry_time, entry_zone, created_at) VALUES (?, ?, ?, ?, ?)',
                  (customer_id, shop_id, entry_time, entry_zone, datetime.now()))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def update_customer_exit(customer_id, exit_time=None, exit_zone=None):
    """Mark customer as exited"""
    conn = get_connection()
    c = conn.cursor()
    if exit_time is None:
        exit_time = datetime.now()
    
    # Get entry time to calculate duration
    c.execute('SELECT entry_time FROM customers WHERE customer_id = ?', (customer_id,))
    row = c.fetchone()
    
    if row:
        entry_time = datetime.fromisoformat(row['entry_time'])
        duration = int((exit_time - entry_time).total_seconds())
        
        c.execute('UPDATE customers SET exit_time = ?, exit_zone = ?, duration = ? WHERE customer_id = ?',
                  (exit_time, exit_zone, duration, customer_id))
        conn.commit()
    
    conn.close()

def add_customer_zone_visit(customer_id, zone_name, enter_time=None):
    """Add customer zone visit"""
    conn = get_connection()
    c = conn.cursor()
    if enter_time is None:
        enter_time = datetime.now()
    
    c.execute('INSERT INTO customer_zones (customer_id, zone_name, enter_time) VALUES (?, ?, ?)',
              (customer_id, zone_name, enter_time))
    conn.commit()
    conn.close()

def update_zone_exit(customer_id, zone_name, exit_time=None):
    """Update zone exit time for customer"""
    conn = get_connection()
    c = conn.cursor()
    if exit_time is None:
        exit_time = datetime.now()
    
    c.execute('SELECT enter_time FROM customer_zones WHERE customer_id = ? AND zone_name = ? AND exit_time IS NULL',
              (customer_id, zone_name))
    row = c.fetchone()
    
    if row:
        enter_time = datetime.fromisoformat(row['enter_time'])
        duration = int((exit_time - enter_time).total_seconds())
        
        c.execute('UPDATE customer_zones SET exit_time = ?, duration = ? WHERE customer_id = ? AND zone_name = ? AND exit_time IS NULL',
                  (exit_time, duration, customer_id, zone_name))
        conn.commit()
    
    conn.close()

def get_customers_today(shop_id):
    """Get all customers from today"""
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT * FROM customers WHERE shop_id = ? AND DATE(entry_time) = ?', (shop_id, today))
    customers = c.fetchall()
    conn.close()
    return customers

def get_active_customers(shop_id):
    """Get currently active customers (no exit time)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM customers WHERE shop_id = ? AND exit_time IS NULL', (shop_id,))
    customers = c.fetchall()
    conn.close()
    return customers

# Zone Functions
def add_zone(shop_id, name, description, x1, y1, x2, y2):
    """Add a new zone"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO zones (shop_id, name, description, x1, y1, x2, y2, enabled, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (shop_id, name, description, x1, y1, x2, y2, True, datetime.now()))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def get_zones(shop_id):
    """Get all zones for shop"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM zones WHERE shop_id = ? AND enabled = ?', (shop_id, True))
    zones = c.fetchall()
    conn.close()
    return zones

def delete_zone(zone_id):
    """Delete a zone"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE zones SET enabled = ? WHERE id = ?', (False, zone_id))
    conn.commit()
    conn.close()

# Camera Functions
def add_camera(shop_id, name, rtsp_url, location, camera_type='', viewing_angle='', brand_model='', 
               ip_address='', port='', night_vision='', recording_quality='1080p', bitrate='', 
               audio_support='', storage_location='', recording_enabled=True):
    """Add a new camera with detailed information"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO cameras (shop_id, name, rtsp_url, location, status, frame_rate, resolution, 
                     camera_type, viewing_angle, brand_model, ip_address, port, night_vision, 
                     recording_quality, bitrate, audio_support, storage_location, recording_enabled, created_at) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (shop_id, name, rtsp_url, location, 'inactive', 30, '1080p', 
                   camera_type, viewing_angle, brand_model, ip_address, port, night_vision,
                   recording_quality, bitrate, audio_support, storage_location, recording_enabled, datetime.now()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def get_cameras(shop_id):
    """Get all cameras for shop"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM cameras WHERE shop_id = ?', (shop_id,))
    cameras = c.fetchall()
    conn.close()
    return cameras

def update_camera(camera_id, name, rtsp_url, location, camera_type='', viewing_angle='', brand_model='', 
                  ip_address='', port='', night_vision='', recording_quality='1080p', bitrate='', 
                  audio_support='', storage_location='', recording_enabled=True):
    """Update camera details"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''UPDATE cameras SET name = ?, rtsp_url = ?, location = ?, camera_type = ?, viewing_angle = ?, 
                     brand_model = ?, ip_address = ?, port = ?, night_vision = ?, recording_quality = ?, 
                     bitrate = ?, audio_support = ?, storage_location = ?, recording_enabled = ? 
                     WHERE id = ?''',
                  (name, rtsp_url, location, camera_type, viewing_angle, brand_model, ip_address, port, 
                   night_vision, recording_quality, bitrate, audio_support, storage_location, recording_enabled, camera_id))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def update_camera_status(camera_id, status):
    """Update camera status"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE cameras SET status = ? WHERE id = ?', (status, camera_id))
    conn.commit()
    conn.close()

# Product Functions
def add_product(shop_id, product_name, category, price, stock_quantity, description=''):
    """Add a new product"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO products (shop_id, product_name, category, price, stock_quantity, description, enabled, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                  (shop_id, product_name, category, price, stock_quantity, description, True, datetime.now()))
        conn.commit()
        product_id = c.lastrowid
        conn.close()
        return product_id
    except Exception as e:
        conn.close()
        return None

def get_products(shop_id):
    """Get all products for shop"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE shop_id = ? AND enabled = ?', (shop_id, True))
    products = c.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id):
    """Get product by ID"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = c.fetchone()
    conn.close()
    return product

def update_product(product_id, product_name, category, price, stock_quantity, description=''):
    """Update product details"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE products SET product_name = ?, category = ?, price = ?, stock_quantity = ?, description = ? WHERE id = ?',
              (product_name, category, price, stock_quantity, description, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    """Delete a product (soft delete)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE products SET enabled = ? WHERE id = ?', (False, product_id))
    conn.commit()
    conn.close()

# Order Functions
def create_order(shop_id, customer_id, total_amount):
    """Create a new order"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO orders (shop_id, customer_id, order_date, total_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                  (shop_id, customer_id, datetime.now(), total_amount, 'completed', datetime.now()))
        conn.commit()
        order_id = c.lastrowid
        conn.close()
        return order_id
    except Exception as e:
        conn.close()
        return None

def add_order_item(order_id, product_id, quantity, unit_price):
    """Add item to order"""
    conn = get_connection()
    c = conn.cursor()
    total_price = quantity * unit_price
    try:
        c.execute('INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                  (order_id, product_id, quantity, unit_price, total_price, datetime.now()))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def get_orders(shop_id, days=None):
    """Get orders for shop"""
    conn = get_connection()
    c = conn.cursor()
    if days:
        date_filter = f"DATE(order_date) >= DATE('now', '-{days} days')"
        c.execute(f'SELECT * FROM orders WHERE shop_id = ? AND {date_filter}', (shop_id,))
    else:
        c.execute('SELECT * FROM orders WHERE shop_id = ?', (shop_id,))
    orders = c.fetchall()
    conn.close()
    return orders

def get_order_items(order_id):
    """Get items for an order"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT oi.*, p.product_name, p.category FROM order_items oi 
                 JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?''', (order_id,))
    items = c.fetchall()
    conn.close()
    return items

def get_monthly_sales(shop_id, year, month):
    """Get sales data for specific month"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT * FROM orders WHERE shop_id = ? AND strftime('%Y', order_date) = ? AND strftime('%m', order_date) = ?''',
              (shop_id, str(year), str(month).zfill(2)))
    orders = c.fetchall()
    conn.close()
    return orders

# Initialize database on import
init_db()
