# Communication-Breakdown# Communication-Breakdown



A secure, decentralized broadcast network simulation demonstrating cryptographic messaging, micro-incentive economics, and resilient mesh communication protocols on the University of Rhode Island Kingston campus. This project implements **MVP B2** of the Communication-Breakdown roadmap, featuring real cryptography, economic incentives, and attack-resistant networking.A web-based simulation of a secure broadcast network that demonstrates encrypted message distribution across virtual nodes on a US map. This repository contains a Python/FastAPI backend and a React/Leaflet frontend. The goal is an educational simulation that shows how encrypted messages are published, propagated across a broadcast-style network, and only readable by intended recipients.



## Project VisionThis README is a single place to understand the project, how to run it, the current state, and the recommended next steps (roadmap) to evolve the project from a simulation to a crypto-aware demo and eventually to Raspberry Pi devices.



Communication-Breakdown is building toward a hybrid communication system for emergency and infrastructure-resilient messaging that combines:## Repository layout

- **Decentralized mesh networking** for resilience during infrastructure failures  

- **Cryptographic security** with public/private key encryption, digital signatures, and zero-knowledge proofs  ```

- **Economic incentives** to encourage network participation and message relay  Communication-Breakdown/

- **Multi-network routing** (WiFi + LoRa) for different message priorities  ├── mock-encryption/                 # Alternate copy of the project (original)

├── mock-encryption-lines/           # Main project used in development

This repository contains the simulation and proof-of-concept for **Track B (The Communications Network)** of the multi-track MVP plan.│   ├── backend/                     # FastAPI backend

│   │   └── main.py

## Repository Layout│   └── frontend/                    # React frontend (Create React App)

│       └── src/

```├── mock-env/                        # Python virtualenv used for backend dev

Communication-Breakdown/└── README.md                        # This file

├── mvp1-mock/                       # MVP B1 prototype (basic simulation)```

│   ├── backend/                     # Initial FastAPI backend

│   ├── frontend/                    # Initial React frontend## What this project does

│   └── mock-env/                    # Python virtualenv

├── mvp2-crypto/                     # **CURRENT: MVP B2 (Active Development)**- Simulates 10 virtual nodes (with fixed locations) on a small map (Rhode Island by default). 

│   ├── backend/                     # Advanced FastAPI backend with crypto- Nodes can publish messages which are broadcasted to other nodes using a simulated radio-style propagation.

│   │   ├── main.py                  # Core simulation with economy & CRDSA- The backend currently simulates packet forwarding based on broadcast range and (new) explicit connections.

│   │   ├── crypto_utils.py          # ECDSA, ECDH, AES-GCM, ZKP- The frontend uses Leaflet to show nodes and allows creating demo connections by dragging between nodes. Those connections can be persisted to the backend and are used by the simulation to forward packets.

│   │   ├── economy.py               # Wallet, reputation, economy tracking

│   │   └── requirements.txtThis is a simulation — the current code does not perform production-ready encryption (yet). The roadmap below shows how to add cryptographic confidentiality and integrity in staged MVP steps.

│   ├── frontend/                    # Enhanced React frontend

│   │   └── src/## Quick start (development)

│   │       ├── App.js               # URI campus map with draggable nodes

│   │       └── index.cssPrerequisites:

│   ├── crypto-env/                  # Python virtualenv with crypto packages- Python 3.10+ and pip

│   ├── uri-map.png                  # URI Kingston campus map background- Node.js and npm

│   └── README.md                    # MVP B2 documentation (see there for details)

└── README.md                        # This fileBackend (FastAPI)

```

1. Create and activate a virtual environment (optional but recommended):

## What This Project Does (MVP B2)

```powershell

**MVP B2: Economic & Resilient Simulation** - A fully-featured campus network simulation with:python -m venv mock-env

mock-env\Scripts\Activate.ps1    # PowerShell on Windows

### Core Features```



1. **Real Cryptography**2. Install backend dependencies and start the server (from backend folder):

   - ECDSA signatures (SECP256R1) for "Help" messages

   - ECDH + AES-GCM encryption for "Logistics" messages```powershell

   - Simulated Zero-Knowledge Proofs for "Safe" messagescd mock-encryption-lines\backend

pip install -r requirements.txt

2. **Micro-Incentive Economy**uvicorn main:app --host 0.0.0.0 --port 8000 --reload

   - Credit system (100 starting credits)```

   - Send costs: 2 credits (Logistics/Help), 0 credits (Safety)

   - Relay rewards: 1 credit (logistics), 10 credits (safety)The backend will expose API docs at `http://localhost:8000/docs`.

   - Universal Basic Income: 5 credits every 10 ticks

   - Real-time Gini/Nakamoto coefficientsFrontend (React)



