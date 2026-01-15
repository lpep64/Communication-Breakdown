# MVP3: Mesh Communication

Advanced disaster communication network with real cryptography, economic incentives, and attack resistance deployed on URI Kingston campus.

## Overview

This MVP demonstrates a fully-featured disaster communication system with production-grade cryptography, economic incentive mechanisms, reputation-based security, and attack simulation capabilities. Deployed virtually on the URI Kingston campus with realistic 100m transmission ranges.

## Key Features

- **Real Cryptography:**
  - ECDSA signatures (SECP256R1) for Help messages
  - ECDH + AES-GCM encryption for Logistics messages
  - Simulated Zero-Knowledge Proofs for Safe messages

- **Economic System:**
  - Credit-based micro-payments (100 credits initial, 1 credit UBI per tick)
  - Message costs: 2 credits (Logistics/Help), 0 credits (Safe)
  - Relay rewards: 1 credit per successful relay
  - Gini & Nakamoto coefficient tracking

- **Reputation System:**
  - Self-reputation tracking (starts at 100%)
  - Penalties: Hash tampering (-30%), refusing relay (-2%/tick), message tampering (-40%)
  - Enforcement: Nodes below 30% reputation are isolated

- **Network Protocols:**
  - CRDSA collision simulation with SIC algorithm
  - Bloom filter gossip for anti-entropy
  - TTL management for message expiry

- **Attack Simulation:**
  - Selfish node attacks
  - Hash manipulation
  - Message tampering
  - Network partitioning

## Getting Started

### Backend Setup
```powershell
cd backend
python -m venv ..\crypto-env
..\crypto-env\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```powershell
cd frontend
npm install
npm start
```

## Usage

### Web UI (React + Leaflet)
1. Open http://localhost:3000
2. View 10 nodes on URI campus map (OpenStreetMap)
3. Click nodes to select, Shift+click to create connections
4. Use node settings to edit hash values, toggle auto-relay
5. View economy dashboard for Gini/Nakamoto coefficients

### Terminal Demo (Presentation Mode)
```powershell
cd backend
python presentation_demo.py
```

Follow the interactive terminal prompts for a guided demo showcasing:
- Cryptographic message types
- Economic incentive mechanics
- Reputation system enforcement
- Attack simulation scenarios

## Message Types

| Type | Encryption | Cost | Network | Use Case |
|------|-----------|------|---------|----------|
| **Logistics** | ECDH+AES-GCM | 2 credits | WiFi | Targeted emergency coordination |
| **Help** | ECDSA signature | 2 credits | WiFi | Public emergency broadcasts |
| **Safe** | ZKP (simulated) | FREE | LoRa | Anonymous status for vulnerable populations |

## Technical Architecture

- **Backend:** Python/FastAPI with cryptography, ecdsa packages
- **Frontend:** React with Leaflet for OpenStreetMap visualization
- **Crypto:** Real ECDSA/ECDH/AES-GCM implementations
- **Economy:** Credit tracking with wealth inequality metrics
- **Reputation:** Active enforcement with network isolation

## Documentation

- [Presentation Demo Guide](./backend/PRESENTATION_DEMO_README.md)
- [Gap Analysis](./MVP_B2_GAP_ANALYSIS.md)
- [Presentation Notes](./PRESENTATION_NOTES.md)
- [Virtual Environment Setup](./VENV_README.md)

## Notes

- Nodes randomly placed on URI campus each startup
- 100m transmission range matches realistic WiFi coverage
- Economy and reputation systems demonstrate game-theoretic incentives
- Designed for educational and research purposes
