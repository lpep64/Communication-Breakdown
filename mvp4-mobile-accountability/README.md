# MVP 3: Rapid Response - Personnel Accountability System

A **mobile-responsive personnel accountability application** that demonstrates trust-preserving emergency status tracking. This system shows how organizations can fulfill their duty of care during disasters while respecting employee privacy through cryptographic signatures, location privacy controls, and a foundation for future Zero-Knowledge Proof integration.

## 🎯 What Makes This Special

- ✅ **Personnel Roster Management**: Track employee status without invasive monitoring
- ✅ **Request Response System**: Select employees and request status updates with 5-minute timer
- ✅ **Location Privacy Toggle**: Employees can hide their location from managers
- ✅ **Mobile-Responsive Design**: Clean, touch-friendly interface for field use
- ✅ **Real-Time Status Updates**: "Safe" / "Needs Help" / "Unknown" tracking
- ✅ **Check-in Timestamps**: See when employees last reported their status
- ✅ **Cryptographic Signatures**: ECDSA signing proves status authenticity
- ✅ **Manager Dashboard**: Centralized view with roster table + map visualization
- ✅ **Checkbox Selection**: Select individual or all employees on roster/map
- ✅ **OpenStreetMap Integration**: Geographic awareness for crisis zones (respects hidden locations)
- ✅ **Notification System**: Visual alerts for status changes
- ✅ **Privacy-First Design**: Foundation for future ZKP integration

## 🏗️ System Architecture

### Backend (Python/FastAPI)
- **Employee Management**: 10 employees with unique IDs, names, and cryptographic keys
- **Status Tracking**: Real-time status updates with timestamps
- **Cryptographic Signing**: ECDSA (SECP256R1) signatures on all status packets
- **Notification Queue**: Alert system for "Needs Help" status changes
- **RESTful API**: Clean endpoints for roster, status updates, notifications

### Frontend (React + Leaflet)
- **Mobile-First Design**: Responsive layout optimized for phones/tablets
- **Roster View**: Card-based employee list with status indicators
- **Map View**: OpenStreetMap with color-coded employee markers
- **Employee Portal**: Self-service status update interface
- **Manager Dashboard**: Aggregated view of all personnel
- **Notification Center**: Toast-style alerts for critical events

## 📁 Project Structure

```
mvp3-mobile/
├── backend/
│   ├── main.py                  # FastAPI server with employee + crypto logic
│   ├── crypto_utils.py          # ECDSA signature generation/verification
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Backend documentation
├── frontend/
│   ├── src/
│   │   ├── App.js              # Main React component (mobile-responsive)
│   │   ├── index.js            # React entry point
│   │   └── index.css           # Mobile-first styling
│   ├── public/
│   │   └── index.html          # HTML template
│   ├── package.json            # Node.js dependencies
│   └── README.md               # Frontend documentation
├── guardian-env/               # Python virtual environment
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Setup Python Environment

```powershell
# Create virtual environment
cd mvp3-mobile
python -m venv guardian-env

# Activate environment
.\guardian-env\Scripts\Activate.ps1

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Start Backend Server

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

### 3. Start Frontend Development Server

```powershell
# In a new terminal
cd frontend
npm install  # First time only
npm start
```

Frontend will open at `http://localhost:3000`

### 4. Demo Workflow

**Employee Self-Check:**
1. Open `http://localhost:3000/employee/1` (any ID 1-10)
2. Click "Mark as Safe" or "Send Help Request"
3. Status is cryptographically signed and sent to backend

**Manager Dashboard:**
1. Open `http://localhost:3000/manager`
2. View roster with real-time status indicators:
   - 🟢 Green = Safe
   - 🔴 Red = Needs Help
   - ⚪ Gray = Unknown/No Update
3. Click employee cards to see details
4. View map with color-coded markers

**Notification System:**
- Toast notifications appear when employees request help
- Notification center shows all recent alerts
- Auto-dismiss after 5 seconds

## 🔧 API Endpoints

### Employee Management
- `GET /employees` - Get all employees with status
- `GET /employee/{id}` - Get single employee details
- `POST /employee/{id}/status` - Update employee status (signed)
- `GET /employee/{id}/verify` - Verify signature on last status update

### Manager Dashboard
- `GET /roster` - Get roster summary (counts by status)
- `GET /notifications` - Get recent status change alerts
- `POST /notifications/mark_read/{id}` - Mark notification as read
- `DELETE /notifications/clear` - Clear all notifications

### Utilities
- `GET /health` - Health check endpoint
- `POST /reset` - Reset all employees to "Unknown" status

## 📊 Employee Data Model

```json
{
  "id": 1,
  "name": "Alice Johnson",
  "status": "Safe",
  "last_update": "2025-12-02T14:30:00Z",
  "location": {
    "lat": 41.4880,
    "lon": -71.5304
  },
  "public_key": "-----BEGIN PUBLIC KEY-----...",
  "signature": "a3f5b2c1..."
}
```

**Status Values:**
- `"Unknown"` - No status reported (default)
- `"Safe"` - Employee confirmed safe
- `"Needs Help"` - Emergency assistance requested

**Privacy Note**: Locations are stored but NOT displayed to managers in this MVP. Future ZKP integration will prove geofence membership without revealing exact coordinates.

## 🔐 Cryptographic Features

