# Communication-Breakdown Frontend

React frontend for the mock encryption simulation with interactive map and node inventory management.

## Features

- Interactive US map with 10 node locations
- Clickable node markers with popups
- Node inventory panels with message publishing
- Target node selection with checkboxes
- Message history with encryption simulation
- Real-time message broadcasting visualization

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open browser to http://localhost:3000

## Usage

1. Click any node marker on the map to open its inventory
2. Use the "Publish New Message" section to send encrypted messages
3. Select target nodes using checkboxes
4. View message history with encryption status:
   - Green: Messages you can decrypt (target or sender)
   - Red: Encrypted messages (hash format)
   - Blue: Messages you sent

## Dependencies

- React 18.2.0
- React-Leaflet 4.2.1
- Leaflet 1.9.4
- Axios 1.6.0