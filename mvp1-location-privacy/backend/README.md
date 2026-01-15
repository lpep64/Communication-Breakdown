# Backend (FastAPI)

This backend simulates employee nodes and provides API endpoints for message publishing and response collection.

## Features
- Simulated node environment with historical location data
- Publisher/subscriber model for message queries
- API endpoints for frontend integration

## Setup
1. Create a Python virtual environment
2. Install dependencies (see requirements.txt)
3. Run the FastAPI server

## Endpoints
- `/nodes` - List all simulated nodes
- `/publish` - Send area/time query to nodes
- `/responses` - Get node responses

---

All data is simulated for MVP/demo purposes.