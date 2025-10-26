from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Set, Tuple
import uuid
from datetime import datetime
import json
import random
import asyncio
import math
from contextlib import asynccontextmanager

# Global simulation state
simulation_running = False

# Data models
class Node(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    location_name: str
    range: int  # Broadcast range in km

class MessagePacket(BaseModel):
    packet_id: str
    original_message_id: str
    publisher_id: int
    target_ids: List[int]
    message_text: str
    history: List[int]  # List of node IDs this packet has visited

class PublishMessageRequest(BaseModel):
    publisher_node_id: int
    message_text: str
    target_node_ids: List[int]

class Message(BaseModel):
    message_id: str
    publisher_node_id: int
    message_text: str
    target_node_ids: List[int]
    timestamp: str
    is_target: Optional[bool] = None

class NodeMessage(BaseModel):
    message_id: str
    publisher_node_id: int
    timestamp: str
    is_target: bool
    content: str


class ConnectionRequest(BaseModel):
    node_a: int
    node_b: int

def generate_random_conus_location():
    """Generate random coordinates within the continental United States"""
    # Continental US approximate boundaries
    # North: 49°N (Canadian border)
    # South: 25°N (Southern tip of Florida/Texas)
    # East: -67°W (Maine coast)
    # West: -125°W (Pacific coast)
    
    latitude = random.uniform(25.0, 49.0)
    longitude = random.uniform(-125.0, -67.0)
    
    return latitude, longitude

def generate_location_name(lat, lng):
    """Generate a descriptive location name based on coordinates"""
    # Simple region mapping based on coordinates
    if lng > -95:  # Eastern US
        if lat > 39:
            region = "Northeast"
        else:
            region = "Southeast"
    else:  # Western US
        if lat > 39:
            region = "Northwest" 
        else:
            region = "Southwest"
    
    return f"{region} ({lat:.2f}°N, {abs(lng):.2f}°W)"

# Generate nodes with fixed locations across Rhode Island
def create_fixed_nodes():
    """Create 10 nodes with fixed locations across Rhode Island"""
    # Fixed locations across Rhode Island cities and towns
    fixed_locations = [
        (41.8240, -71.4128, "Providence, RI"),         # Node 1 - Capital
        (41.4901, -71.3128, "Newport, RI"),            # Node 2 - Coastal
        (41.7000, -71.4300, "Cranston, RI"),           # Node 3 - Southwest Providence
        (41.5834, -71.4648, "Warwick, RI"),            # Node 4 - South of Providence
        (41.9739, -71.5995, "Woonsocket, RI"),         # Node 5 - Northern border
        (41.3707, -71.4245, "Westerly, RI"),           # Node 6 - Southwest coast
        (41.5456, -71.6616, "West Greenwich, RI"),     # Node 7 - Western RI
        (41.6555, -71.1533, "Bristol, RI"),            # Node 8 - Eastern coast
        (41.7370, -71.1534, "Barrington, RI"),         # Node 9 - East Bay
        (41.4582, -71.5659, "Richmond, RI")            # Node 10 - South central
    ]
    
    nodes = []
    for i, (lat, lng, location_name) in enumerate(fixed_locations, 1):
        # Much smaller range - 5km default for Rhode Island scale
        range_km = 5  # Start with 5km range
        
        node = Node(
            id=i,
            name=f"Node {i}",
            latitude=lat,
            longitude=lng,
            location_name=location_name,
            range=range_km
        )
        nodes.append(node)
    
    return nodes

# Calculate distance between two points using Haversine formula
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth in kilometers"""
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    earth_radius = 6371
    
    return earth_radius * c

# Generate fixed node locations
NODES = create_fixed_nodes()

# In-memory packet storage - each node has its own inventory of packets
node_inventories: Dict[int, List[MessagePacket]] = {i: [] for i in range(1, 11)}

# Explicit connections (undirected) between nodes for demo/persistent links
# Stored as a set of tuples (a,b) where a < b
CONNECTIONS: Set[Tuple[int, int]] = set()

# Old message storage for backward compatibility (if needed)
messages_store = []
node_messages = {i: [] for i in range(1, 11)}

async def simulation_tick():
    """Core simulation logic - runs every 3 seconds"""
    global node_inventories, NODES
    
    # Create a copy of current inventories to avoid modifying while iterating
    new_packets = []
    
    # For each node, share packets to neighbors found either by range OR explicit connections
    for node_a in NODES:
        for node_b in NODES:
            if node_a.id == node_b.id:
                continue

            # Calculate distance between nodes
            distance = calculate_distance(
                node_a.latitude, node_a.longitude,
                node_b.latitude, node_b.longitude
            )

            # Determine if node_b should receive packets from node_a
            connected_via_range = distance <= node_a.range
            a, b = min(node_a.id, node_b.id), max(node_a.id, node_b.id)
            connected_via_link = (a, b) in CONNECTIONS

            if connected_via_range or connected_via_link:
                # Node A shares its inventory with Node B
                for packet in node_inventories[node_a.id]:
                    # Check anti-loop rule: reject if node_b is already in history
                    if node_b.id not in packet.history:
                        # Create new packet copy for node_b
                        new_packet = MessagePacket(
                            packet_id=str(uuid.uuid4()),
                            original_message_id=packet.original_message_id,
                            publisher_id=packet.publisher_id,
                            target_ids=packet.target_ids,
                            message_text=packet.message_text,
                            history=packet.history + [node_b.id]
                        )
                        new_packets.append((node_b.id, new_packet))
    
    # Add all new packets to their respective inventories
    for node_id, packet in new_packets:
        # Check if we already have this packet (same original_message_id and same history)
        existing = any(
            p.original_message_id == packet.original_message_id and 
            p.history == packet.history 
            for p in node_inventories[node_id]
        )
        if not existing:
            node_inventories[node_id].append(packet)

async def start_simulation():
    """Start the background simulation loop"""
    global simulation_running
    simulation_running = True
    
    while simulation_running:
        await simulation_tick()
        await asyncio.sleep(3)  # Tick every 3 seconds

async def stop_simulation():
    """Stop the background simulation loop"""
    global simulation_running
    simulation_running = False

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting simulation...")
    task = asyncio.create_task(start_simulation())
    try:
        yield
    finally:
        # Shutdown
        print("Stopping simulation...")
        await stop_simulation()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

app = FastAPI(title="Communication-Breakdown Mock Encryption API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_hash(message_text: str) -> str:
    """Generate a mock hash for encrypted messages"""
    return f"[HASH] {uuid.uuid4().hex[:16]}..."

@app.get("/")
async def root():
    return {"message": "Communication-Breakdown Mock Encryption API"}

@app.get("/nodes")
async def get_nodes():
    """Get all nodes with their locations and ranges"""
    return [
        {
            "node_id": node.id,
            "name": node.name,
            "lat": node.latitude,
            "lng": node.longitude,
            "range": node.range
        }
        for node in NODES
    ]

@app.post("/regenerate_nodes")
async def regenerate_nodes():
    """Regenerate all nodes with new fixed locations"""
    global NODES, node_inventories
    NODES = create_fixed_nodes()
    # Clear all inventories when regenerating nodes
    node_inventories = {i: [] for i in range(1, 11)}
    return {"message": "Nodes regenerated with fixed locations", "nodes": NODES}

@app.post("/publish_message")
async def publish_message(request: PublishMessageRequest):
    """Publish a message to the network - creates initial packet in publisher's inventory"""
    
    # Validate publisher node exists
    if request.publisher_node_id not in range(1, 11):
        raise HTTPException(status_code=404, detail="Publisher node not found")
    
    # Validate target nodes exist
    for target_id in request.target_node_ids:
        if target_id not in range(1, 11):
            raise HTTPException(status_code=404, detail=f"Target node {target_id} not found")
    
    # Create the initial message packet
    original_message_id = str(uuid.uuid4())
    packet_id = str(uuid.uuid4())
    
    packet = MessagePacket(
        packet_id=packet_id,
        original_message_id=original_message_id,
        publisher_id=request.publisher_node_id,
        target_ids=request.target_node_ids,
        message_text=request.message_text,
        history=[request.publisher_node_id]  # Start with publisher in history
    )
    
    # Place packet in publisher's inventory
    node_inventories[request.publisher_node_id].append(packet)
    
    return {
        "message_id": original_message_id,
        "packet_id": packet_id,
        "status": "published",
        "timestamp": datetime.now().isoformat(),
        "publisher_node_id": request.publisher_node_id
    }


@app.get("/connections")
async def get_connections():
    """Return all explicit undirected connections"""
    return [{"a": a, "b": b} for (a, b) in sorted(CONNECTIONS)]


@app.post("/connections")
async def add_connection(req: ConnectionRequest):
    """Add an undirected connection between two nodes"""
    if req.node_a not in range(1, 11) or req.node_b not in range(1, 11):
        raise HTTPException(status_code=404, detail="One or both nodes not found")
    if req.node_a == req.node_b:
        raise HTTPException(status_code=400, detail="Cannot connect node to itself")
    a, b = min(req.node_a, req.node_b), max(req.node_a, req.node_b)
    CONNECTIONS.add((a, b))
    return {"status": "connected", "a": a, "b": b}


@app.delete("/connections")
async def remove_connection(req: ConnectionRequest):
    """Remove an undirected connection between two nodes"""
    a, b = min(req.node_a, req.node_b), max(req.node_a, req.node_b)
    if (a, b) in CONNECTIONS:
        CONNECTIONS.remove((a, b))
        return {"status": "removed", "a": a, "b": b}
    raise HTTPException(status_code=404, detail="Connection not found")

@app.get("/node/{node_id}/messages")
async def get_node_messages(node_id: int):
    """Get message history for a specific node"""
    if node_id not in range(1, 11):
        raise HTTPException(status_code=404, detail="Node not found")
    
    return {
        "node_id": node_id,
        "messages": node_messages[node_id]
    }

@app.get("/node/{node_id}/inventory")
async def get_node_inventory(node_id: int):
    """Get packet inventory for a specific node"""
    if node_id not in range(1, 11):
        raise HTTPException(status_code=404, detail="Node not found")
    
    packets = node_inventories[node_id]
    
    # Format packets for frontend display
    formatted_packets = []
    for packet in packets:
        # Determine if this node can decrypt the message
        can_decrypt = node_id in packet.target_ids
        
        formatted_packet = {
            "packet_id": packet.packet_id,
            "original_message_id": packet.original_message_id,
            "publisher_id": packet.publisher_id,
            "target_ids": packet.target_ids,
            "history": packet.history,
            "path_string": "->".join([str(nid) for nid in packet.history]),
            "can_decrypt": can_decrypt,
            "content": packet.message_text if can_decrypt else generate_hash(packet.message_text)
        }
        formatted_packets.append(formatted_packet)
    
    node = NODES[node_id - 1]
    return {
        "node_id": node_id,
        "node_name": node.name,
        "location": {
            "latitude": node.latitude,
            "longitude": node.longitude,
            "location_name": node.location_name
        },
        "range": node.range,
        "packets": formatted_packets,
        "packet_count": len(formatted_packets)
    }

@app.delete("/messages/clear")
async def clear_all_messages():
    """Clear all messages from the system"""
    global messages_store, node_messages, node_inventories
    messages_store.clear()
    node_messages = {i: [] for i in range(1, 11)}
    node_inventories = {i: [] for i in range(1, 11)}
    return {"status": "All messages and packets cleared"}

@app.get("/simulation/status")
async def get_simulation_status():
    """Get the current simulation status"""
    total_packets = sum(len(inventory) for inventory in node_inventories.values())
    return {
        "running": simulation_running,
        "total_packets": total_packets,
        "node_packet_counts": {node_id: len(inventory) for node_id, inventory in node_inventories.items()}
    }

@app.put("/node/{node_id}/range")
async def update_node_range(node_id: int, new_range: int):
    """Update the broadcast range for a specific node"""
    if node_id not in range(1, 11):
        raise HTTPException(status_code=404, detail="Node not found")
    
    if new_range < 1 or new_range > 50:
        raise HTTPException(status_code=400, detail="Range must be between 1 and 50 km")
    
    # Find and update the node
    for i, node in enumerate(NODES):
        if node.id == node_id:
            NODES[i].range = new_range
            break
    
    return {
        "node_id": node_id,
        "new_range": new_range,
        "status": "range_updated"
    }

@app.get("/node/{node_id}/network")
async def get_node_network(node_id: int):
    """Get network connectivity information for a specific node"""
    if node_id not in range(1, 11):
        raise HTTPException(status_code=404, detail="Node not found")
    
    current_node = None
    for node in NODES:
        if node.id == node_id:
            current_node = node
            break
    
    if not current_node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Nodes that current node can reach (within its broadcast range)
    nodes_in_range = []
    # Nodes that can reach the current node (current node is within their range)
    nodes_that_can_reach = []
    
    for node in NODES:
        if node.id == node_id:
            continue
            
        distance = calculate_distance(
            current_node.latitude, current_node.longitude,
            node.latitude, node.longitude
        )
        
        # Check if this node is within current node's range
        if distance <= current_node.range:
            nodes_in_range.append({
                "node_id": node.id,
                "name": node.name,
                "distance_km": round(distance, 1),
                "can_receive": True,
                "coordinates": {"lat": node.latitude, "lng": node.longitude}
            })
        
        # Check if current node is within this node's range
        if distance <= node.range:
            nodes_that_can_reach.append({
                "node_id": node.id,
                "name": node.name,
                "distance_km": round(distance, 1),
                "range_km": node.range,
                "can_send_to_me": True,
                "coordinates": {"lat": node.latitude, "lng": node.longitude}
            })

    # Explicit connections
    nodes_connected = []
    for (a, b) in CONNECTIONS:
        if a == node_id:
            other = next((n for n in NODES if n.id == b), None)
            if other:
                nodes_connected.append({
                    "node_id": other.id,
                    "name": other.name,
                    "coordinates": {"lat": other.latitude, "lng": other.longitude},
                    "connected_via": "link"
                })
        elif b == node_id:
            other = next((n for n in NODES if n.id == a), None)
            if other:
                nodes_connected.append({
                    "node_id": other.id,
                    "name": other.name,
                    "coordinates": {"lat": other.latitude, "lng": other.longitude},
                    "connected_via": "link"
                })
    
    return {
        "node_id": node_id,
        "node_name": current_node.name,
        "node_coordinates": {"lat": current_node.latitude, "lng": current_node.longitude},
        "broadcast_range": current_node.range,
        "nodes_in_my_range": nodes_in_range,
        "nodes_that_can_reach_me": nodes_that_can_reach,
        "nodes_connected": nodes_connected,
        "total_reachable": len(nodes_in_range),
        "total_can_reach_me": len(nodes_that_can_reach)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)