3. **Network Simulation**From the project root you can either run the frontend directly or via the root helper script.

   - CRDSA collision simulation with SIC algorithm

   - Gossip protocol using Bloom filtersDirect (recommended during development):

   - TTL-based packet expiration (5 minutes)

   - Memory management (max 100 packets/node)```powershell

cd mock-encryption-lines\frontend

4. **Attack Simulation**npm install

   - Packet tampering detectionnpm start

   - Position-based MITM scenarios```

   - Network partition testing

   - DoS recovery validationOr from repository root (a helper script is included):



5. **Interactive Campus Map**```powershell

   - URI Kingston campus as backgroundcd mock-encryption-lines

   - Draggable nodes (update positions via API)npm start

   - Range circles (adjustable 10-200 meters for campus scale)```

   - Economy dashboard with live metrics

   - Message type selection (Logistics/Help/Safe)Open `http://localhost:3000` to view the app. Click any node to open its Inventory panel. Use "Connect Mode" to drag and drop connections between nodes — these connections persist to the backend and are used by the simulation to forward messages.



## Quick Start## Key endpoints (backend)



### Prerequisites- `GET /nodes` — list nodes and locations

- Python 3.11+ with pip- `POST /publish_message` — publish a new message (publisher id, plaintext or ciphertext, target ids)

- Node.js 16+ with npm- `GET /node/{node_id}/inventory` — get packets visible to a node (backend will decrypt/display only if the node is a target, once crypto is implemented)

- Windows PowerShell or bash- `DELETE /messages/clear` — clear all messages

- `GET /connections` — list explicit undirected connections (added to support frontend persist)

### Running the Simulation- `POST /connections` — add an undirected connection { node_a, node_b }

- `DELETE /connections` — remove a connection { node_a, node_b }

**Backend** (Terminal 1):

```powershell## Current state (short)

cd mvp2-crypto

.\crypto-env\Scripts\Activate.ps1- Frontend (`mock-encryption-lines/frontend/src/App.js`) has a Connect Mode that allows dragging connections between nodes and persists those to the backend.

cd backend- Backend simulation (`mock-encryption-lines/backend/main.py`) forwards packets both by broadcast range and across explicit undirected connections saved via the new `/connections` endpoints. Anti-loop prevention (packet history) is implemented.

uvicorn main:app --reload --port 8000- Confirmation dialogs for clearing messages have been removed so the "Clear All Messages" button acts immediately.

```- A root `.gitignore` was added to the repository and staged files were cleaned to avoid committing build artifacts and virtualenv folders.



**Frontend** (Terminal 2):## 📅 The New Multi-Track MVP Calendar

```powershell

cd mvp2-crypto\frontendThis plan is broken into three parallel development tracks

npm install  # first time only

npm start* **Track B: The Comms Network (The "Pipe")**

```    * **Goal:** Build the secure, resilient, decentralized communication protocol and hardware.

* **Track C: The RL Agent (The "Brain")**

**Access**: Open `http://localhost:3000` to view the URI campus map with network nodes.    * **Goal:** Build the AI agent that learns from the "App" to intelligently optimize the "Pipe."



## Development Roadmap---



### Track B: Communication Network### Track B: Comms Network MVP (The "Pipe")

- ✅ **MVP B1**: Core Security (Crypto & ZKP) - *Completed*

- ✅ **MVP B2**: Economic & Resilient Simulation - *Complete (Current)** **MVP B1: Core Security (Crypto & ZKP)**

- ⏳ **MVP B3**: Physical Hardware (Raspberry Pi + LoRa)    * **Goal:** Solve the security and ethical problems in simulation.

  - Port full stack to Raspberry Pi devices    * **Features:** The core simulation (radius spread, Leaflet UI) with:

  - Integrate LoRa radios for long-range mesh        1.  Real Public/Private Key Encryption & Digital Signatures.

  - Deploy on URI campus for real-world testing        2.  The "Safe" (ZKP, anonymous) vs. "Help" (Identifiable) user choice.



### Track C: Reinforcement Learning (Future)* **MVP B2: Economic & Resilient Simulation**

- **MVP C1**: Network-Aware Agent - RL router choosing optimal paths    * **Goal:** Simulate the features that make the network viable and resilient.

