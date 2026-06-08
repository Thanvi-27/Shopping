from datetime import datetime
from database import get_connection

def calculate_hourly_stats(customers):
    """Calculate statistics by hour"""
    hourly_data = {}
    
    for customer in customers:
        if customer.get('entry_time'):
            entry_time = datetime.fromisoformat(customer['entry_time']) if isinstance(customer['entry_time'], str) else customer['entry_time']
            hour = entry_time.hour
            
            if hour not in hourly_data:
                hourly_data[hour] = {'count': 0, 'total_duration': 0}
            
            hourly_data[hour]['count'] += 1
            if customer.get('duration'):
                hourly_data[hour]['total_duration'] += customer['duration']
    
    hourly_stats = []
    for hour in sorted(hourly_data.keys()):
        data = hourly_data[hour]
        hourly_stats.append({
            'hour': hour,
            'customer_count': data['count'],
            'average_dwell_time': int(data['total_duration'] / data['count']) if data['count'] > 0 else 0
        })
    
    return hourly_stats

def calculate_zone_stats(customers, zones):
    """Calculate statistics for each zone"""
    zone_names = [z['name'] for z in zones]
    zone_stats = {name: {'total_customers': 0, 'total_dwell_time': 0} for name in zone_names}
    
    conn = get_connection()
    c = conn.cursor()
    
    # Get zone visits from database
    for customer_id in [c['customer_id'] for c in customers]:
        c.execute('SELECT zone_name, duration FROM customer_zones WHERE customer_id = ? AND duration IS NOT NULL', (customer_id,))
        rows = c.fetchall()
        
        for row in rows:
            zone_name = row['zone_name']
            if zone_name in zone_stats:
                zone_stats[zone_name]['total_customers'] += 1
                zone_stats[zone_name]['total_dwell_time'] += row['duration']
    
    conn.close()
    
    zone_results = []
    total_customers = len(customers)
    
    for zone in zones:
        stats = zone_stats[zone['name']]
        avg_dwell = stats['total_dwell_time'] / stats['total_customers'] if stats['total_customers'] > 0 else 0
        footfall_pct = (stats['total_customers'] / total_customers * 100) if total_customers > 0 else 0
        
        zone_results.append({
            'zone_name': zone['name'],
            'total_customers': stats['total_customers'],
            'average_dwell_time': int(avg_dwell),
            'footfall_percentage': round(footfall_pct)
        })
    
    return zone_results

def calculate_peak_hours(hourly_stats):
    """Identify peak hours"""
    if not hourly_stats:
        return []
    
    avg_customers = sum(h['customer_count'] for h in hourly_stats) / len(hourly_stats)
    peak_hours = [h for h in hourly_stats if h['customer_count'] > avg_customers]
    
    return peak_hours

def calculate_daily_trend(customers):
    """Calculate customer count by day of week"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_stats = {i: 0 for i in range(7)}
    
    for customer in customers:
        if customer.get('entry_time'):
            entry_time = datetime.fromisoformat(customer['entry_time']) if isinstance(customer['entry_time'], str) else customer['entry_time']
            day = entry_time.weekday()
            day_stats[day] += 1
    
    trend = []
    for day_num in range(7):
        trend.append({
            'day': days[day_num],
            'count': day_stats[day_num]
        })
    
    return trend

def get_dashboard_summary(shop_id):
    """Get dashboard summary data"""
    conn = get_connection()
    c = conn.cursor()
    
    # Get today's customers
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT * FROM customers WHERE shop_id = ? AND DATE(entry_time) = ?', (shop_id, today))
    customers = c.fetchall()
    
    # Calculate metrics
    total_customers = len(customers)
    
    # Average dwell time
    durations = [cust['duration'] for cust in customers if cust.get('duration')]
    avg_dwell_time = sum(durations) / len(durations) if durations else 0
    
    # Get hourly stats
    c.execute('SELECT * FROM zones WHERE shop_id = ? AND enabled = ?', (shop_id, True))
    zones = c.fetchall()
    zones = [dict(z) for z in zones]
    
    conn.close()
    
    customers = [dict(c) for c in customers]
    hourly_stats = calculate_hourly_stats(customers)
    zone_stats = calculate_zone_stats(customers, zones)
    peak_hours = calculate_peak_hours(hourly_stats)
    daily_trend = calculate_daily_trend(customers)
    
    return {
        'total_customers': total_customers,
        'average_dwell_time': int(avg_dwell_time),
        'peak_hours_count': len(peak_hours),
        'hourly_stats': hourly_stats,
        'zone_stats': zone_stats,
        'peak_hours': peak_hours,
        'daily_trend': daily_trend
    }

def get_real_time_data(shop_id):
    """Get real-time analytics"""
    conn = get_connection()
    c = conn.cursor()
    
    # Active customers
    c.execute('SELECT * FROM customers WHERE shop_id = ? AND exit_time IS NULL', (shop_id,))
    active = c.fetchall()
    
    active_count = len(active)
    active_customers = [dict(a) for a in active]
    
    conn.close()
    
    return {
        'active_customer_count': active_count,
        'active_customers': active_customers
    }

def export_to_csv(shop_id, start_date, end_date):
    """Export analytics data to CSV format"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''SELECT * FROM customers WHERE shop_id = ? AND DATE(entry_time) BETWEEN ? AND ?''',
              (shop_id, start_date, end_date))
    customers = c.fetchall()
    conn.close()
    
    csv_data = "Customer ID,Entry Time,Exit Time,Duration (sec),Zones Visited\n"
    
    for customer in customers:
        zones_visited = 0
        csv_data += f"{customer['customer_id']},\"{customer['entry_time']}\",\"{customer['exit_time']}\",{customer['duration']},{zones_visited}\n"
    
    return csv_data

