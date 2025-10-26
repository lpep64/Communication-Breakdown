# Communication-Breakdown

A web-based simulation of a secure broadcast network that demonstrates encrypted message distribution across virtual nodes on a US map. This repository contains a Python/FastAPI backend and a React/Leaflet frontend. The goal is an educational simulation that shows how encrypted messages are published, propagated across a broadcast-style network, and only readable by intended recipients.

This README is a single place to understand the project, how to run it, the current state, and the recommended next steps (roadmap) to evolve the project from a simulation to a crypto-aware demo and eventually to Raspberry Pi devices.

## Repository layout

```
Communication-Breakdown/
├── mock-encryption/                 # Alternate copy of the project (original)
├── mock-encryption-lines/           # Main project used in development
│   ├── backend/                     # FastAPI backend
│   │   └── main.py
│   └── frontend/                    # React frontend (Create React App)
│       └── src/
├── mock-env/                        # Python virtualenv used for backend dev
└── README.md                        # This file
```

## What this project does

- Simulates 10 virtual nodes (with fixed locations) on a small map (Rhode Island by default). 
- Nodes can publish messages which are broadcasted to other nodes using a simulated radio-style propagation.
- The backend currently simulates packet forwarding based on broadcast range and (new) explicit connections.
- The frontend uses Leaflet to show nodes and allows creating demo connections by dragging between nodes. Those connections can be persisted to the backend and are used by the simulation to forward packets.

This is a simulation — the current code does not perform production-ready encryption (yet). The roadmap below shows how to add cryptographic confidentiality and integrity in staged MVP steps.

## Quick start (development)

Prerequisites:
- Python 3.10+ and pip
- Node.js and npm

Backend (FastAPI)

1. Create and activate a virtual environment (optional but recommended):

```powershell
python -m venv mock-env
mock-env\Scripts\Activate.ps1    # PowerShell on Windows
```

2. Install backend dependencies and start the server (from backend folder):

```powershell
cd mock-encryption-lines\backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will expose API docs at `http://localhost:8000/docs`.

Frontend (React)

From the project root you can either run the frontend directly or via the root helper script.

Direct (recommended during development):

```powershell
cd mock-encryption-lines\frontend
npm install
npm start
```

Or from repository root (a helper script is included):

```powershell
cd mock-encryption-lines
npm start
```

Open `http://localhost:3000` to view the app. Click any node to open its Inventory panel. Use "Connect Mode" to drag and drop connections between nodes — these connections persist to the backend and are used by the simulation to forward messages.

## Key endpoints (backend)

- `GET /nodes` — list nodes and locations
- `POST /publish_message` — publish a new message (publisher id, plaintext or ciphertext, target ids)
- `GET /node/{node_id}/inventory` — get packets visible to a node (backend will decrypt/display only if the node is a target, once crypto is implemented)
- `DELETE /messages/clear` — clear all messages
- `GET /connections` — list explicit undirected connections (added to support frontend persist)
- `POST /connections` — add an undirected connection { node_a, node_b }
- `DELETE /connections` — remove a connection { node_a, node_b }

## Current state (short)

- Frontend (`mock-encryption-lines/frontend/src/App.js`) has a Connect Mode that allows dragging connections between nodes and persists those to the backend.
- Backend simulation (`mock-encryption-lines/backend/main.py`) forwards packets both by broadcast range and across explicit undirected connections saved via the new `/connections` endpoints. Anti-loop prevention (packet history) is implemented.
- Confirmation dialogs for clearing messages have been removed so the "Clear All Messages" button acts immediately.
- A root `.gitignore` was added to the repository and staged files were cleaned to avoid committing build artifacts and virtualenv folders.

## Recommended Roadmap (Next steps)

This is the order I recommend to add cryptography and further features. Each step focuses on one problem so we can test, verify, and demonstrate the behavior incrementally.

### Next MVP (Crypto)

Goal: Simulate end-to-end encrypted messaging (confidentiality).

1. Backend: Give each node a real (public_key, private_key) pair.
   - For the simulation, keys can be generated at startup and stored in memory or in a simple JSON file. Use a standard asymmetric algorithm (e.g., RSA 2048 or ECC).

2. Backend: Implement `GET /public_keys` (a simple key server returning public keys indexed by node id).

3. Frontend: When Node 3 publishes a message intended for Node 8, the publisher fetches Node 8's public key and encrypts the message.

4. Logic: The `message_text` field inside packets becomes ciphertext. Only Node 8 (using its private key) can decrypt and view the plaintext. Other nodes see ciphertext or a mock hash.

Notes: For performance and message size, use hybrid encryption: generate a random symmetric key (AES-GCM), encrypt the message with AES-GCM, then encrypt the symmetric key per-target with their public key.

### MVP +1 (Integrity)

Goal: Simulate message integrity (preventing message tampering attacks).

1. Backend: When a publisher publishes, sign the message (or its hash) with the publisher's private key.

2. Logic: As the packet spreads, each forwarding/receiving node verifies the signature using the publisher's public key. Store verification result with the packet so the frontend can show verified/tampered status.

Result: Nodes can be confident that the message originated from the publisher and hasn't been modified en route.

### MVP +2 (Features)

Add features that improve UX and demo fidelity:
- Node movement API (PUT /node/{id}/location) to change lat/lng at runtime.
- Persist connections and node keys to disk for durability.
- Add a Node History UI in the frontend showing packet paths, verification status, and decrypted content where allowed.
- Non-blocking toasts and UI polish (disable blocking alert/confirm — already updated).

### Final Step (Physical Deployment)

Port the final Python backend (and optionally the frontend) to Raspberry Pi devices to demonstrate the system running on physical hardware. Provide provisioning scripts, key-loading workflows, and network/firewall notes.

## Acceptance criteria (short)

- A published message encrypted for Node B decrypts correctly only on Node B.
- Signed messages verify at all hops; any tampering is flagged.
- Packets propagate across explicit links and range-based broadcasts as expected.
- Frontend shows clear indicators for encrypted vs decrypted packets and signature verification state.

## How I can help next

- I can implement the Crypto MVP backend changes (key generation and `GET /public_keys`) and modify the frontend publish flow (examples with Web Crypto API).
- Or I can implement both backend + frontend changes and run quick local tests here.

If you'd like me to start, tell me whether you prefer
- Backend-first (I add keyserver endpoints and generate keys), or
- Full-stack (I implement both backend + frontend encryption and a demo flow).

Either option is straightforward; backend-first is a small, low-risk step and lets us test key distribution before changing the frontend publish code.

---

If you want this README committed to the repository root, tell me and I will create/commit the file. If you'd like edits or a different format (short, developer-focused, or a printable handout), say which and I'll produce it.
