import cv2
import numpy as np
from collections import defaultdict
from datetime import datetime
import threading

class CustomerDetector:
    """Detect and track customers from video feed using OpenCV"""
    
    def __init__(self):
        self.tracked_customers = {}
        self.frame_count = 0
        self.fps = 30
        # Background subtractor for detecting moving people
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True,
            varThreshold=100
        )
        
    def process_frame(self, frame, zones):
        """Process a video frame and detect customers"""
        try:
            detections = self.detect_persons(frame)
            customers_in_frame = self.track_customers(detections)
            zones_data = self.assign_customers_to_zones(customers_in_frame, zones)
            
            return {
                'detections': detections,
                'customers_in_frame': customers_in_frame,
                'zones_data': zones_data,
                'frame_count': self.frame_count
            }
        except Exception as e:
            print(f"Error processing frame: {e}")
            return None
    
    def detect_persons(self, frame):
        """Detect persons in frame using background subtraction"""
        detections = []
        
        try:
            # Resize for faster processing
            resized = cv2.resize(frame, (640, 480))
            
            # Apply background subtraction to get foreground mask
            fg_mask = self.bg_subtractor.apply(resized)
            
            # Remove shadows (shadow pixels are gray in MOG2)
            _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
            
            # Apply morphological operations to clean up the mask
            kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel_open)
            
            kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel_close)
            
            # Dilate to fill gaps
            kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
            fg_mask = cv2.dilate(fg_mask, kernel_dilate, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area (tuned for people detection)
            MIN_AREA = 300
            MAX_AREA = 80000
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if MIN_AREA < area < MAX_AREA:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Filter by aspect ratio (people are taller than wide)
                    aspect_ratio = h / (w + 1)
                    if 0.3 < aspect_ratio < 3.0:
                        # Scale back to original frame
                        xscale = frame.shape[1] / resized.shape[1]
                        yscale = frame.shape[0] / resized.shape[0]
                        
                        detections.append({
                            'id': f"det_{len(detections)}",
                            'x': int(x * xscale),
                            'y': int(y * yscale),
                            'width': int(w * xscale),
                            'height': int(h * yscale),
                            'area': area,
                            'confidence': min(area / MAX_AREA, 1.0)
                        })
        except Exception as e:
            print(f"Error in detect_persons: {e}")
        
        return detections
    
    def track_customers(self, detections):
        """Track customers across frames"""
        customers_in_frame = []
        used_tracked_ids = set()
        MAX_TRACKING_DISTANCE = 50
        CONFIDENCE_THRESHOLD = 0.5
        
        # Match detections with existing tracked customers
        for detection in detections:
            matched = False
            
            for track_id, tracked_customer in list(self.tracked_customers.items()):
                if track_id in used_tracked_ids:
                    continue
                
                distance = self.calculate_distance(
                    {'x': detection['x'], 'y': detection['y']},
                    {'x': tracked_customer['lastX'], 'y': tracked_customer['lastY']}
                )
                
                if distance < MAX_TRACKING_DISTANCE:
                    tracked_customer['lastX'] = detection['x']
                    tracked_customer['lastY'] = detection['y']
                    tracked_customer['frameCount'] += 1
                    used_tracked_ids.add(track_id)
                    matched = True
                    customers_in_frame.append({**tracked_customer, 'currentDetection': detection})
                    break
            
            # New customer detected
            if not matched and detection['confidence'] > CONFIDENCE_THRESHOLD:
                customer_id = f"CUST_{datetime.now().timestamp()}_{len(self.tracked_customers)}"
                new_customer = {
                    'customerId': customer_id,
                    'entryTime': datetime.now(),
                    'lastX': detection['x'],
                    'lastY': detection['y'],
                    'frameCount': 1,
                    'currentZone': None,
                    'zoneHistory': []
                }
                self.tracked_customers[customer_id] = new_customer
                customers_in_frame.append({**new_customer, 'currentDetection': detection})
        
        # Remove lost customers
        for track_id in list(self.tracked_customers.keys()):
            if track_id not in used_tracked_ids:
                tracked_customer = self.tracked_customers[track_id]
                tracked_customer['lostFrameCount'] = tracked_customer.get('lostFrameCount', 0) + 1
                
                if tracked_customer.get('lostFrameCount', 0) > 30:
                    tracked_customer['exitTime'] = datetime.now()
                    customers_in_frame.append({**tracked_customer, 'exited': True})
                    del self.tracked_customers[track_id]
            else:
                self.tracked_customers[track_id]['lostFrameCount'] = 0
        
        self.frame_count += 1
        return customers_in_frame
    
    def assign_customers_to_zones(self, customers, zones):
        """Assign customers to zones based on coordinates"""
        zones_data = {}
        
        for zone in zones:
            zones_data[zone['name']] = {
                'customer_count': 0,
                'customers': []
            }
        
        for customer in customers:
            if 'currentDetection' in customer:
                cx = customer['currentDetection']['x'] + customer['currentDetection']['width'] / 2
                cy = customer['currentDetection']['y'] + customer['currentDetection']['height'] / 2
                
                for zone in zones:
                    if self.is_point_in_zone(cx, cy, zone):
                        if customer['currentZone'] != zone['name']:
                            customer['currentZone'] = zone['name']
                            customer['zoneHistory'].append({
                                'zone': zone['name'],
                                'enterTime': datetime.now()
                            })
                        
                        zones_data[zone['name']]['customer_count'] += 1
                        zones_data[zone['name']]['customers'].append(customer['customerId'])
                        break
        
        return zones_data
    
    def is_point_in_zone(self, x, y, zone):
        """Check if point is within zone coordinates"""
        return (x >= zone['x1'] and x <= zone['x2'] and 
                y >= zone['y1'] and y <= zone['y2'])
    
    def calculate_distance(self, p1, p2):
        """Calculate Euclidean distance between two points"""
        return ((p1['x'] - p2['x']) ** 2 + (p1['y'] - p2['y']) ** 2) ** 0.5
    
    def get_tracked_customers(self):
        """Get all tracked customers"""
        return list(self.tracked_customers.values())
    
    def clear_tracking(self):
        """Clear all tracking data"""
        self.tracked_customers = {}
        self.frame_count = 0
