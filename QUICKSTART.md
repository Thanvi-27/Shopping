# 🚀 Quick Start Guide

## 1. Installation (5 minutes)

### Windows:
```bash
cd c:\Thanvi\Shopping
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### macOS/Linux:
```bash
cd ~/Thanvi/Shopping
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Setup Demo Data (2 minutes)

```bash
python setup.py
```

This will:
- Create SQLite database
- Add demo user (demo/demo123)
- Add 4 sample zones
- Add 2 sample cameras
- Generate 7 days of customer data

## 3. Run the Application

```bash
streamlit run app/app.py
```

Opens automatically at http://localhost:8501

## 4. Login & Explore

- **Username**: demo
- **Password**: demo123
- View real-time dashboards
- Explore analytics
- Manage cameras and zones

## 5. Add Your Own Data

### Create New User:
1. Click "Register" tab
2. Enter credentials and shop ID
3. Login with new account

### Configure Cameras:
1. Go to "Cameras" page
2. Click "Add Camera"
3. Enter RTSP URL: `rtsp://user:pass@ip:554/stream`
4. Click "Add Camera"

### Define Shop Zones:
1. Go to "Zones" page
2. Click "Add Zone"
3. Enter zone name and pixel coordinates
4. Click "Add Zone"

## 6. How It Works

### Customer Detection Flow:
```
📹 Camera Feed
    ↓
🖼️  OpenCV Processing (frames)
    ↓
👤 Person Detection (background subtraction)
    ↓
📊 Tracking (centroid matching)
    ↓
📍 Zone Assignment (coordinate checking)
    ↓
💾 Store in SQLite
    ↓
📈 Analytics Calculation
    ↓
🎨 Streamlit Dashboard Display
```

### Data Flow:
```
Real-time:
  Customers detected → Tracked → Assigned to zones → Stored in DB

Analysis:
  DB queries → Calculate metrics → Generate charts → Display in dashboard
```

## 7. Key Features

### Dashboard
- **Current customers**: Active shoppers count
- **Hourly flow**: Line chart of customer distribution
- **Zone distribution**: Pie chart showing where people are
- **Peak hours**: Automatically identified busy times
- **Weekly trend**: Customer patterns by day

### Analytics
- **Date range selection**: Filter by dates
- **CSV/JSON export**: Download data
- **Statistics**: Total customers, average dwell time
- **Full data table**: Browse individual customers

### Cameras
- **Add streams**: Configure RTSP cameras
- **Monitor status**: Active/Inactive/Error
- **Delete cameras**: Remove unused streams

### Zones
- **Define areas**: Draw rectangular zones
- **Zone names**: Label sections (Entrance, Electronics, etc)
- **Coordinates**: Pixel-based zone definition
- **Manage zones**: Edit or delete

## 8. Example Use Cases

### Use Case 1: Find Peak Shopping Times
```
Dashboard → View "Hourly Customer Flow" chart
→ Peak hours automatically highlighted
→ Plan staff accordingly
```

### Use Case 2: Analyze Zone Performance
```
Dashboard → View "Zone Analytics" table
→ See which zones get most visits
→ Plan marketing/restocking
```

### Use Case 3: Generate Management Report
```
Analytics → Set date range
→ Click "Export as CSV"
→ Share detailed metrics with management
```

### Use Case 4: Track Dwell Time Trends
```
Analytics → View "Weekly Trend"
→ Compare customer counts by day
→ Identify low-traffic days for promotions
```

## 9. Troubleshooting

### Problem: Streamlit won't start
```bash
pip install --upgrade streamlit
streamlit run app/app.py --logger.level=debug
```

### Problem: Database errors
```bash
# Remove corrupted database
rm app/shop_analytics.db
# Re-run setup
python setup.py
```

### Problem: No customers detected
- Check camera feed is accessible
- Verify RTSP URL format
- Ensure sufficient lighting in shop
- Check zone coordinates are correct

### Problem: High CPU usage
- Reduce frame resolution
- Increase frame skip rate
- Close other applications
- Use H.264 encoded streams

## 10. Advanced Configuration

### Change Detection Sensitivity
Edit `app/camera_processor.py`:
```python
MIN_AREA = 300        # Smaller = more sensitive
MAX_AREA = 50000      # Larger = detects bigger objects
```

### Modify Zone Coordinates
Edit zones via UI or directly in database:
```python
from app.database import *
conn = get_connection()
c = conn.cursor()
c.execute('SELECT * FROM zones')
print(c.fetchall())
```

### Export All Data
```python
from app.analytics import export_to_csv
csv = export_to_csv('SHOP001', '2024-01-01', '2024-12-31')
print(csv)
```

## 11. Performance Optimization

- **Limit zones**: 5-10 zones per camera for best performance
- **Reduce FPS**: Lower frame rate = less CPU usage
- **H.264 encoding**: Use for RTSP streams
- **Close unused apps**: More memory for OpenCV processing

## 12. Next Steps

1. ✅ Install dependencies
2. ✅ Run setup script
3. ✅ Start dashboard
4. ✅ Login with demo account
5. ➡️ Add your cameras
6. ➡️ Define your zones
7. ➡️ Monitor customers
8. ➡️ Analyze trends
9. ➡️ Export reports

---

**Need help?** Check README.md for detailed documentation
