import sys
import time
import random
import json
from datetime import datetime, timedelta

NODE_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NAME = f"Node {NODE_ID+1}"
CONTACT = f"node{NODE_ID+1}@example.com"

# Generate random location history for the node
history = []
base_time = datetime.now() - timedelta(days=30)
for i in range(100):
    timestamp = base_time + timedelta(hours=i * 7)
    lat = random.uniform(25.0, 49.0)
    lon = random.uniform(-125.0, -67.0)
    history.append({
        'latitude': lat,
        'longitude': lon,
        'timestamp': timestamp.isoformat()
    })

print(f"[{NAME}] Ready. Waiting for area/time query...")

while True:
    try:
        # Simulate receiving a message (read from stdin)
        line = sys.stdin.readline()
        if not line:
            time.sleep(1)
            continue
        query = json.loads(line)
        center_lat = query['center_lat']
        center_lon = query['center_lon']
        radius_km = query['radius_km']
        start_time = query['start_time']
        end_time = query['end_time']
        # Check if node was in area during time range
        in_area = False
        for loc in history:
            ts = loc['timestamp']
            if start_time <= ts <= end_time:
                # Simple distance check (not geodesic for demo)
                dist = ((center_lat - loc['latitude'])**2 + (center_lon - loc['longitude'])**2)**0.5 * 111
                if dist <= radius_km:
                    in_area = True
                    break
        response = {
            'node_id': NODE_ID,
            'name': NAME,
            'contact_info': CONTACT,
            'response': 'Yes' if in_area else 'No'
        }
        print(json.dumps(response))
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
