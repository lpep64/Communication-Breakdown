# MVP4: Mobile Accountability

Mobile-responsive personnel accountability application with cryptographic status verification and privacy controls.

## Overview

This MVP demonstrates a trust-preserving emergency status tracking system where employees can report their safety status while maintaining privacy control over location data. Features cryptographic signatures for authenticity and a mobile-first responsive design for field use.

## Key Features

- **Personnel Management:** Track 10 employees with status updates
- **Request/Response System:** Manager initiates status checks with 5-minute timer
- **Privacy Toggle:** Employees control location sharing visibility
- **Status Options:** Binary "Safe" / "Needs Help" / "Unknown" tracking
- **Cryptographic Signatures:** ECDSA (SECP256R1) proves status authenticity
- **Mobile-Responsive:** Touch-friendly interface optimized for phones/tablets
- **Real-Time Notifications:** Visual alerts for "Needs Help" status changes
- **Dual Views:** Manager dashboard with roster table + map visualization

## Getting Started

### Backend Setup
```powershell
cd backend
python -m venv ..\guardian-env
..\guardian-env\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend available at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### Frontend Setup
```powershell
cd frontend
npm install
npm start
```

Frontend opens at: http://localhost:3000

## Usage

### Manager Dashboard
1. Open http://localhost:3000
2. View employee roster with current status
3. Select individual or all employees via checkboxes
4. Click "Send Request" to initiate status check (5-min timer)
5. Monitor responses in real-time on roster and map

### Employee Portal
1. Navigate to http://localhost:3000/employee/{id} (IDs 1-10)
2. View pending status requests
3. Toggle location privacy (hide/show on manager map)
4. Click "Safe" or "Needs Help" to respond
5. See confirmation with cryptographic signature

## Technical Architecture

**Backend (Python/FastAPI):**
- Employee management with unique IDs and crypto keys
- ECDSA signature generation/verification
- Status tracking with timestamps
- Notification queue for critical events
- RESTful API for all operations

**Frontend (React + Leaflet):**
- Mobile-first responsive design
- OpenStreetMap integration with color-coded markers
- Card-based employee roster
- Toast-style notification system
- Separate employee and manager interfaces

## Status System

- **Safe (Green):** Employee confirms safety
- **Needs Help (Red):** Employee requires assistance
- **Unknown (Gray):** No recent status update
- **Requested (Blue):** Manager has initiated check

## Privacy Features

- Location privacy toggle per employee
- Hidden locations appear as gray markers on map
- Only status (not location) required for safety confirmation
- Foundation for future Zero-Knowledge Proof integration

## Documentation

- [Project Summary](./PROJECT_SUMMARY.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [Update Summary](./UPDATE_SUMMARY.md)

## Notes

- All employee data is simulated for demonstration
- Cryptographic signatures validate status authenticity
- Designed for rapid deployment in emergency scenarios
- Mobile-responsive for field accessibility