def get_product_performance(shop_id, days=30):
    """Get product performance analytics"""
    conn = get_connection()
    c = conn.cursor()
    
    # Get sales in last N days
    c.execute('''
        SELECT oi.product_id, p.product_name, p.category, p.price, 
               COUNT(oi.id) as total_units, SUM(oi.total_price) as total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        WHERE o.shop_id = ? AND DATE(o.order_date) >= DATE('now', '-' || ? || ' days')
        GROUP BY oi.product_id
        ORDER BY total_revenue DESC
    ''', (shop_id, days))
    
    products = c.fetchall()
    conn.close()
    
    return [dict(p) for p in products]

def get_best_worst_products(shop_id, month=None, year=None):
    """Get best and worst selling products"""
    conn = get_connection()
    c = conn.cursor()
    
    if month and year:
        query = '''
            SELECT oi.product_id, p.product_name, p.category, p.price, 
                   COUNT(oi.id) as total_units, SUM(oi.total_price) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.shop_id = ? AND strftime('%Y', o.order_date) = ? AND strftime('%m', o.order_date) = ?
            GROUP BY oi.product_id
            ORDER BY total_revenue DESC
        '''
        c.execute(query, (shop_id, str(year), str(month).zfill(2)))
    else:
        query = '''
            SELECT oi.product_id, p.product_name, p.category, p.price, 
                   COUNT(oi.id) as total_units, SUM(oi.total_price) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.shop_id = ?
            GROUP BY oi.product_id
            ORDER BY total_revenue DESC
        '''
        c.execute(query, (shop_id,))
    
    products = c.fetchall()
    conn.close()
    
    products = [dict(p) for p in products]
    return {
        'best_products': products[:5] if len(products) > 5 else products,
        'worst_products': products[-5:][::-1] if len(products) > 5 else []
    }

def get_product_by_category(shop_id, category):
    """Get product sales by category"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT oi.product_id, p.product_name, p.category, p.price, 
               COUNT(oi.id) as total_units, SUM(oi.total_price) as total_revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        WHERE o.shop_id = ? AND p.category = ?
        GROUP BY oi.product_id
        ORDER BY total_revenue DESC
    ''', (shop_id, category))
    
    products = c.fetchall()
    conn.close()
    
    return [dict(p) for p in products]

def get_most_visited_areas(shop_id, limit=5):
    """Get most visited zones (areas)"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT zone_name, COUNT(*) as visitor_count, AVG(duration) as avg_dwell_time
        FROM customer_zones
        WHERE customer_id IN (SELECT customer_id FROM customers WHERE shop_id = ?)
        GROUP BY zone_name
        ORDER BY visitor_count DESC
        LIMIT ?
    ''', (shop_id, limit))
    
    areas = c.fetchall()
    conn.close()
    
    return [dict(a) for a in areas]

def get_least_visited_areas(shop_id, limit=5):
    """Get least visited zones (areas)"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT zone_name, COUNT(*) as visitor_count, AVG(duration) as avg_dwell_time
        FROM customer_zones
        WHERE customer_id IN (SELECT customer_id FROM customers WHERE shop_id = ?)
        GROUP BY zone_name
        ORDER BY visitor_count ASC
        LIMIT ?
    ''', (shop_id, limit))
    
    areas = c.fetchall()
    conn.close()
    
    return [dict(a) for a in areas]

