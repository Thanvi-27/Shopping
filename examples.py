"""
Example script showing how to use Shop Analytics System programmatically
Run from Python interpreter or as standalone script
"""

import sys
from pathlib import Path

# Add app directory to path
app_path = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_path))

from database import *
from analytics import *
from camera_processor import CustomerDetector
import cv2
from datetime import datetime, timedelta

def example_1_database_operations():
    """Example 1: Basic database operations"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Database Operations")
    print("="*60)
    
    # Add a new user
    print("\n[+] Adding new user...")
    add_user('shop_owner', 'secure_password', 'owner@shop.com', 'SHOP002', 'owner')
    
    # Get user
    print("[+] Retrieving user...")
    user = get_user('shop_owner')
    print(f"    User found: {user['username']} | Shop: {user['shop_id']}")
    
    # Add zones
    print("[+] Adding zones...")
    add_zone('SHOP002', 'Entrance', 'Front entrance', 0, 0, 100, 50)
    add_zone('SHOP002', 'Aisles', 'Product aisles', 0, 50, 100, 150)
    add_zone('SHOP002', 'Checkout', 'Checkout area', 0, 150, 100, 200)
    
    # Get zones
    print("[+] Retrieving zones...")
    zones = get_zones('SHOP002')
    print(f"    Total zones: {len(zones)}")
    for zone in zones:
        print(f"      - {zone['name']}: ({zone['x1']},{zone['y1']}) to ({zone['x2']},{zone['y2']})")

def example_2_customer_tracking():
    """Example 2: Customer tracking"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Customer Tracking")
    print("="*60)
    
    # Add customers
    print("\n[+] Adding customer records...")
    for i in range(5):
        customer_id = f"TEST_CUSTOMER_{i:03d}"
        add_customer(customer_id, 'SHOP002', 'Entrance')
        
        # Simulate zone visits
        zones = ['Entrance', 'Aisles', 'Checkout']
        for zone in zones:
            add_customer_zone_visit(customer_id, zone)
        
        print(f"    Added: {customer_id}")
    
    # Get active customers
    print("\n[+] Retrieving active customers...")
    active = get_active_customers('SHOP002')
    print(f"    Active customers: {len(active)}")
    for cust in active:
        print(f"      - {cust['customer_id']} (Entry: {cust['entry_time']})")

def example_3_analytics():
    """Example 3: Analytics calculations"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Analytics Calculations")
    print("="*60)
    
    print("\n[+] Getting dashboard summary...")
    summary = get_dashboard_summary('SHOP002')
    
    print(f"    Total Customers: {summary['total_customers']}")
    print(f"    Average Dwell Time: {summary['average_dwell_time']} seconds")
    print(f"    Peak Hours Count: {summary['peak_hours_count']}")
    
    print("\n[+] Hourly statistics:")
    for stat in summary['hourly_stats'][:5]:
        print(f"      Hour {stat['hour']:02d}:00 - {stat['customer_count']} customers")
    
    print("\n[+] Zone statistics:")
    for zone in summary['zone_stats']:
        print(f"      {zone['zone_name']}: {zone['total_customers']} visits, " +
              f"Avg dwell: {zone['average_dwell_time']}s, " +
              f"Footfall: {zone['footfall_percentage']}%")

def example_4_real_time():
    """Example 4: Real-time data"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Real-time Data")
    print("="*60)
    
    print("\n[+] Getting real-time data...")
    realtime = get_real_time_data('SHOP002')
    
    print(f"    Active customers: {realtime['active_customer_count']}")
    if realtime['active_customer_count'] > 0:
        print("    Active customer list:")
        for cust in realtime['active_customers'][:5]:
            print(f"      - {cust['customer_id']}")

def example_5_camera_detection():
    """Example 5: Camera detection (simulated)"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Camera Detection (Simulated)")
    print("="*60)
    
    # Create detector
    detector = CustomerDetector()
    print("\n[+] CustomerDetector initialized")
    
    # Create a dummy frame (grayscale image)
    dummy_frame = cv2.imread('camera.png') if Path('camera.png').exists() else None
    
    if dummy_frame is None:
        print("    Note: No camera image available for demo")
        print("    Creating synthetic frame for demo...")
        dummy_frame = cv2.ones((480, 640, 3), dtype='uint8') * 50
        # Add some white rectangles to simulate objects
        cv2.rectangle(dummy_frame, (100, 100), (150, 200), (255, 255, 255), -1)
        cv2.rectangle(dummy_frame, (300, 150), (350, 250), (255, 255, 255), -1)
    
    print(f"    Frame shape: {dummy_frame.shape}")
    
    # Get zones
    zones_list = get_zones('SHOP002')
    zones_dict = [{'name': z['name'], 'x1': z['x1'], 'y1': z['y1'], 'x2': z['x2'], 'y2': z['y2']} 
                  for z in zones_list]
    
    # Process frame
    print("\n[+] Processing frame...")
    result = detector.process_frame(dummy_frame, zones_dict)
    
    if result:
        print(f"    Detections found: {len(result['detections'])}")
        print(f"    Customers tracked: {len(result['customers_in_frame'])}")
        print(f"    Frame count: {result['frame_count']}")

def example_6_export_data():
    """Example 6: Export data"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Data Export")
    print("="*60)
    
    # Export to CSV
    print("\n[+] Exporting to CSV...")
    start = datetime.now().strftime('%Y-%m-%d')
    end = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    csv_data = export_to_csv('SHOP002', start, end)
    print("    CSV generated (first 5 lines):")
    for line in csv_data.split('\n')[:5]:
        print(f"      {line}")

def example_7_camera_management():
    """Example 7: Camera management"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Camera Management")
    print("="*60)
    
    # Add cameras
    print("\n[+] Adding cameras...")
    add_camera('SHOP002', 'Entrance Camera', 'rtsp://entrance.local/stream', 'Main Entrance')
    add_camera('SHOP002', 'Aisle Camera', 'rtsp://aisles.local/stream', 'Product Aisles')
    
    # Get cameras
    print("[+] Retrieving cameras...")
    cameras = get_cameras('SHOP002')
    print(f"    Total cameras: {len(cameras)}")
    for cam in cameras:
        print(f"      - {cam['name']}: {cam['status']} | {cam['location']}")
    
    # Update camera status
    if cameras:
        print("\n[+] Updating first camera status...")
        update_camera_status(cameras[0]['id'], 'active')
        print(f"    Camera {cameras[0]['name']} status updated to: active")

def main():
    """Run all examples"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " SHOP ANALYTICS SYSTEM - USAGE EXAMPLES ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Run examples
        example_1_database_operations()
        example_2_customer_tracking()
        example_3_analytics()
        example_4_real_time()
        example_5_camera_detection()
        example_6_export_data()
        example_7_camera_management()
        
        print("\n" + "="*60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\n📚 Next steps:")
        print("   1. Run: streamlit run app/app.py")
        print("   2. Login with: demo / demo123")
        print("   3. Explore the dashboard")
        print("   4. Add your own cameras and zones")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
