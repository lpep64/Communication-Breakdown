
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from nodes import NODES, Node

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AreaQuery(BaseModel):
    center_lat: float
    center_lon: float
    radius_km: float
    message: str

RESPONSES = {}

@app.get("/nodes")
def get_nodes():
    return [{
        "node_id": n.node_id,
        "name": n.name,
        "contact_info": n.contact_info
    } for n in NODES]

@app.post("/publish")
async def publish_query(query: AreaQuery):
    from geopy.distance import geodesic
    global RESPONSES
    RESPONSES = {}
    for node in NODES:
        # Only check the most recent location
        loc = node.location_history[-1]
        dist = geodesic((float(query.center_lat), float(query.center_lon)), (float(loc['latitude']), float(loc['longitude']))).km
        in_area = dist <= float(query.radius_km) + 1
        RESPONSES[node.node_id] = {
            "name": node.name,
            "contact_info": node.contact_info,
            "response": "Yes" if in_area else "No"
        }
    return {"status": "published"}

@app.get("/responses")
async def get_responses():
    return list(RESPONSES.values())
