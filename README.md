# 📊 Shop Analytics System - Python Edition

A complete Python-based customer analytics system that tracks shopping patterns, dwell time, and zone-specific behavior using computer vision and real-time analytics.

## Features

✅ **Real-time Customer Detection** - OpenCV-based person detection and tracking
✅ **Zone Analytics** - Track customer time spent in specific shop sections
✅ **Peak Hour Analysis** - Identify busiest shopping hours
✅ **Customer Flow** - Visualize hourly customer patterns
✅ **Dwell Time Tracking** - Measure average time customers spend shopping
✅ **Weekly Trends** - Monitor customer trends across days
✅ **Data Export** - Export analytics as CSV or JSON
✅ **Multi-Camera Support** - Configure multiple camera streams
✅ **Web Dashboard** - Interactive Streamlit dashboard (100% Python!)

## Technology Stack

- **Frontend**: Streamlit (Pure Python web dashboard)
- **Backend**: Python with Flask support
- **Database**: SQLite
- **Computer Vision**: OpenCV
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **No HTML/CSS/JS**: Everything is Python!

## Installation

### 1. Clone/Setup the Project

```bash
cd c:\Thanvi\Shopping
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Run the Dashboard

```bash
streamlit run app\app.py
```

The application will open at `http://localhost:8501`

### Default Demo Credentials

- **Username**: demo
- **Password**: demo123

Or register with any credentials (shop_id required)

## Project Structure

```
Shopping/
├── app/
│   ├── app.py                 # Main Streamlit dashboard application
│   ├── database.py            # SQLite database operations
│   ├── analytics.py           # Analytics calculations
│   ├── camera_processor.py    # OpenCV camera processing & customer detection
│   └── shop_analytics.db      # SQLite database (auto-created)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── setup.py                   # Setup script (optional)
```

## Core Modules

### database.py
SQLite database management with functions for:
- User authentication
- Customer tracking
- Zone management
- Camera configuration
- Analytics data storage

### camera_processor.py
OpenCV-based computer vision with:
- Person detection using background subtraction
- Customer tracking across frames
- Zone assignment logic
- Motion detection

### analytics.py
Analytics calculation functions:
- Hourly statistics
- Zone statistics
- Peak hour identification
- Weekly trends
- Data export

### app.py
Streamlit dashboard with pages for:
- Login/Registration
- Dashboard (real-time metrics & charts)
- Analytics (date range analysis & export)
- Camera management
- Zone configuration

## Dashboard Features

### 📊 Dashboard Page
- **Summary Metrics**: Total customers, avg dwell time, peak hours
- **Hourly Flow Chart**: Line chart showing customer distribution by hour
- **Zone Distribution**: Pie chart of customers across zones
- **Zone Analytics**: Table with detailed zone statistics
- **Peak Hours Table**: Hourly data for identified peaks
- **Weekly Trend**: Bar chart showing customer count by day

### 📈 Analytics Page
- **Date Range Filter**: Analyze data for specific periods
- **Export Options**: Download data as CSV or JSON
- **Statistics Summary**: Total customers, average duration
- **Full Data Table**: Browse all customer records

### 📹 Cameras Page
- **View Cameras**: List all configured cameras with status
- **Add Camera**: Register new RTSP streams
- **Delete Camera**: Remove camera configuration

### 📍 Zones Page
- **View Zones**: Display all defined shop zones
- **Add Zone**: Define rectangular zones by coordinates
- **Delete Zone**: Remove zone configuration

## Key Algorithms

### Customer Detection
Uses OpenCV morphological operations and contour detection:
1. Resize frame for faster processing
2. Convert to grayscale
3. Apply Gaussian blur
4. Morphological closing
5. Find contours
6. Filter by area (300-50000 pixels)

### Customer Tracking
Centroid distance tracking:
- Match detections with existing tracks (50px threshold)
- Create new tracks for unmatched detections
- Remove tracks after 30 frames of no detection

### Zone Assignment
Bounding box intersection:
- Check if customer centroid is within zone coordinates
- Update zone history when entering/exiting
- Calculate dwell time per zone

## Database Schema

### Users Table
- id, username, password, email, shop_id, role, created_at

### Customers Table
- id, customer_id, shop_id, entry_time, exit_time, duration, entry_zone, exit_zone

### Customer Zones Table
- id, customer_id, zone_name, enter_time, exit_time, duration

### Zones Table
- id, shop_id, name, description, x1, y1, x2, y2, enabled, created_at

### Cameras Table
- id, shop_id, name, rtsp_url, location, status, frame_rate, resolution, created_at

### Analytics Table
- id, shop_id, date, hour, total_customers, avg_spend_time, peak_time, created_at

## API Data Endpoints

The system includes analytics functions that can be called from Python:

```python
from analytics import *

# Get dashboard summary
summary = get_dashboard_summary('shop_id')

# Get real-time data
realtime = get_real_time_data('shop_id')

# Export data
csv_data = export_to_csv('shop_id', '2024-01-01', '2024-01-31')
```

## Camera Setup

### RTSP Stream Configuration

Add cameras with RTSP URLs:
```
rtsp://username:password@192.168.1.100:554/stream
rtsp://camera_name:password@192.168.1.101/live
```

### Supported Camera Formats
- Any IP camera with RTSP stream support
- USB webcams (convert to local stream if needed)
- Video files for testing

## Configuration & Customization

### Edit Detection Thresholds
In `camera_processor.py`:
- `MIN_AREA`: Minimum pixels to consider a person
- `MAX_AREA`: Maximum pixels for person detection
- `MAX_TRACKING_DISTANCE`: Tracking distance threshold
- `CONFIDENCE_THRESHOLD`: Detection confidence level

### Modify UI Colors/Look
Edit Streamlit theme in the `st.markdown()` CSS section in `app.py`

### Change Database Location
Edit `DB_PATH` in `database.py`:
```python
DB_PATH = Path('your/custom/path/database.db')
```

## Troubleshooting

### Streamlit Not Loading
```bash
pip install --upgrade streamlit
streamlit run app\app.py --logger.level=debug
```

### Database Locked Error
Delete `shop_analytics.db` and restart (will recreate empty database)

### OpenCV Issues
```bash
pip install --upgrade opencv-python numpy
```

### Memory Issues with Video
- Reduce frame resolution in camera settings
- Increase frame skip rate
- Close other applications

## Performance Tips

- Use H.264 encoded RTSP streams for better performance
- Set appropriate zone sizes (avoid overlapping zones)
- Limit zones to 5-10 for 1080p streams
- Use frame skipping for cameras with high FPS

## Future Enhancements

- [ ] Machine learning for customer classification
- [ ] Heatmap generation
- [ ] Customer re-identification across days
- [ ] Predictive analytics
- [ ] Email reports
- [ ] Mobile app integration
- [ ] Multi-shop dashboard
- [ ] Advanced filtering options

## License

Open Source - Feel free to modify and use

## Support

For issues or questions, check the database with:
```python
from database import *
conn = get_connection()
print(conn.execute('SELECT * FROM customers').fetchall())
```

---

**Created**: April 2024
**Version**: 1.0.0
**Language**: 100% Python 🐍
