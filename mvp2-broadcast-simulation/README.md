# MVP2: Broadcast Simulation

Encrypted message broadcast network simulation demonstrating targeted message distribution.

## Overview

This MVP simulates a broadcast network where messages are distributed to all nodes, but only designated recipients can "decrypt" and read the content. It demonstrates the concept of public broadcast with selective access control.

## System Architecture

**Backend (Python/FastAPI):**
- Manages 10 virtual nodes with fixed US map locations
- RESTful endpoints for message publishing and retrieval
- Simulated encryption via `is_target` flag (not production cryptography)
- Broadcast-style message distribution to all nodes

**Frontend (React/Leaflet):**
- Interactive US map with clickable node markers
- Node inventory interface for each node
- Message visualization based on access level
- Message composition and target selection

## Getting Started

### Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs at: http://localhost:8000

### Frontend Setup
```powershell
cd frontend
npm install
npm start
```
Frontend runs at: http://localhost:3000

## Usage

1. **Select a Node:** Click any node marker on the map
2. **View Inventory:** See the node's message history
3. **Compose Message:** Enter message text
4. **Select Targets:** Check boxes for recipient nodes
5. **Publish:** Send message to network
6. **Observe Results:**
   - Target nodes: See plaintext message
   - Non-target nodes: See encrypted hash
   - Publisher node: See sent message

## Key Features

- **Broadcast Network:** Messages sent to all nodes
- **Targeted Access:** Only recipients can read content
- **Visual Differentiation:** Clear indication of message access levels
- **Interactive Map:** Geographic visualization of network topology

## Technical Notes

- Encryption is simulated, not production-grade
- All nodes receive all messages (broadcast model)
- Access control via boolean flag system
- Designed for educational demonstration

3. **Run the Server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access API Documentation**:
   - Navigate to `http://localhost:8000/docs` for interactive API documentation

### Frontend Setup (React)

1. **Install Dependencies**:
   ```bash
