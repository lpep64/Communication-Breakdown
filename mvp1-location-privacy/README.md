# Personnel Accountability MVP

## System Architecture

**Backend (Python/FastAPI):**
- Simulates 10 employee nodes, each with a randomly generated silly name (including Impractical Jokers name game names).
- Each node has a single current location (randomly generated).
- Provides API endpoints to query which nodes are inside a user-defined geographic area.
- Returns only "Yes" or "No" for each node—never shares exact location.
- No historical location or time-based logic; only current location is checked.
- CORS enabled for frontend communication.

**Frontend (React/Leaflet):**
- Interactive map of the US for area selection (center + radius in km).
- Roster of 9 employees shown in a compact list with silly names and contact info.
- User can select area and radius, then send a query to backend.
- Responses update in real time, with a "Last updated" timestamp.
- "Clear Responses" button resets the roster status.

## Getting Started

### 1. Backend Setup
Open a terminal and run:
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Backend runs at: http://localhost:8000

### 2. Frontend Setup
Open a new terminal and run:
```powershell
cd frontend
npm install
npm start
```
Frontend runs at: http://localhost:3000

### 3. Usage
- Open http://localhost:3000 in your browser.
- Draw/select an area on the map and set the radius (km).
- Click "Send Query" to see which employees are inside the area.
- View responses in the roster list below the map.
- Use "Clear Responses" to reset the roster status.

## Notes
- All data is simulated; no real employee/location data is used.
- No employee location is ever revealed—only "Yes" or "No" for area presence.
- Names are randomly generated and intentionally silly for demo purposes.

## Notes

- All data is simulated; no real employee/location data is used.## Note

- No employee location is ever revealed—only "Yes" or "No" for area presence.All data is simulated. No real employee/location data is used.

- Names are randomly generated and intentionally silly for demo purposes.

---

## TODO / Potential Future Work
1. **Roster Management Tools:**
	- Creation of proper roster management features, including multiple views, full employee directory, and access to standard information/resources.
2. **Employee Frontend & Security:**
	- Develop a secure frontend for employees, including authentication and pop-up dialogs for answering manager queries.
3. **Event & Polling System:**
	- Allow employers to create events in regions, enabling employees to vote in polls or answer yes/no to location-wide questions.
4. **Historical Data Search:**
	- Enable searching for employees who were present in a geographic area at a previous point in time.
5. **Employee Location Sharing:**
	- Allow employees to share previous and current location data to confirm their whereabouts, with privacy controls.
6. **Enhanced Security Measures:**
	- Implement additional security features for both frontend and backend, including authentication, authorization, and data protection.
7. **Full Stack Deployment:**
	- Prepare the system for production-ready, full stack deployment with robust infrastructure and monitoring.