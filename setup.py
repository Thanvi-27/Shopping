"""
Setup script to initialize demo data for Shop Analytics System
Run this before first use to populate the database with sample data
"""

from app.database import *
from datetime import datetime, timedelta
import random

def setup_demo_data():
    """Initialize database with demo data"""
    
    print("🔧 Initializing Shop Analytics System...")
    
    # Add demo user
    print("👤 Adding demo user...")
    add_user('demo', 'demo123', 'demo@shop.com', 'SHOP001', 'owner')
    
    # Add sample zones
    print("📍 Adding sample zones...")
    zones_data = [
        ('SHOP001', 'Entrance', 'Main entrance area', 0, 0, 200, 150),
        ('SHOP001', 'Electronics', 'Electronics section', 200, 0, 400, 200),
        ('SHOP001', 'Checkout', 'Checkout counters', 100, 400, 300, 500),
        ('SHOP001', 'Clothing', 'Clothing department', 0, 200, 200, 400),
    ]
    
    for shop_id, name, desc, x1, y1, x2, y2 in zones_data:
        add_zone(shop_id, name, desc, x1, y1, x2, y2)
    
    # Add sample cameras
    print("📹 Adding sample cameras...")
    add_camera('SHOP001', 'Main Camera', 'rtsp://camera1:pass@192.168.1.100:554/stream', 'Main Entrance')
    add_camera('SHOP001', 'Electronics Camera', 'rtsp://camera2:pass@192.168.1.101:554/stream', 'Electronics Section')
    
    # Add sample customers
    print("👥 Adding sample customer data...")
    base_time = datetime.now() - timedelta(days=7)
    
    for day in range(7):
        current_date = base_time + timedelta(days=day)
        
        # Simulate customers throughout the day
        for hour in range(9, 21):  # 9 AM to 9 PM
            num_customers = random.randint(5, 20) if hour in [12, 13, 18, 19] else random.randint(2, 10)
            
            for i in range(num_customers):
                customer_id = f"CUST_{day}_{hour}_{i}"
                entry_time = current_date.replace(hour=hour, minute=random.randint(0, 59))
                
                add_customer(customer_id, 'SHOP001', random.choice([z[1] for z in zones_data]), entry_time)
                
                # Add zone visits
                num_zones = random.randint(2, 4)
                for zone_idx in range(num_zones):
                    zone_name = random.choice([z[1] for z in zones_data])
                    zone_entry = entry_time + timedelta(minutes=random.randint(5, 30))
                    add_customer_zone_visit(customer_id, zone_name, zone_entry)
                    
                    # Mark zone exit
                    zone_exit = zone_entry + timedelta(minutes=random.randint(5, 25))
                    update_zone_exit(customer_id, zone_name, zone_exit)
                
                # Mark customer exit
                exit_time = entry_time + timedelta(minutes=random.randint(15, 120))
                update_customer_exit(customer_id, exit_time, random.choice([z[1] for z in zones_data]))
    
    print("✅ Demo data setup complete!")
    print("\n📊 Dashboard Statistics:")
    print("   - 1 Demo User (demo/demo123)")
    print("   - 4 Shop Zones")
    print("   - 2 Sample Cameras")
    print("   - 7 Days of Customer Data (simulated)")
    print("   - 500+ Sample Customers")

if __name__ == '__main__':
    # Clear existing data
    import os
    db_path = 'app/shop_analytics.db'
    if os.path.exists(db_path):
        print("⚠️  Existing database found. Backing up...")
        os.rename(db_path, f"{db_path}.backup")
    
    # Initialize fresh database
    init_db()
    
    # Add demo data
    setup_demo_data()
    
    print("\n🎉 Ready to use! Run: streamlit run app/app.py")