def get_sales_by_day_of_week(shop_id, year=None, month=None):
    """Get sales broken down by day of week"""
    conn = get_connection()
    c = conn.cursor()
    
    if month and year:
        query = '''
            SELECT strftime('%w', o.order_date) as day_num, 
                   CASE CAST(strftime('%w', o.order_date) AS INTEGER)
                       WHEN 0 THEN 'Sunday'
                       WHEN 1 THEN 'Monday'
                       WHEN 2 THEN 'Tuesday'
                       WHEN 3 THEN 'Wednesday'
                       WHEN 4 THEN 'Thursday'
                       WHEN 5 THEN 'Friday'
                       WHEN 6 THEN 'Saturday'
                   END as day_name,
                   COUNT(DISTINCT o.id) as order_count,
                   SUM(o.total_amount) as total_revenue
            FROM orders o
            WHERE o.shop_id = ? AND strftime('%Y', o.order_date) = ? AND strftime('%m', o.order_date) = ?
            GROUP BY day_num
            ORDER BY day_num
        '''
        c.execute(query, (shop_id, str(year), str(month).zfill(2)))
    else:
        query = '''
            SELECT strftime('%w', o.order_date) as day_num,
                   CASE CAST(strftime('%w', o.order_date) AS INTEGER)
                       WHEN 0 THEN 'Sunday'
                       WHEN 1 THEN 'Monday'
                       WHEN 2 THEN 'Tuesday'
                       WHEN 3 THEN 'Wednesday'
                       WHEN 4 THEN 'Thursday'
                       WHEN 5 THEN 'Friday'
                       WHEN 6 THEN 'Saturday'
                   END as day_name,
                   COUNT(DISTINCT o.id) as order_count,
                   SUM(o.total_amount) as total_revenue
            FROM orders o
            WHERE o.shop_id = ?
            GROUP BY day_num
            ORDER BY day_num
        '''
        c.execute(query, (shop_id,))
    
    sales = c.fetchall()
    conn.close()
    
    return [dict(s) for s in sales]

def get_monthly_summary(shop_id, year, month):
    """Get complete monthly summary"""
    conn = get_connection()
    c = conn.cursor()
    
    # Total revenue
    c.execute('''SELECT SUM(total_amount) as total_revenue FROM orders 
                 WHERE shop_id = ? AND strftime('%Y', order_date) = ? AND strftime('%m', order_date) = ?''',
              (shop_id, str(year), str(month).zfill(2)))
    revenue_row = c.fetchone()
    total_revenue = revenue_row['total_revenue'] or 0
    
    # Total orders
    c.execute('''SELECT COUNT(*) as total_orders FROM orders 
                 WHERE shop_id = ? AND strftime('%Y', order_date) = ? AND strftime('%m', order_date) = ?''',
              (shop_id, str(year), str(month).zfill(2)))
    orders_row = c.fetchone()
    total_orders = orders_row['total_orders']
    
    # Total customers
    c.execute('''SELECT COUNT(*) as total_customers FROM customers 
                 WHERE shop_id = ? AND strftime('%Y', entry_time) = ? AND strftime('%m', entry_time) = ?''',
              (shop_id, str(year), str(month).zfill(2)))
    customers_row = c.fetchone()
    total_customers = customers_row['total_customers']
    
    conn.close()
    
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    return {
        'total_revenue': round(total_revenue, 2),
        'total_orders': total_orders,
        'total_customers': total_customers,
        'average_order_value': round(avg_order_value, 2)
    }

def filter_products(shop_id, category=None, min_price=None, max_price=None):
    """Filter products by multiple criteria"""
    conn = get_connection()
    c = conn.cursor()
    
    query = 'SELECT * FROM products WHERE shop_id = ? AND enabled = ?'
    params = [shop_id, True]
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    if min_price is not None:
        query += ' AND price >= ?'
        params.append(min_price)
    
    if max_price is not None:
        query += ' AND price <= ?'
        params.append(max_price)
    
    c.execute(query, params)
    products = c.fetchall()
    conn.close()
    
    return [dict(p) for p in products]