### ECDSA Signatures (Current Implementation)
- **Key Generation**: SECP256R1 curve (256-bit security)
- **Signing**: Every status update includes signature over `{employee_id, status, timestamp}`
- **Verification**: Backend verifies signature matches employee's public key
- **Authenticity**: Prevents status spoofing (can't pretend to be another employee)

### Zero-Knowledge Proofs (Future Growth)
The current system lays the groundwork for ZKP integration:
1. **Location Privacy**: Employee locations are captured but hidden from UI
2. **Geofence Circuit**: Future ZKP will prove "inside crisis zone" without revealing coordinates
3. **Trust Layer**: Managers see proof validity, not raw GPS data

See "Future Growth" section below for full ZKP roadmap.

## 🎨 UI/UX Features

### Mobile-Responsive Design
- **Breakpoints**: Optimized for 320px (phone) to 1920px (desktop)
- **Touch-Friendly**: Large buttons (min 44x44px), swipe gestures
- **Readable Text**: 16px base font, high contrast ratios
- **Fast Loading**: Lazy-loaded map tiles, optimized assets

### Status Indicators
- **Color-Coded**: Instant visual recognition (green/red/gray)
- **Icon Support**: Emoji indicators for accessibility
- **Timestamps**: Relative time display ("2 minutes ago")
- **Auto-Refresh**: Polls backend every 5 seconds

### Notification System
- **Toast Alerts**: Non-blocking, auto-dismissing
- **Priority Queue**: "Needs Help" alerts always on top
- **Sound Support**: Optional audio alerts (future)
- **History View**: Review past 50 notifications

## 🌍 Geographic Features

### OpenStreetMap Integration
- **Base Layer**: OSM tiles (no API key required)
- **Employee Markers**: Custom color-coded pins
- **Crisis Zones**: Polygon overlays for geofence boundaries (future)
- **Clustering**: Group nearby employees at low zoom levels

### Campus Deployment
Default setup uses **URI Kingston Campus** coordinates:
- Center: `41.4880°N, 71.5304°W`
- Coverage: ~2km radius
- 10 employees randomly placed within campus bounds

Easily adaptable to any location by editing `CAMPUS_CENTER` in `backend/main.py`.

## 📈 Future Growth Plan

### Phase 1: Core Enhancements (Next 2-4 weeks)
- [ ] Multi-status options ("Injured", "Trapped", "Evacuating")
- [ ] Message field (brief text updates)
- [ ] Battery level reporting
- [ ] Offline status queueing (send when reconnected)

### Phase 2: Zero-Knowledge Proof Integration (2-3 months)
- [ ] Implement point-in-circle ZKP (simplified geofence)
- [ ] Generate ZKP on employee device (prove "inside 500m radius")
- [ ] Verify ZKP on manager dashboard (display ✓/✗, not coordinates)
- [ ] Benchmark proof generation time on mobile hardware
- [ ] Extend to polygon geofences (full crisis zone shapes)

### Phase 3: Decentralization (3-6 months)
- [ ] P2P transport layer (BLE / WiFi-Direct mesh)
- [ ] Store-and-forward relaying (status packets hop through employees)
- [ ] Byzantine fault tolerance (reputation system from MVP B2)
- [ ] Offline-first architecture (IndexedDB storage)

### Phase 4: Enterprise Integration (6-12 months)
- [ ] SSO authentication (SAML, OAuth)
- [ ] Role-based access control (managers, admins, auditors)
- [ ] API connectors for RapidC2, Everbridge, etc.
- [ ] Compliance reporting (OSHA, SOX, GDPR)
- [ ] Multi-tenant support (separate organizations)

### Phase 5: Advanced Features (12+ months)
- [ ] Machine learning (anomaly detection, route prediction)
- [ ] Wearable device support (smartwatch check-ins)
- [ ] Voice commands (hands-free status updates)
- [ ] International crisis integration (FEMA, Red Cross APIs)

## 🎓 Educational Value

### Concepts Demonstrated
1. **Privacy-Preserving Design**: Minimize data collection, maximize trust
2. **Cryptographic Authenticity**: Public-key infrastructure for identity
3. **Mobile-First Development**: Responsive design, offline considerations
4. **RESTful Architecture**: Clean API design, separation of concerns
5. **Real-Time Systems**: WebSocket-ready (currently polling for simplicity)

### Perfect For
- ✅ Human-Computer Interaction (HCI) courses
- ✅ Mobile app development classes
- ✅ Cryptography and security curricula
- ✅ Disaster response planning workshops
- ✅ Senior capstone projects
- ✅ Startup pitch competitions (SaaS product potential)

## 🔬 Research Applications

This MVP serves as a foundation for academic research in:
- **Trust-Preserving Surveillance**: Balancing safety and privacy
- **Zero-Knowledge Protocols**: Practical ZKP deployment on mobile
- **Crisis Communication**: Human factors in emergency technology
- **Decentralized Systems**: Mesh networks for disaster scenarios
- **Applied Cryptography**: Real-world PKI implementation

## 🤝 Relationship to Other MVPs

### MVP 1 (Mock System)
- **Shared**: Basic FastAPI + React architecture
- **Evolved**: Added cryptography, mobile responsiveness

### MVP 2 (Crypto Disaster Network)
- **Reused**: ECDSA signature utils, OpenStreetMap integration
- **Simplified**: Removed gossip protocol, economic system, reputation
- **Adapted**: Nodes → Employees, Messages → Status Updates

### MVP 3 (This System)
- **Focus**: Personnel accountability, not disaster communication
- **Architecture**: Centralized (simpler), not decentralized mesh
- **Use Case**: Corporate/organizational duty of care

## 📄 License

See project license file for details.

## 🙏 Acknowledgments

- University of Rhode Island Kingston Campus (demo location)
- MVP B2 codebase (cryptographic foundation)
- Python `cryptography` library (ECDSA implementation)
- React-Leaflet (map visualization)
- OpenStreetMap (free tile service)

---

**Ready to demo?** Start backend + frontend, open `/manager` dashboard, and click employee status buttons! 📱