- **MVP C2**: Intelligent Mesh Agent - Self-optimizing based on reputation/cost/congestion    * **Features:**

        1.  **Micro-Incentive Economy:** Implement a "credit" system. Nodes *pay* credits to send "logistics" data and *earn* credits for relaying any data. "Safety" packets are free to send but pay the *highest reward* to relay, incentivizing their propagation.

## For More Information        2.  **Hybrid Hardware (LoRa):** Simulate a second, parallel network in the UI. The "LoRa Mesh" (long-range, low-data) is used for "Safety" packets, while the "Wi-Fi Mesh" (short-range, high-data) is used for "logistics" (and costs credits).



See **mvp2-crypto/README.md** for comprehensive documentation including:* **MVP B3: Physical Hardware Validation (Pi + LoRa)**

- Detailed API endpoint reference    * **Goal:** Prove the full protocol on real hardware.

- Testing commands and validation    * **Features:** Port the *full* stack (Crypto, ZKP, Credits, Subnets) to the Raspberry Pi fleet.

- Economic incentive mechanics    * **Hardware:** Each Pi must be equipped with both a **Wi-Fi/Bluetooth** radio and a **LoRa (Long Range)** module to test the hybrid routing.

- Cryptographic implementation details    * **Test:** Run the "Cyber-Physical" (sensor-to-actuator) experiment over the *LoRa* channel, proving its resilience.

- Attack simulation scenarios

---

## Contributing

### Track C: Reinforcement Learning MVP (The "Brain")

This project is actively developed for educational and research purposes focused on emergency communication resilience.

* **MVP C1: Network-Aware Agent (Simulation)**

## License    * **Goal:** Create an agent that can intelligently switch between centralized and decentralized networks.

    * **"State" (Input):** `Central_Network_Status: (Online/Offline)`, `Packet_Priority: (Safety/Logistics)`.

Educational research project. See LICENSE file for details.    * **"Action" (Output):** `Route_Via: (Centralized_API / Decentralized_Mesh)`.

    * **"Reward":** `(Speed of Delivery + Success)`.

## Contact    * **Result:** A basic "smart router" that uses the mesh *only when the internet is down*.



Repository: https://github.com/lpep64/Communication-Breakdown* **MVP C2: Intelligent Mesh Agent (Simulation)**

    * **Goal:** Create an agent that can self-optimize *inside* the mesh.
    * **"State" (Input):** All of C1, *plus* `Neighbor_Reputation_Score`, `Neighbor_Credit_Cost`, `Neighbor_Congestion`.
    * **"Action" (Output):** `Route_Via_Neighbor: (Node_A, Node_B, Node_C...)`.
    * **"Reward":** `(Speed + Success + Credit_Cost_Saving)`.
    * **Result:** A "smart" mesh that learns the most reliable *and* cheapest paths, avoiding malicious/congested nodes.

---

## The Final Product (A + B + C)

This is where all three tracks merge into a single, revolutionary system.

* **The Roster App (A) feeds the Brain (C).**
    * The "Advertiser Analytics" from **(A2)** and "Location/Job Data" from **(A3)** are now fed *directly* into the RL agent **(C)** as its "State."

* **The Brain (C) controls the Pipe (B).**
    * The RL agent, now equipped with *both* network-level data and personnel-level data, makes the final routing decision.

* **The System in Action:**
    * A manager wants to message "B-Shift Welders in Building 4."
    * The **RL Agent (C)** gets the list of 10 people from the **Roster App (A)**.
    * It analyzes the *data from (A)*:
        * `Nodes 1-5`: High response rate on the app.
        * `Node 6`: Never responds to app, 90% SMS response rate.
        * `Nodes 7-10`: Are in a known "dead zone" (data from B's LoRa mesh).
    * It analyzes the *data from (B)*:
        * Centralized Internet: `Online`.
        * Decentralized Wi-Fi Mesh: `Congested` (costs 10 credits).
        * Decentralized LoRa Mesh: `Clear`.
    * **The RL Agent's "Smart" Decision:**
        * `Nodes 1-5`: Send via **Centralized Push Notification** (cheapest, most reliable for them).
        * `Node 6`: Send via **Centralized SMS** (learned preference).
        * `Nodes 7-10`: Send via the **Decentralized LoRa Mesh (B)**, as it's the *only* path that can reach them.
    * **Result:** You have a system that achieves a 100% delivery rate by intelligently blending centralized and decentralized networks, optimizing for cost, speed, and learned user behavior.