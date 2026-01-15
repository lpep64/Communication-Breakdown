# Guardian Protocol - Quick Start Guide

Complete setup and demo instructions for the personnel accountability system.

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- Windows PowerShell (or terminal of choice)

## Full Setup (5 Minutes)

### Step 1: Create Python Virtual Environment

```powershell
cd mvp3-mobile
python -m venv guardian-env
.\guardian-env\Scripts\Activate.ps1
```

### Step 2: Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

You should see packages install:
- fastapi
- uvicorn
- cryptography
- pydantic
- python-dotenv

### Step 3: Start Backend Server

```powershell
uvicorn main:app --reload --port 8000
```

Expected output:
```
🛡️  Guardian Protocol Backend
============================================================
Employees: 10
Campus: 41.4880°N, 71.5304°W
API Docs: http://localhost:8000/docs
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ Backend is ready! Leave this terminal running.

### Step 4: Install Frontend Dependencies (New Terminal)

```powershell
cd mvp3-mobile\frontend
npm install
```

This installs React, Leaflet, axios, and dependencies (~2-3 minutes).

### Step 5: Start Frontend Server

```powershell
npm start
```

Browser automatically opens to `http://localhost:3000`.

✅ Frontend is ready!

## Demo Walkthrough (5 Minutes)

### Test 1: Manager Dashboard

1. You should see the **Manager Dashboard** by default
2. Notice 4 stat cards:
   - Total Employees: 10
   - ✅ Safe: 0
   - 🚨 Needs Help: 0
   - ❓ Unknown: 10 (all employees start here)
3. Click **🗺️ Map View** button
4. See 10 gray markers on URI Kingston campus map
5. Click any marker to see popup with employee info
6. Click **📋 Roster View** to return to grid

### Test 2: Employee Status Update

1. In the header, click the **dropdown menu** and select **"Employee 1"**
2. You'll see Alice Johnson's employee portal
3. Click **✅ Mark as Safe** button
4. Status display turns green: "✅ You are marked as SAFE"
5. Notice "Last Update: Just now" and "Signature: 🔒 Signed"

### Test 3: Watch Real-Time Updates

1. Keep Employee 1 portal open
2. Open a **new browser tab** → `http://localhost:3000`
3. You'll see Manager Dashboard
4. Notice stats changed:
   - ✅ Safe: 1 (was 0)
   - ❓ Unknown: 9 (was 10)
5. Find "Alice Johnson" card - it has a **green left border** and "✅ Safe" badge
6. Switch to **Map View** - Alice's marker is now **green**

### Test 4: Emergency Help Request

1. Go back to Employee 1 portal tab
2. Click **🚨 Send Help Request** button
3. Status turns red: "🚨 HELP REQUESTED"
4. Switch to Manager Dashboard tab
5. **Notification appears** in top-right corner:
   - "🚨 Help Requested"
   - "Alice Johnson is requesting help!"
6. Stats updated:
   - 🚨 Needs Help: 1
   - ✅ Safe: 0
7. Alice's card now has **red left border** and pulsing indicator
8. On Map View, her marker is **red and pulsing**

### Test 5: Multiple Employees

1. Select **"Employee 2"** from dropdown (Bob Martinez)
2. Click **✅ Mark as Safe**
3. Select **"Employee 3"** (Carol Zhang)
4. Click **🚨 Send Help Request**
5. Return to **Manager Dashboard**
6. Stats now show:
   - ✅ Safe: 1 (Bob)
   - 🚨 Needs Help: 2 (Alice, Carol)
   - ❓ Unknown: 7
7. Multiple notifications appeared (auto-dismiss after 5 sec)

### Test 6: Mobile Responsive Design

1. Open browser DevTools (F12)
2. Click **Toggle Device Toolbar** (Ctrl+Shift+M)
3. Select "iPhone 12 Pro" or similar mobile device
4. See mobile-optimized layout:
   - Stacked buttons (vertical)
   - Single-column roster cards
   - Touch-friendly tap targets
   - Readable text sizes

## API Testing (Optional)

### View Auto-Generated API Docs

Open `http://localhost:8000/docs` in browser to see:
- Interactive Swagger UI
- All endpoints with request/response schemas
- "Try it out" buttons to test endpoints

### Example curl Commands

```powershell
# Get all employees
curl http://localhost:8000/employees

# Get roster summary
curl http://localhost:8000/roster

# Update employee 5 to Safe
curl -X POST http://localhost:8000/employee/5/status `
  -H "Content-Type: application/json" `
  -d '{"status": "Safe"}'

# Verify signature
curl http://localhost:8000/employee/5/verify

# Get notifications
curl http://localhost:8000/notifications

# Reset all employees
curl -X POST http://localhost:8000/reset
```

## Cryptography Verification

### Test Signature System

1. Open backend terminal, run Python shell:
```powershell
cd backend
python
```

2. Test crypto utilities:
```python
from crypto_utils import CryptoUtils

crypto = CryptoUtils()

# Generate key pair
private_key, public_key = crypto.generate_key_pair()
print("Generated keys successfully")

# Sign a status
sig = crypto.sign_status(private_key, 1, "Safe", "2025-12-02T14:30:00Z")
print(f"Signature: {sig[:50]}...")

# Verify signature
is_valid = crypto.verify_signature(public_key, 1, "Safe", "2025-12-02T14:30:00Z", sig)
print(f"Valid: {is_valid}")  # Should print True

# Try tampering
is_tampered = crypto.verify_signature(public_key, 1, "Needs Help", "2025-12-02T14:30:00Z", sig)
print(f"Tampered valid: {is_tampered}")  # Should print False
```

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- Solution: Activate virtual environment first
```powershell
.\guardian-env\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Error**: `Port 8000 is already in use`
- Solution: Stop other process or use different port
```powershell
uvicorn main:app --reload --port 8001
# Update API_BASE in frontend/src/App.js
```

### Frontend won't start

**Error**: `npm: command not found`
- Solution: Install Node.js from https://nodejs.org/

**Error**: `Failed to compile` or module errors
- Solution: Delete and reinstall
```powershell
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json
npm install
```

### Map not loading

- Check internet connection (OSM tiles require network)
- Try different browser (Chrome recommended)
- Check browser console for tile errors

### Status updates not working

- Verify backend is running (`http://localhost:8000` should show JSON)
- Check browser console for CORS errors
- Try hard refresh (Ctrl+Shift+R)

## Next Steps

### For Academic Presentation

1. Practice the demo flow above (5-7 minutes)
2. Emphasize privacy features:
   - Locations captured but hidden from manager
   - Foundation for ZKP integration
   - Cryptographic signatures prevent spoofing
3. Show code highlights:
   - `backend/crypto_utils.py` - Real ECDSA signatures
   - `frontend/src/App.js` - Mobile-first React components
   - `backend/main.py` - RESTful API design

### For Development

1. Add more employees (edit `initialize_employees()` in `backend/main.py`)
2. Customize campus location (edit `CAMPUS_CENTER`)
3. Modify status options (add "Injured", "Evacuating", etc.)
4. Implement ZKP (see main `README.md` Future Growth section)

### For Deployment

1. Set up PostgreSQL database (replace in-memory storage)
2. Add JWT authentication for manager access
3. Deploy backend to cloud (Heroku, AWS, Azure)
4. Deploy frontend to Vercel/Netlify
5. Configure CORS for production domains

## Questions?

See detailed documentation in:
- `README.md` - Project overview and features
- `backend/README.md` - API details and data models
- `frontend/README.md` - Component architecture and styling
