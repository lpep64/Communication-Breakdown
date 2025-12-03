"""
Rapid Response - Personnel Accountability Backend
FastAPI server for employee status tracking with cryptographic signatures
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import random
from crypto_utils import CryptoUtils

app = FastAPI(title="Rapid Response API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class Location(BaseModel):
    lat: float
    lon: float

class Employee(BaseModel):
    id: int
    name: str
    status: str = "Unknown"  # "Safe", "Needs Help", "Unknown", "In Danger"
    last_update: Optional[str] = None
    location: Location
    public_key: str
    signature: Optional[str] = None
    location_hidden: bool = False
    last_checkin: Optional[str] = None
    request_pending: bool = False
    request_sent_time: Optional[str] = None
    response_time: Optional[str] = None
    response_type: str = "none"  # "none", "requested", "yellow", "green", "red", "grey"

class StatusUpdate(BaseModel):
    status: str
    timestamp: Optional[str] = None

class Notification(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    message: str
    timestamp: str
    status: str  # "Needs Help", "Safe"
    read: bool = False

# ============================================================================
# GLOBAL STATE
# ============================================================================

# URI Kingston Campus center point
CAMPUS_CENTER = {"lat": 41.4880, "lon": -71.5304}
CAMPUS_RADIUS_KM = 1.0

# Employee database (in-memory for MVP)
employees_db: Dict[int, dict] = {}
private_keys_db: Dict[int, any] = {}  # Store private keys for signing
notifications_db: List[Notification] = []
notification_counter = 0

# Request tracking
request_history: List[dict] = []  # Store all request cycles with responses

crypto = CryptoUtils()

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_employees():
    """Initialize 10 employees with random campus locations and crypto keys"""
    global employees_db, private_keys_db
    
    names = [
        "Alice Johnson", "Bob Martinez", "Carol Zhang", "David O'Brien",
        "Emma Davis", "Frank Wilson", "Grace Kim", "Henry Taylor",
        "Iris Patel", "Jack Anderson"
    ]
    
    for i, name in enumerate(names, start=1):
        # Generate random location on campus
        lat_offset = random.uniform(-0.01, 0.01)  # ~1km radius
        lon_offset = random.uniform(-0.01, 0.01)
        
        location = Location(
            lat=CAMPUS_CENTER["lat"] + lat_offset,
            lon=CAMPUS_CENTER["lon"] + lon_offset
        )
        
        # Generate cryptographic key pair
        private_key, public_key_pem = crypto.generate_key_pair()
        
        # Store employee
        employees_db[i] = {
            "id": i,
            "name": name,
            "status": "Unknown",
            "last_update": None,
            "location": location.dict(),
            "public_key": public_key_pem,
            "signature": None,
            "location_hidden": False,
            "last_checkin": None,
            "request_pending": False,
            "request_sent_time": None,
            "response_time": None,
            "response_type": "grey"
        }
        
        # Store private key (in production, this would be on employee's device)
        private_keys_db[i] = private_key
    
    print(f"✓ Initialized {len(employees_db)} employees with crypto keys")

# Initialize on startup
initialize_employees()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_notification(employee_id: int, status: str):
    """Create a notification when employee status changes to 'Needs Help'"""
    global notification_counter, notifications_db
    
    employee = employees_db.get(employee_id)
    if not employee:
        return
    
    notification_counter += 1
    
    if status == "Needs Help":
        message = f"{employee['name']} is requesting help!"
    else:
        message = f"{employee['name']} updated status to {status}"
    
    notification = Notification(
        id=notification_counter,
        employee_id=employee_id,
        employee_name=employee['name'],
        message=message,
        timestamp=datetime.utcnow().isoformat() + "Z",
        status=status,
        read=False
    )
    
    notifications_db.append(notification)
    
    # Keep only last 50 notifications
    if len(notifications_db) > 50:
        notifications_db.pop(0)

# ============================================================================
# API ENDPOINTS - EMPLOYEE MANAGEMENT
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "Rapid Response API",
        "version": "1.0.0",
        "status": "operational",
        "employees": len(employees_db),
        "notifications": len(notifications_db)
    }

@app.get("/employees", response_model=List[Employee])
def get_employees():
    """Get all employees with current status"""
    return [Employee(**emp) for emp in employees_db.values()]

@app.get("/employee/{employee_id}", response_model=Employee)
def get_employee(employee_id: int):
    """Get single employee details"""
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return Employee(**employees_db[employee_id])

@app.post("/employee/{employee_id}/status")
def update_status(employee_id: int, status_update: StatusUpdate):
    """
    Update employee status with cryptographic signature
    
    Simulates the employee's device signing the status update
    """
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get current timestamp if not provided
    timestamp = status_update.timestamp or (datetime.utcnow().isoformat() + "Z")
    
    # Validate status
    valid_statuses = ["Safe", "Needs Help", "Unknown", "In Danger"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    # Sign the status update (simulating employee device)
    private_key = private_keys_db[employee_id]
    signature = crypto.sign_status(
        private_key,
        employee_id,
        status_update.status,
        timestamp
    )
    
    # Determine response type based on status
    response_type_map = {
        "Safe": "green",
        "Needs Help": "red",
        "In Danger": "red",
        "Unknown": "grey"
    }
    
    # Update employee record
    was_requested = employees_db[employee_id]["request_pending"]
    employees_db[employee_id]["status"] = status_update.status
    employees_db[employee_id]["last_update"] = timestamp
    employees_db[employee_id]["signature"] = signature
    employees_db[employee_id]["last_checkin"] = timestamp  # Record check-in time
    employees_db[employee_id]["response_type"] = response_type_map.get(status_update.status, "grey")
    
    # If this was a response to a request, record it
    if was_requested:
        employees_db[employee_id]["response_time"] = timestamp
        employees_db[employee_id]["request_pending"] = False
    
    # Create notification if needed
    create_notification(employee_id, status_update.status)
    
    return {
        "success": True,
        "employee_id": employee_id,
        "status": status_update.status,
        "timestamp": timestamp,
        "signature": signature[:50] + "...",  # Truncate for readability
        "signature_valid": True  # We just created it, so it's valid
    }

@app.get("/employee/{employee_id}/verify")
def verify_employee_signature(employee_id: int):
    """Verify the cryptographic signature on employee's last status update"""
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee = employees_db[employee_id]
    
    if not employee["signature"]:
        return {
            "employee_id": employee_id,
            "has_signature": False,
            "message": "No status update has been signed yet"
        }
    
    # Verify signature
    is_valid = crypto.verify_signature(
        employee["public_key"],
        employee_id,
        employee["status"],
        employee["last_update"],
        employee["signature"]
    )
    
    return {
        "employee_id": employee_id,
        "name": employee["name"],
        "status": employee["status"],
        "timestamp": employee["last_update"],
        "signature_valid": is_valid,
        "message": "Signature verified successfully" if is_valid else "Signature verification failed"
    }

