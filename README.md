# Rapid-Response

A repository detailing the engineering and business investigation of Rapid-Recall personnel accountability systems developed at the University of Rhode Island's Industrial Systems Engineering program.

**Prepared For:** Rapid C2  
**Date:** December 13, 2025  
**Team Members:** Luke Pepin, Haleigh Wagner, Noah Daylor, Emily Lopez

## Overview

This project addresses critical flaws in existing emergency personnel accountability systems through four progressive prototypes. Each MVP demonstrates different approaches to solving the core problem: maintaining personnel safety and accountability during high-risk situations while preserving employee privacy and trust.

## Problem Statement

> "Ensuring personnel accountability and safety during high-risk situations through the utilization of software outreach and user feedback."

Current emergency communication methods rely on fragmented channels (email, SMS, independent messaging apps) leading to "lost minutes" and increased operational risk. This repository documents our investigation into privacy-preserving, high-speed response mechanisms for crisis management.

## Repository Structure

The repository contains four progressive MVP iterations:

### [MVP1: Location Privacy](./mvp1-location-privacy/)
Personnel accountability system demonstrating location privacy through geographic area queries. Managers can check if employees are in a specific region without revealing exact coordinates.

**Key Features:**
- Geographic area-based queries (center + radius)
- Binary response system (Yes/No presence)
- No exact location sharing
- Simulated employee roster with random locations

### [MVP2: Broadcast Simulation](./mvp2-broadcast-simulation/)
Encrypted message broadcast network simulation showing how messages can be distributed across nodes with targeted decryption.

**Key Features:**
- Simulated 10-node broadcast network
- Targeted message encryption (mock)
- Interactive map-based node visualization
- Message inventory and publishing interface

### [MVP3: Mesh Communication](./mvp3-mesh-communication/)
Advanced disaster communication network with real cryptography, economic incentives, and attack resistance deployed on URI campus.

**Key Features:**
- Real cryptography (ECDSA, ECDH, AES-GCM, ZKP)
- Micro-incentive economy with reputation system
- CRDSA collision simulation
- Attack simulation capabilities
- URI Kingston campus deployment

### [MVP4: Mobile Accountability](./mvp4-mobile-accountability/)
Mobile-responsive personnel accountability application with cryptographic status verification and privacy controls.

**Key Features:**
- Mobile-first responsive design
- Binary status system (Safe/Needs Help)
- Location privacy toggle
- ECDSA cryptographic signatures
- Real-time notification system
- Manager dashboard with map visualization

## Quick Start

Each MVP is self-contained with its own README and setup instructions. Navigate to the specific MVP folder for detailed setup and usage documentation.

**General Requirements:**
- Python 3.10+
- Node.js 16+
- npm or yarn

**Basic Setup Pattern:**
```powershell
# Backend (Python/FastAPI)
cd mvp#-name/backend
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (React)
cd mvp#-name/frontend
npm install
npm start
```

## Key Findings

### Privacy as a Barrier to Entry
Continuous location tracking creates significant workforce resistance. Our privacy-first architectures (deliberate pinging, conditional logic, location obscuring) demonstrated that safety accountability can be maintained while preserving employee trust.

### Operational Inefficiency
Stakeholders confirmed current check-in procedures are "slow and fragmented." The validated solution requires maximum speed, minimum effort binary responses (Safe/Needs Help) to bypass slower forms of communication.

### Feature Critique
Emergency accountability tools must maintain focused value propositions. Feature creep—particularly sensitive features like mental health interventions—dilute core functionality and erode user trust.

## Financial Projections

Annual operating costs for production deployment: **$840 - $12,500+**

**Cost Breakdown:**
- Developer fees: $125 (one-time $25 Android + $100/year iOS)
- Cloud hosting: $240-$2,400/year ($20-$200/month)
- Compliance & Security: $5,000-$15,000/year (largest variable, non-negotiable)

The security implementation represents the primary cost driver but is essential for handling sensitive employee safety data and mitigating privacy concerns.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, coding standards, and submission guidelines.

## License

MIT License - See [LICENSE](./LICENSE) for details.

Copyright © 2025 University of Rhode Island - Industrial Systems Engineering

## Contact

**University of Rhode Island**  
Industrial Systems Engineering  
Kingston, RI 02881

**Repository:** https://github.com/URI-ISE/Rapid-Response

---

*This project represents a comprehensive investigation into trust-preserving emergency communication systems. The progressive MVP structure demonstrates the evolution from basic privacy-preserving queries to sophisticated cryptographic accountability systems suitable for real-world deployment.*
