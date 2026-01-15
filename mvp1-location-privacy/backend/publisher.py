import subprocess
import json
import time
from datetime import datetime, timedelta

NUM_NODES = 5
node_procs = []

# Start node subscriber processes
for i in range(NUM_NODES):
    proc = subprocess.Popen([
        "python", "backend/node_subscriber.py", str(i)
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    node_procs.append(proc)

# Example area/time query
center_lat = 39.0
center_lon = -95.0
radius_km = 500.0
start_time = (datetime.now() - timedelta(days=1)).isoformat()
end_time = datetime.now().isoformat()
query = {
    "center_lat": center_lat,
    "center_lon": center_lon,
    "radius_km": radius_km,
    "start_time": start_time,
    "end_time": end_time,
    "message": "Report if you were in the area!"
}

print("Publishing query to all nodes...")
for proc in node_procs:
    proc.stdin.write(json.dumps(query) + "\n")
    proc.stdin.flush()

responses = []
for proc in node_procs:
    # Wait for response from each node
    line = proc.stdout.readline()
    try:
        resp = json.loads(line)
        responses.append(resp)
    except Exception as e:
        print(f"Error reading response: {e}")

print("\nNode responses:")
for resp in responses:
    print(f"{resp['name']}: {resp['response']}")

# Optional: terminate node processes after query
for proc in node_procs:
    proc.terminate()
