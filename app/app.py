import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import cv2
import numpy as np
from database import *
from analytics import get_dashboard_summary, get_real_time_data, export_to_csv, get_product_performance, get_best_worst_products, get_most_visited_areas, get_least_visited_areas, get_sales_by_day_of_week, get_monthly_summary, filter_products
from camera_processor import CustomerDetector

# Page config
st.set_page_config(page_title="Shop Analytics", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #0066cc;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'shop_id' not in st.session_state:
    st.session_state.shop_id = None

def login_page():
    """Display login page"""
    st.title("📊 Shop Analytics System")
    st.write("Track customer behavior and shopping patterns in real-time")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            user = get_user(username)
            if user and user['password'] == password:  # In production, use hashed passwords
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.shop_id = user['shop_id']
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        # Demo credentials
        st.info("""
        **Demo Credentials:**
        - Username: demo
        - Password: demo123
        """)
    
    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Choose Username", key="reg_username")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        shop_id = st.text_input("Shop ID", key="shop_id")
        
        if st.button("Register"):
            if add_user(new_username, new_password, new_email, shop_id):
                st.success("Registered successfully! Please login.")
            else:
                st.error("Username already exists")

def dashboard_page():
    """Display main dashboard"""
    st.title("📊 Dashboard")
    
    # Refresh button
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Get data
    summary = get_dashboard_summary(st.session_state.shop_id)
    realtime = get_real_time_data(st.session_state.shop_id)
    
    # Summary metrics
    st.subheader("Today's Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👥 Total Customers", summary['total_customers'])
    with col2:
        avg_minutes = summary['average_dwell_time'] // 60
        st.metric("⏱️ Avg. Dwell Time", f"{avg_minutes} min")
    with col3:
        st.metric("📈 Peak Hours", summary['peak_hours_count'])
    
    # Active customers
    st.subheader("Currently Active Customers")
    st.metric("Active Customers", realtime['active_customer_count'])
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Hourly Customer Flow")
        if summary['hourly_stats']:
            df_hourly = pd.DataFrame(summary['hourly_stats'])
            fig = px.line(df_hourly, x='hour', y='customer_count', markers=True)
            fig.update_xaxes(title_text="Hour of Day")
            fig.update_yaxes(title_text="Customer Count")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Zone Distribution")
        if summary['zone_stats']:
            df_zones = pd.DataFrame(summary['zone_stats'])
            fig = px.pie(df_zones, values='total_customers', names='zone_name')
            st.plotly_chart(fig, use_container_width=True)
    
    # Zone statistics table
    st.subheader("📍 Zone Analytics")
    if summary['zone_stats']:
        df_zones = pd.DataFrame(summary['zone_stats'])
        st.dataframe(df_zones, use_container_width=True)
    
    # Peak hours table
    st.subheader("⏰ Peak Hours")
    if summary['peak_hours']:
        df_peaks = pd.DataFrame(summary['peak_hours'])
        st.dataframe(df_peaks, use_container_width=True)
    
    # Daily trend
    st.subheader("📅 Weekly Trend")
    if summary['daily_trend']:
        df_trend = pd.DataFrame(summary['daily_trend'])
        fig = px.bar(df_trend, x='day', y='count')
        fig.update_xaxes(title_text="Day of Week")
        fig.update_yaxes(title_text="Customer Count")
        st.plotly_chart(fig, use_container_width=True)

def analytics_page():
    """Display detailed analytics"""
    st.title("📈 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date")
    
    if st.button("Apply Filter"):
        # Get customers in date range
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM customers WHERE shop_id = ? AND DATE(entry_time) BETWEEN ? AND ?',
                  (st.session_state.shop_id, start_date, end_date))
        customers = [dict(row) for row in c.fetchall()]
        conn.close()
        
        if customers:
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export as CSV"):
                    csv_data = export_to_csv(st.session_state.shop_id, start_date, end_date)
                    st.download_button("Download CSV", csv_data, "analytics.csv")
            
            with col2:
                if st.button("📥 Export as JSON"):
                    import json
                    json_data = json.dumps(customers, indent=2, default=str)
                    st.download_button("Download JSON", json_data, "analytics.json")
            
            # Display statistics
            st.subheader("Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Customers", len(customers))
            with col2:
                durations = [c['duration'] for c in customers if c.get('duration')]
                avg_duration = sum(durations) / len(durations) if durations else 0
                st.metric("Avg Duration (min)", int(avg_duration / 60))
            with col3:
                st.metric("Date Range", f"{(end_date - start_date).days} days")
            
            # Customer data table
            st.subheader("Customer Data")
            df = pd.DataFrame(customers)
            st.dataframe(df, use_container_width=True)