# ============================================================================
# API ENDPOINTS - MANAGER DASHBOARD
# ============================================================================

@app.get("/roster")
def get_roster_summary():
    """Get roster summary with status counts"""
    status_counts = {"Safe": 0, "Needs Help": 0, "Unknown": 0, "In Danger": 0}
    
    for emp in employees_db.values():
        status_counts[emp["status"]] += 1
    
    return {
        "total_employees": len(employees_db),
        "status_counts": status_counts,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/notifications", response_model=List[Notification])
def get_notifications(unread_only: bool = False):
    """Get notifications (optionally filter to unread only)"""
    if unread_only:
        return [n for n in notifications_db if not n.read]
    
    # Return most recent first
    return sorted(notifications_db, key=lambda x: x.timestamp, reverse=True)

@app.post("/notifications/mark_read/{notification_id}")
def mark_notification_read(notification_id: int):
    """Mark a notification as read"""
    for notification in notifications_db:
        if notification.id == notification_id:
            notification.read = True
            return {"success": True, "notification_id": notification_id}
    
    raise HTTPException(status_code=404, detail="Notification not found")

@app.delete("/notifications/clear")
def clear_notifications():
    """Clear all notifications"""
    global notifications_db
    count = len(notifications_db)
    notifications_db = []
    return {"success": True, "cleared": count}

@app.put("/employee/{employee_id}/location_privacy")
def toggle_location_privacy(employee_id: int, hidden: bool):
    """Toggle location privacy for an employee"""
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employees_db[employee_id]["location_hidden"] = hidden
    
    return {
        "success": True,
        "employee_id": employee_id,
        "location_hidden": hidden,
        "message": f"Location privacy {'enabled' if hidden else 'disabled'}"
    }

@app.post("/request_response")
def request_response(employee_ids: List[int]):
    """Send a request for response to selected employees"""
    if not employee_ids:
        raise HTTPException(status_code=400, detail="No employees selected")
    
    # Create notifications for selected employees
    timestamp = datetime.utcnow().isoformat() + "Z"
    notifications_created = []
    
    # Create new request record
    request_record = {
        "id": len(request_history) + 1,
        "timestamp": timestamp,
        "employee_ids": employee_ids,
        "responses": {}
    }
    
    for emp_id in employee_ids:
        if emp_id in employees_db:
            # Mark employee as having pending request (resets previous request)
            employees_db[emp_id]["request_pending"] = True
            employees_db[emp_id]["request_sent_time"] = timestamp
            employees_db[emp_id]["response_time"] = None
            employees_db[emp_id]["response_type"] = "yellow"
            
            # Initialize response tracking
            request_record["responses"][emp_id] = {
                "employee_name": employees_db[emp_id]["name"],
                "status": "Pending",
                "response_time": None,
                "response_type": "yellow"
            }
            
            global notification_counter
            notification_counter += 1
            
            notification = Notification(
                id=notification_counter,
                employee_id=emp_id,
                employee_name=employees_db[emp_id]['name'],
                message=f"Manager requesting status update from {employees_db[emp_id]['name']}",
                timestamp=timestamp,
                status="Request",
                read=False
            )
            notifications_db.append(notification)
            notifications_created.append(emp_id)
    
    # Store request in history
    request_history.insert(0, request_record)  # Most recent first
    
    return {
        "success": True,
        "requested_count": len(notifications_created),
        "employee_ids": notifications_created,
        "timestamp": timestamp,
        "request_id": request_record["id"]
    }

@app.get("/request_history")
def get_request_history():
    """Get history of all request/response cycles"""
    # Update responses with current employee data
    for request in request_history:
        for emp_id in request["employee_ids"]:
            if emp_id in employees_db and emp_id in request["responses"]:
                emp = employees_db[emp_id]
                request["responses"][emp_id]["status"] = emp["status"]
                request["responses"][emp_id]["response_time"] = emp.get("response_time")
                request["responses"][emp_id]["response_type"] = emp.get("response_type", "grey")
    
    return request_history

@app.post("/employee/{employee_id}/timeout")
def mark_employee_timeout(employee_id: int):
    """Mark employee as 'Needs Help' due to timeout"""
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Update employee to Needs Help status
    employees_db[employee_id]["status"] = "Needs Help"
    employees_db[employee_id]["last_update"] = timestamp
    employees_db[employee_id]["response_type"] = "red"
    employees_db[employee_id]["request_pending"] = False
    
    # Create orange "Unresponsive" notification
    global notification_counter
    notification_counter += 1
    
    notification = Notification(
        id=notification_counter,
        employee_id=employee_id,
        employee_name=employees_db[employee_id]['name'],
        message=f"{employees_db[employee_id]['name']} did not respond - marked as Needs Help",
        timestamp=timestamp,
        status="Unresponsive",
        read=False
    )
    notifications_db.append(notification)
    
    return {
        "success": True,
        "employee_id": employee_id,
        "status": "Needs Help",
        "reason": "timeout"
    }

# ============================================================================
# API ENDPOINTS - UTILITIES
# ============================================================================

@app.post("/reset")
def reset_employees():
    """Reset all employees to 'Unknown' status"""
    for emp_id in employees_db:
        employees_db[emp_id]["status"] = "Unknown"
        employees_db[emp_id]["last_update"] = None
        employees_db[emp_id]["signature"] = None
    
    global notifications_db
    notifications_db = []
    
    return {
        "success": True,
        "message": "All employees reset to Unknown status",
        "employees_reset": len(employees_db)
    }

@app.post("/regenerate")
def regenerate_employees():
    """Regenerate employees with new random locations and keys"""
    initialize_employees()
    
    global notifications_db, notification_counter
    notifications_db = []
    notification_counter = 0
    
    return {
        "success": True,
        "message": "Employees regenerated with new locations and crypto keys",
        "total_employees": len(employees_db)
    }

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("⚡ Rapid Response Backend")
    print("=" * 60)
    print(f"Employees: {len(employees_db)}")
    print(f"Campus: {CAMPUS_CENTER['lat']:.4f}°N, {abs(CAMPUS_CENTER['lon']):.4f}°W")
    print(f"API Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
