# Guardian Protocol - Backend

FastAPI server providing personnel accountability with cryptographic signatures.

## Features

- **Employee Roster Management**: Track 10 employees with unique IDs
- **Status Updates**: "Safe" / "Needs Help" / "Unknown"
- **ECDSA Signatures**: Cryptographic proof of status authenticity
- **Notification System**: Real-time alerts for status changes
- **RESTful API**: Clean endpoints with auto-generated docs

## Setup

### 1. Create Virtual Environment

```powershell
cd mvp3-mobile
python -m venv guardian-env
.\guardian-env\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 3. Start Server

```powershell
uvicorn main:app --reload --port 8000
```

Server runs at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

## API Endpoints

### Employee Management

- `GET /employees` - List all employees with status
- `GET /employee/{id}` - Get employee details
- `POST /employee/{id}/status` - Update employee status (auto-signed)
- `GET /employee/{id}/verify` - Verify signature on last update

### Manager Dashboard

- `GET /roster` - Get roster summary (status counts)
- `GET /notifications` - Get status change notifications
- `POST /notifications/mark_read/{id}` - Mark notification as read
- `DELETE /notifications/clear` - Clear all notifications

### Utilities

- `GET /` - Health check
- `POST /reset` - Reset all employees to "Unknown"
- `POST /regenerate` - Regenerate employees with new keys/locations

## Data Models

### Employee
```json
{
  "id": 1,
  "name": "Alice Johnson",
  "status": "Safe",
  "last_update": "2025-12-02T14:30:00Z",
  "location": {"lat": 41.4880, "lon": -71.5304},
  "public_key": "-----BEGIN PUBLIC KEY-----...",
  "signature": "a3f5b2c1..."
}
```

### Notification
```json
{
  "id": 1,
  "employee_id": 1,
  "employee_name": "Alice Johnson",
  "message": "Alice Johnson is requesting help!",
  "timestamp": "2025-12-02T14:30:00Z",
  "status": "Needs Help",
  "read": false
}
```

## Cryptography

Uses **ECDSA (SECP256R1)** for status signing:

1. Each employee has a unique key pair (generated on startup)
2. Status updates are signed: `sign({employee_id, status, timestamp})`
3. Signatures can be verified using employee's public key
4. Prevents status spoofing (can't pretend to be another employee)

See `crypto_utils.py` for implementation details.

## Configuration

### Campus Location
Edit `CAMPUS_CENTER` in `main.py`:
```python
CAMPUS_CENTER = {"lat": 41.4880, "lon": -71.5304}  # URI Kingston
```

### Employee Names
Edit `names` list in `initialize_employees()` function.

## Development

### Hot Reload
The `--reload` flag auto-restarts server on code changes.

### Testing
Test endpoints using FastAPI's interactive docs at `/docs` or:

```powershell
# Get all employees
curl http://localhost:8000/employees

# Update employee 1 status
curl -X POST http://localhost:8000/employee/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "Safe"}'

# Verify signature
curl http://localhost:8000/employee/1/verify
```

## Future Enhancements

- WebSocket support for real-time updates
- Database persistence (PostgreSQL, MongoDB)
- JWT authentication for manager access
- ZKP integration (prove geofence membership)
- Offline status queueing