def cameras_page():
    """Manage cameras"""
    st.title("📹 Cameras")
    
    tab1, tab2 = st.tabs(["View Cameras", "Add Camera"])
    
    with tab1:
        cameras = get_cameras(st.session_state.shop_id)
        if cameras:
            for camera in cameras:
                with st.expander(f"📹 {camera['name']} - {camera['location']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Basic Info**")
                        st.write(f"Status: {camera['status']}")
                        st.write(f"FPS: {camera['frame_rate']}")
                        st.write(f"Recording: {'✅ Enabled' if camera['recording_enabled'] else '❌ Disabled'}")
                    
                    with col2:
                        st.write("**Camera Specs**")
                        st.write(f"Type: {camera['camera_type'] or 'Not specified'}")
                        st.write(f"Brand/Model: {camera['brand_model'] or 'Not specified'}")
                        st.write(f"Viewing Angle: {camera['viewing_angle'] or 'Not specified'}")
                        st.write(f"Night Vision: {camera['night_vision'] or 'Not specified'}")
                    
                    with col3:
                        st.write("**Network & Storage**")
                        st.write(f"IP Address: {camera['ip_address'] or 'Not specified'}")
                        st.write(f"Port: {camera['port'] or 'Not specified'}")
                        st.write(f"Quality: {camera['recording_quality']}")
                        st.write(f"Storage: {camera['storage_location'] or 'Not specified'}")
                    
                    st.write(f"**RTSP URL:** {camera['rtsp_url']}")
                    st.write(f"**Bitrate:** {camera['bitrate'] or 'Auto'}")
                    st.write(f"**Audio:** {'✅ Supported' if camera['audio_support'] else '❌ Not supported'}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Edit Details", key=f"edit_{camera['id']}"):
                            st.session_state.edit_camera_id = camera['id']
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"del_{camera['id']}"):
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute('DELETE FROM cameras WHERE id = ?', (camera['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()
        else:
            st.info("No cameras configured yet")
    
    with tab2:
        st.subheader("Add New Camera")
        
        # Basic Information
        st.write("**📋 Basic Information**")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Camera Name*", placeholder="e.g., Front Entrance Camera")
        with col2:
            location = st.text_input("Location*", placeholder="e.g., Main Entrance")
        
        rtsp_url = st.text_input("RTSP URL", placeholder="rtsp://user:password@host:554/stream")
        
        # Camera Specifications
        st.write("**🎥 Camera Specifications**")
        col1, col2, col3 = st.columns(3)
        with col1:
            camera_type = st.selectbox("Camera Type", 
                                      ["", "IP Camera", "Analog", "Wireless", "PTZ (Pan-Tilt-Zoom)"],
                                      help="Optional: Type of CCTV camera")
        with col2:
            viewing_angle = st.selectbox("Viewing Angle",
                                        ["", "60°", "90°", "120°", "150°", "180°"],
                                        help="Optional: Camera field of view")
        with col3:
            brand_model = st.text_input("Brand/Model", 
                                       placeholder="e.g., Hikvision DS-2CD2143G2-I",
                                       help="Optional: Camera brand and model")
        
        col1, col2 = st.columns(2)
        with col1:
            night_vision = st.selectbox("Night Vision",
                                       ["", "No", "IR 30m", "IR 50m", "IR 100m"],
                                       help="Optional: Infrared night vision capability")
        with col2:
            audio_support = st.checkbox("Audio Support", help="Optional: Does camera have microphone?")
        
        # Network Information
        st.write("**🌐 Network Information**")
        col1, col2 = st.columns(2)
        with col1:
            ip_address = st.text_input("IP Address", 
                                      placeholder="e.g., 192.168.1.100",
                                      help="Optional: Camera network IP")
        with col2:
            port = st.text_input("Port", 
                                placeholder="e.g., 554",
                                help="Optional: Network port number")
        
        # Recording Settings
        st.write("**💾 Recording Settings**")
        col1, col2 = st.columns(2)
        with col1:
            recording_quality = st.selectbox("Recording Quality",
                                            ["720p", "1080p", "2K", "4K"],
                                            index=1,
                                            help="Choose recording resolution")
        with col2:
            bitrate = st.text_input("Bitrate (Kbps)",
                                   placeholder="e.g., 2048",
                                   help="Optional: Recording bitrate")
        
        storage_location = st.selectbox("Storage Location",
                                       ["", "Local Storage", "NVR", "Cloud", "Hybrid"],
                                       help="Optional: Where recordings are stored")
        
        recording_enabled = st.checkbox("Enable Recording", value=True, 
                                       help="Enable video recording by default?")
        
        if st.button("Add Camera"):
            if name and location:
                try:
                    if add_camera(
                        shop_id=st.session_state.shop_id,
                        name=name,
                        rtsp_url=rtsp_url,
                        location=location,
                        camera_type=camera_type,
                        viewing_angle=viewing_angle,
                        brand_model=brand_model,
                        ip_address=ip_address,
                        port=port,
                        night_vision=night_vision,
                        recording_quality=recording_quality,
                        bitrate=bitrate,
                        audio_support='Yes' if audio_support else 'No',
                        storage_location=storage_location,
                        recording_enabled=recording_enabled
                    ):
                        st.success("✅ Camera added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add camera")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.error("Please enter Camera Name and Location")

def zones_page():
    """Manage shop zones"""
    st.title("📍 Shop Zones")
    
    tab1, tab2 = st.tabs(["View Zones", "Add Zone"])
    
    with tab1:
        zones = get_zones(st.session_state.shop_id)
        if zones:
            for zone in zones:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"**{zone['name']}**")
                    st.write(f"Description: {zone['description']}")
                    st.write(f"Coordinates: X({zone['x1']}-{zone['x2']}), Y({zone['y1']}-{zone['y2']})")
                with col2:
                    if st.button("Delete", key=f"del_zone_{zone['id']}"):
                        delete_zone(zone['id'])
                        st.rerun()
                st.divider()
        else:
            st.info("No zones configured yet")
    
    with tab2:
        st.subheader("Add New Zone")
        zone_name = st.text_input("Zone Name", placeholder="e.g., Electronics")
        description = st.text_input("Description", placeholder="Zone description")
        
        col1, col2 = st.columns(2)
        with col1:
            x1 = st.number_input("X1 (Top-Left)", value=0)
            y1 = st.number_input("Y1 (Top-Left)", value=0)
        with col2:
            x2 = st.number_input("X2 (Bottom-Right)", value=100)
            y2 = st.number_input("Y2 (Bottom-Right)", value=100)
        
        if st.button("Add Zone"):
            if add_zone(st.session_state.shop_id, zone_name, description, int(x1), int(y1), int(x2), int(y2)):
                st.success("Zone added successfully!")
                st.rerun()
            else:
                st.error("Failed to add zone")

def products_page():
    """Manage products"""
    st.title("🛍️ Products Management")
    
    tab1, tab2, tab3 = st.tabs(["View Products", "Add Product", "Filter Products"])
    
    with tab1:
        products = get_products(st.session_state.shop_id)
        if products:
            for product in products:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{product['product_name']}**")
                    st.write(f"Category: {product['category']}")
                    st.write(f"Price: ${product['price']:.2f}")
                    st.write(f"Stock: {product['stock_quantity']} units")
                    if product['description']:
                        st.write(f"Description: {product['description']}")
                with col2:
                    if st.button("Edit", key=f"edit_{product['id']}"):
                        st.session_state.edit_product_id = product['id']
                        st.rerun()
                with col3:
                    if st.button("Delete", key=f"del_product_{product['id']}"):
                        delete_product(product['id'])
                        st.success("Product deleted!")
                        st.rerun()
                st.divider()
        else:
            st.info("No products added yet")
    
    with tab2:
        st.subheader("Add New Product")
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name", placeholder="e.g., iPhone 15")
            price = st.number_input("Price ($)", min_value=0.0, step=0.01)
        
        with col2:
            category = st.text_input("Category", placeholder="e.g., Electronics")
            stock = st.number_input("Stock Quantity", min_value=0, step=1)
        
        description = st.text_area("Description", placeholder="Product description...")
        
        if st.button("Add Product"):
            if product_name and category and price > 0:
                product_id = add_product(st.session_state.shop_id, product_name, category, price, stock, description)
                if product_id:
                    st.success("Product added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add product")
            else:
                st.error("Please fill in all required fields")
    
    with tab3:
        st.subheader("Filter Products")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categories = [p['category'] for p in get_products(st.session_state.shop_id)]
            categories = list(set(categories))
            selected_category = st.selectbox("Category", ["All"] + categories)
        
        with col2:
            min_price = st.number_input("Min Price ($)", min_value=0.0, step=0.01)
        
        with col3:
            max_price = st.number_input("Max Price ($)", min_value=0.0, step=0.01, value=10000.0)
        
        if st.button("Apply Filters"):
            category = None if selected_category == "All" else selected_category
            filtered_products = filter_products(st.session_state.shop_id, category, min_price if min_price > 0 else None, max_price if max_price < 10000 else None)
            
            if filtered_products:
                st.subheader(f"Found {len(filtered_products)} products")
                df = pd.DataFrame(filtered_products)
                st.dataframe(df[['product_name', 'category', 'price', 'stock_quantity']], use_container_width=True)
            else:
                st.info("No products match the selected filters")

def monthly_analysis_page():
    """Monthly analysis dashboard"""
    st.title("📊 Monthly Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        current_month = datetime.now().month
        current_year = datetime.now().year
        selected_month = st.selectbox("Month", list(range(1, 13)), index=current_month - 1)
    with col2:
        selected_year = st.number_input("Year", value=current_year, min_value=2020)
    
    if st.button("Generate Report"):
        # Monthly summary
        st.subheader("Monthly Summary")
        summary = get_monthly_summary(st.session_state.shop_id, selected_month, selected_year)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Revenue", f"${summary['total_revenue']:.2f}")
        with col2:
            st.metric("📦 Total Orders", summary['total_orders'])
        with col3:
            st.metric("👥 Total Customers", summary['total_customers'])
        with col4:
            st.metric("📈 Avg Order Value", f"${summary['average_order_value']:.2f}")
        
        # Best and worst products
        st.subheader("Product Performance")
        best_worst = get_best_worst_products(st.session_state.shop_id, selected_month, selected_year)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Selling Products")
            if best_worst['best_products']:
                df_best = pd.DataFrame(best_worst['best_products'])
                st.dataframe(df_best[['product_name', 'category', 'total_units', 'total_revenue']], use_container_width=True)
            else:
                st.info("No sales data available")
        
        with col2:
            st.subheader("📉 Worst Selling Products")
            if best_worst['worst_products']:
                df_worst = pd.DataFrame(best_worst['worst_products'])
                st.dataframe(df_worst[['product_name', 'category', 'total_units', 'total_revenue']], use_container_width=True)
            else:
                st.info("No sales data available")
        
        # Sales by day of week
        st.subheader("Sales by Day of Week")
        sales_by_day = get_sales_by_day_of_week(st.session_state.shop_id, selected_year, selected_month)
        
        if sales_by_day:
            df_days = pd.DataFrame(sales_by_day)
            fig = px.bar(df_days, x='day_name', y='total_revenue', title='Revenue by Day of Week')
            fig.update_xaxes(title_text="Day of Week")
            fig.update_yaxes(title_text="Revenue ($)")
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_days, use_container_width=True)
        else:
            st.info("No sales data for this month")
        
        # Most and least visited areas
        st.subheader("Zone Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 Most Visited Areas")
            most_visited = get_most_visited_areas(st.session_state.shop_id, limit=5)
            if most_visited:
                df_most = pd.DataFrame(most_visited)
                st.dataframe(df_most[['zone_name', 'visitor_count', 'avg_dwell_time']], use_container_width=True)
            else:
                st.info("No visitor data available")
        
        with col2:
            st.subheader("❄️ Least Visited Areas")
            least_visited = get_least_visited_areas(st.session_state.shop_id, limit=5)
            if least_visited:
                df_least = pd.DataFrame(least_visited)
                st.dataframe(df_least[['zone_name', 'visitor_count', 'avg_dwell_time']], use_container_width=True)
            else:
                st.info("No visitor data available")

# Main app
if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title(f"Welcome, {st.session_state.user}!")
    st.sidebar.write(f"Shop ID: {st.session_state.shop_id}")
    
    page = st.sidebar.radio("Navigation", ["Dashboard", "Analytics", "Products", "Monthly Analysis", "Cameras", "Zones", "Logout"])
    
    if page == "Dashboard":
        dashboard_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Products":
        products_page()
    elif page == "Monthly Analysis":
        monthly_analysis_page()
    elif page == "Cameras":
        cameras_page()
    elif page == "Zones":
        zones_page()
    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.shop_id = None
        st.rerun()
