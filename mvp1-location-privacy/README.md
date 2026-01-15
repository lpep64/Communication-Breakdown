# MVP1: Location Privacy

Personnel accountability system demonstrating location privacy through geographic area queries.

## Overview

This MVP demonstrates how organizations can check employee safety during emergencies without compromising individual privacy. Managers can query if employees are within a specific geographic area, receiving only "Yes" or "No" responses—exact locations are never revealed.

## System Architecture

**Backend (Python/FastAPI):**
- Simulates 10 employee nodes with randomly generated names
- Each node has a current location (randomly generated)
- API endpoints for geographic area queries
- Returns binary responses (Yes/No) only—never exact coordinates
- CORS enabled for frontend communication

**Frontend (React/Leaflet):**
- Interactive map of the US for area selection
- Area definition via center point + radius (km)
- Employee roster with contact information
- Real-time query responses
- "Last updated" timestamps

## Getting Started

### Backend Setup
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### Frontend Setup
```powershell
cd frontend
npm install
npm start
```
Frontend runs at: http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Select an area on the map and set the radius (km)
3. Click "Send Query" to check employee presence
4. View Yes/No responses in the roster
5. Use "Clear Responses" to reset

## Key Features

- **Privacy-First:** No exact locations ever transmitted
- **Geographic Queries:** Area-based accountability
- **Real-Time Updates:** Instant response feedback
- **Simulated Data:** No real employee information used

## Technical Notes

- All employee data is simulated for demonstration purposes
- Location data is randomly generated at startup
- No historical tracking or persistent storage
- Designed for educational and proof-of-concept purposes