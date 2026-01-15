# Communication-Breakdown

A web-based simulation of a secure broadcast network that demonstrates encrypted message distribution across virtual nodes on a US map. This project simulates the publishing and receiving of encrypted messages where only designated targets can "decrypt" and read the message content.

## System Architecture

### Backend (Python/FastAPI)
- **Node Management**: Manages 10 virtual nodes, each with fixed, hardcoded locations across the US map
- **API Endpoints**: Provides RESTful endpoints for the core simulation loop
- **Message Broadcasting**: Core endpoint `POST /publish_message` accepts:
  - `publisher_node_id`: ID of the node sending the message
  - `message_text`: The actual message content
  - `list_of_target_node_ids`: Array of node IDs that should be able to decrypt the message
- **Simulated Encryption**: Does *not* perform real encryption but broadcasts messages to all nodes with an `is_target` boolean flag to simulate encrypted communication

### Frontend (React/Leaflet)
- **Interactive Map**: Displays a US map using Leaflet with 10 nodes as clickable markers
- **Node Inventory**: Clicking any node opens its dedicated "Inventory" interface
- **Message Visualization**: Renders messages differently based on the node's relationship to the message (target, publisher, or observer)

## Project Structure

```
mock-encryption/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── README.md           # Backend documentation
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Styling
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── package.json        # Node.js dependencies
│   └── README.md          # Frontend documentation
└── README.md              # This file
```

## MVP Functionality (The Simulation Loop)

The core user experience follows this workflow:

1. **Node Selection**: User clicks on any node (e.g., "Node 3") on the interactive map to open its **Inventory**

2. **Inventory Interface**: The Inventory displays two main sections:
   - **Publish New Message Area**: Interface for creating and sending new messages
   - **Message History List**: Chronological list of all messages this node has received

3. **Message Creation**: To publish a new message:
   - User types their message in the text input field
   - A **checklist of all other 9 nodes** appears
   - User selects target recipients by checking boxes (e.g., "Node 5" and "Node 8")

4. **Message Publishing**: User clicks "Publish" button
   - Frontend sends the message and target list `[5, 8]` to the backend via API
   - Backend processes the request and broadcasts to all nodes

5. **Message Broadcasting**: Backend sends message object to *all* nodes (simulating broadcast nature of the network)

6. **Simulated Encryption Rendering**: Frontend displays messages in each node's "Message History" based on access level:
   - **Target Nodes (e.g., Nodes 5 & 8)**: Display plaintext message (e.g., "Meet at dawn")
   - **Non-Target Nodes (all others)**: Show red, unreadable hash (e.g., `[HASH] 2d7f9a1b...8c3e9a` or `############`)
   - **Publisher Node (Node 3)**: Shows the sent message in their outbound message format

## Getting Started

### Backend Setup (Python/FastAPI)

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access API Documentation**:
   - Navigate to `http://localhost:8000/docs` for interactive API documentation

### Frontend Setup (React)

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Install Required Packages**:
   ```bash
   npm install react-leaflet leaflet axios
   ```

3. **Start Development Server**:
   ```bash
   npm start
   ```

4. **Access Application**:
   - Navigate to `http://localhost:3000` to view the interactive map

## API Endpoints (Simulated)

### Core Endpoints

#### `GET /nodes`
Returns the complete list of 10 virtual nodes with their geographic locations.

**Response**:
```json
{
  "nodes": [
    {
      "id": 1,
      "name": "Node 1",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "location_name": "New York, NY"
    },
    // ... 9 more nodes
  ]
}
```

#### `POST /publish_message`
The core endpoint for message broadcasting simulation.

**Request Body**:
```json
{
  "publisher_node_id": 3,
  "message_text": "Meet at dawn",
  "target_node_ids": [5, 8]
}
```

**Response**:
```json
{
  "message_id": "msg_12345",
  "status": "broadcast_complete",
  "timestamp": "2024-01-01T12:00:00Z",
  "recipients": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
```

#### `GET /node/{node_id}/messages`
Retrieves message history for a specific node, including encryption status.

**Response**:
```json
{
  "node_id": 5,
  "messages": [
    {
      "message_id": "msg_12345",
      "publisher_node_id": 3,
      "timestamp": "2024-01-01T12:00:00Z",
      "is_target": true,
      "content": "Meet at dawn"
    },
    {
      "message_id": "msg_12346",
      "publisher_node_id": 7,
      "timestamp": "2024-01-01T11:30:00Z",
      "is_target": false,
      "content": "[HASH] 2d7f9a1b8c3e9a"
    }
  ]
}
```

#### `GET /node/{node_id}/inventory`
Opens the inventory interface for a specific node.

**Response**:
```json
{
  "node_id": 3,
  "node_name": "Node 3",
  "location": {
    "latitude": 41.8781,
    "longitude": -87.6298,
    "location_name": "Chicago, IL"
  },
  "message_count": 15,
  "last_activity": "2024-01-01T12:00:00Z"
}
```

## Technical Implementation Notes

- **No Real Encryption**: This is a simulation focused on demonstrating secure communication concepts
- **Client-Side Rendering**: Encryption/decryption visualization happens entirely in the frontend
- **Broadcast Network**: All nodes receive all messages, simulating radio broadcast behavior
- **State Management**: Consider using React Context or Redux for managing node states and message history
- **Real-time Updates**: Future enhancement could include WebSocket connections for live message updates

## Future Enhancements

- Real-time message broadcasting using WebSockets
- Node-to-node direct messaging simulation
- Network topology visualization
- Message encryption strength simulation
- Multi-hop routing simulation
- Network disruption scenarios