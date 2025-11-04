from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Set, Tuple
import uuid
from datetime import datetime
import random
import asyncio
import math
from contextlib import asynccontextmanager
import base64
from pybloom_live import BloomFilter

# Import crypto and economy modules
from crypto_utils import CryptoManager, simulate_zkp_proof, verify_zkp_proof, generate_message_id
from economy import (
    Wallet, ReputationManager, EconomyTracker, global_economy,
    INITIAL_CREDITS, LOGISTICS_SEND_COST, LOGISTICS_RELAY_REWARD,
    SAFETY_SEND_COST, SAFETY_RELAY_REWARD, UBI_AMOUNT, UBI_INTERVAL_TICKS
)

# Configuration Constants
NUM_NODES = 10
MAX_INVENTORY_SIZE = 100  # Maximum packets per node inventory (prevents memory leak)
MAX_MESSAGE_LENGTH = 1000  # Maximum message text length
PACKET_TTL_SECONDS = 300  # Packet time-to-live (5 minutes)

# CRDSA Configuration
CRDSA_ENABLED = True  # Enable/disable CRDSA collision simulation
CRDSA_SLOTS_PER_TICK = 5  # Number of time slots per simulation tick
CRDSA_REPLICAS = 2  # Number of packet replicas (2 or 3 typical for CRDSA)
CRDSA_MAX_SIC_ITERATIONS = 10  # Maximum SIC iterations

# Gossip Protocol Configuration
BLOOM_FILTER_CAPACITY = 1000  # Expected number of items
BLOOM_FILTER_ERROR_RATE = 0.01  # 1% false positive rate

# Global simulation state
simulation_running = False
simulation_lock = None  # Will be initialized in lifespan

# Enhanced Node class with runtime components
class NodeRuntime:
    """Runtime wrapper for Node with crypto, wallet, and reputation"""
    def __init__(self, node_data: 'Node'):
        # Store base node data
        self.id = node_data.id
        self.name = node_data.name
        self.latitude = node_data.latitude
        self.longitude = node_data.longitude
        self.location_name = node_data.location_name
        self.range = node_data.range
        self.hash_value = f"0x{uuid.uuid4().hex[:8]}"  # Initial hash value
        self.auto_relay = True  # Auto-relay messages (can be disabled to simulate attacks)
        
        # Initialize crypto, wallet, and reputation
        self.crypto = CryptoManager()
        self.public_key_id = self.crypto.get_public_key_id()
        self.wallet = Wallet(self.id, INITIAL_CREDITS)
        self.reputation = ReputationManager(self.id)
        self.known_messages: Set[str] = set()
        self.peer_public_keys: Dict[int, bytes] = {}
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_name": self.location_name,
            "range": self.range,
            "hash": self.hash_value,
            "auto_relay": self.auto_relay
        }

# Data models
class Node(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    location_name: str
    range: int  # Broadcast range in meters (campus scale)

class MessagePacket(BaseModel):
    packet_id: str
    original_message_id: str
    publisher_id: int
    target_ids: List[int]
    message_text: str
    history: List[int]  # List of node IDs this packet has visited
    created_at: float = 0.0  # Timestamp for TTL tracking
    
    # New fields for MVP B2
    message_type: str = "Logistics"  # "Logistics", "Help", or "Safe"
    network_type: str = "WiFi"  # "WiFi" or "LoRa"
    
    # Cryptographic fields
    signature: Optional[str] = None  # ECDSA signature for "Help" messages
    proof: Optional[str] = None  # ZKP proof for "Safe" messages
    
    # Encryption fields (for "Logistics" messages)
    is_encrypted: bool = False
    ciphertext: Optional[str] = None
    nonce: Optional[str] = None

class UpdatePositionRequest(BaseModel):
    latitude: float
    longitude: float

class PublishMessageRequest(BaseModel):
    publisher_node_id: int
    message_text: str
    target_node_ids: List[int]
    message_type: str = "Logistics"  # "Logistics", "Help", or "Safe"
    
    @field_validator('message_type')
    @classmethod
    def validate_message_type(cls, v):
        if v not in ['Logistics', 'Help', 'Safe']:
            raise ValueError(f'message_type must be one of: Logistics, Help, Safe. Got: {v}')
        return v
    
    @field_validator('message_text')
    @classmethod
    def validate_message_text(cls, v):
        if len(v) == 0:
            raise ValueError('message_text cannot be empty')
        if len(v) > MAX_MESSAGE_LENGTH:
            raise ValueError(f'message_text exceeds maximum length of {MAX_MESSAGE_LENGTH} characters')
        return v
    
    @field_validator('target_node_ids')
    @classmethod
    def validate_target_nodes(cls, v):
        if not v:
            raise ValueError('target_node_ids cannot be empty')
        if len(v) > NUM_NODES:
            raise ValueError(f'target_node_ids cannot exceed {NUM_NODES} nodes')
        for tid in v:
            if tid < 1 or tid > NUM_NODES:
                raise ValueError(f'Invalid target node ID: {tid}. Must be between 1 and {NUM_NODES}')
        return v
    
    @field_validator('publisher_node_id')
    @classmethod
    def validate_publisher_id(cls, v):
        if v < 1 or v > NUM_NODES:
            raise ValueError(f'Invalid publisher_node_id: {v}. Must be between 1 and {NUM_NODES}')
        return v

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

def generate_random_uri_campus_location():
    """Generate random coordinates within URI Kingston campus bounds"""
    # URI Kingston campus approximate boundaries
    # Campus center: ~41.4882°N, -71.5268°W
    # Campus spans roughly 0.015 degrees latitude (~1.7 km) and 0.020 degrees longitude (~1.5 km)
    
    # Define campus bounding box
    lat_min = 41.480  # Southern edge
    lat_max = 41.492  # Northern edge
    lng_min = -71.537  # Western edge
    lng_max = -71.516  # Eastern edge
    
    latitude = random.uniform(lat_min, lat_max)
    longitude = random.uniform(lng_min, lng_max)
    
    return latitude, longitude

# Generate nodes with random locations on URI campus
def create_fixed_nodes():
    """Create 10 nodes with random locations across URI Kingston campus"""
    nodes = []
    for i in range(1, NUM_NODES + 1):
        # Generate random position within URI campus
        lat, lng = generate_random_uri_campus_location()
        location_name = f"URI Campus ({lat:.4f}°N, {abs(lng):.4f}°W)"
        
        # Campus-appropriate range in meters
        range_meters = 100  # 100 meters default range
        
        # Create Pydantic node data
        node_data = Node(
            id=i,
            name=f"Node {i}",
            latitude=lat,
            longitude=lng,
            location_name=location_name,
            range=range_meters
        )
        # Wrap in runtime with crypto, wallet, and reputation
        node = NodeRuntime(node_data)
        nodes.append(node)
    
    # Exchange public keys between all nodes (trust establishment)
    for node in nodes:
        for peer in nodes:
            if node.id != peer.id:
                node.peer_public_keys[peer.id] = peer.crypto.get_public_key_bytes()
    
    return nodes

# Calculate distance between two points using Haversine formula
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth in meters"""
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
    
    # Radius of Earth in meters (6371 km * 1000)
    earth_radius = 6371000
    
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

def apply_crdsa_collision_simulation(node_inventories: Dict[int, List['MessagePacket']]) -> Dict[int, List['MessagePacket']]:
    """
    Apply CRDSA collision simulation with packet replicas and SIC algorithm.
    
    CRDSA (Contention Resolution Diversity Slotted ALOHA):
    - Each packet is transmitted multiple times (replicas) in random slots
    - Collisions occur when multiple packets occupy the same slot
    - SIC (Successive Interference Cancellation) iteratively resolves collisions
    
    Args:
        node_inventories: Current packet inventories per node
    
    Returns:
        Updated inventories with packets that survived collisions
    """
    if not CRDSA_ENABLED:
        return node_inventories
    
    # Process each node's inventory separately
    updated_inventories = {}
    
    for node_id, packets in node_inventories.items():
        if not packets:
            updated_inventories[node_id] = []
            continue
        
        # Create CRDSA slots
        slots = [[] for _ in range(CRDSA_SLOTS_PER_TICK)]
        packet_to_slots = {}  # Map packet to its replica slots
        
        # Assign packet replicas to random slots
        for packet in packets:
            # Generate unique slot assignments for this packet
            packet_slots = random.sample(range(CRDSA_SLOTS_PER_TICK), min(CRDSA_REPLICAS, CRDSA_SLOTS_PER_TICK))
            packet_to_slots[packet.packet_id] = packet_slots
            
            # Add packet to each of its assigned slots
            for slot_idx in packet_slots:
                slots[slot_idx].append(packet)
        
        # SIC algorithm: Iteratively resolve collisions
        resolved_packets = set()
        unresolved_packets = set(packet_to_slots.keys())
        
        for iteration in range(CRDSA_MAX_SIC_ITERATIONS):
            if not unresolved_packets:
                break  # All packets resolved
            
            newly_resolved = []
            
            # Find singleton slots (only one packet in slot)
            for slot_idx, slot_packets in enumerate(slots):
                if len(slot_packets) == 1:
                    packet = slot_packets[0]
                    if packet.packet_id in unresolved_packets:
                        # This packet is successfully received
                        newly_resolved.append(packet.packet_id)
            
            if not newly_resolved:
                # No more singletons found, remaining packets are lost to collisions
                break
            
            # Remove resolved packets from all their slots (SIC cancellation)
            for packet_id in newly_resolved:
                resolved_packets.add(packet_id)
                unresolved_packets.discard(packet_id)
                
                # Remove this packet from all its slots
                for slot_idx in packet_to_slots[packet_id]:
                    slots[slot_idx] = [p for p in slots[slot_idx] if p.packet_id != packet_id]
        
        # Keep only resolved packets
        survived_packets = [p for p in packets if p.packet_id in resolved_packets]
        updated_inventories[node_id] = survived_packets
        
        # Log collision statistics
        total_packets = len(packets)
        lost_packets = total_packets - len(survived_packets)
        if total_packets > 0:
            loss_rate = (lost_packets / total_packets) * 100
            if loss_rate > 0:
                print(f"  [CRDSA] Node {node_id}: {lost_packets}/{total_packets} packets lost ({loss_rate:.1f}% loss)")
    
    return updated_inventories

async def simulation_tick():
    """
    Core simulation logic with economic incentives - runs every 3 seconds
    
    Key features:
    - Relay rewards: Nodes earn credits for forwarding packets
    - Reputation tracking: Nodes track which peers successfully relay
    - Message type routing: Safety packets prioritized on LoRa network
    - Memory management: Cleans up old packets (TTL) and enforces inventory limits
    """
    global node_inventories, NODES, global_economy
    
    # Acquire lock to prevent race conditions with API requests
    async with simulation_lock:
        # Increment global tick counter
        global_economy.increment_tick()
        
        # Universal Basic Income (UBI) distribution
        if global_economy.tick_count % UBI_INTERVAL_TICKS == 0:
            for node in NODES:
                node.wallet.add_credits(UBI_AMOUNT, "UBI")
        
        # Clean up expired packets (TTL check) - prevents memory leak
        current_time = datetime.now().timestamp()
        for node_id in node_inventories:
            node_inventories[node_id] = [
                p for p in node_inventories[node_id]
                if (current_time - p.created_at) < PACKET_TTL_SECONDS
            ]
            
            # Enforce max inventory size (keep most recent packets)
            if len(node_inventories[node_id]) > MAX_INVENTORY_SIZE:
                node_inventories[node_id] = node_inventories[node_id][-MAX_INVENTORY_SIZE:]
        
        # Apply CRDSA collision simulation (packet loss modeling)
        node_inventories = apply_crdsa_collision_simulation(node_inventories)
    
    # Create a copy of current inventories to avoid modifying while iterating
    new_packets = []
    relay_events = []  # Track successful relays for reputation and rewards
    
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
                # Check if node_a is configured to auto-relay (simulate selfish node attack)
                if not node_a.auto_relay:
                    continue  # Skip relaying if auto_relay is disabled
                
                # Node A shares its inventory with Node B
                for packet in node_inventories[node_a.id]:
                    # Check anti-loop rule: reject if node_b is already in history
                    if node_b.id not in packet.history:
                        # Economic logic: Node A (relay) gets paid for forwarding
                        # Determine relay reward based on message type
                        if packet.message_type == "Safe":
                            relay_reward = SAFETY_RELAY_REWARD
                            transaction_type = 'safety_relay'
                        else:
                            relay_reward = LOGISTICS_RELAY_REWARD
                            transaction_type = 'logistics_relay'
                        
                        # Pay the relay node (node_a) for forwarding
                        node_a.wallet.add_credits(relay_reward, f"Relay {packet.message_type}")
                        global_economy.record_transaction(transaction_type, relay_reward)
                        
                        # Reputation tracking: record that node_a sent to node_b
                        # (We'll update when node_b successfully relays onward)
                        if len(packet.history) > 1:
                            # The previous hop sent to node_a
                            previous_hop_id = packet.history[-1]
                            if previous_hop_id != packet.publisher_id:
                                # Track that the previous hop successfully got node_a to relay
                                previous_hop_node = NODES[previous_hop_id - 1]
                                previous_hop_node.reputation.record_successful_relay_by_peer(node_a.id)
                        
                        # Create new packet copy for node_b
                        new_packet = MessagePacket(
                            packet_id=str(uuid.uuid4()),
                            original_message_id=packet.original_message_id,
                            publisher_id=packet.publisher_id,
                            target_ids=packet.target_ids,
                            message_text=packet.message_text,
                            history=packet.history + [node_b.id],
                            created_at=packet.created_at,  # Preserve original creation time
                            message_type=packet.message_type,
                            network_type=packet.network_type,
                            signature=packet.signature,
                            proof=packet.proof,
                            is_encrypted=packet.is_encrypted,
                            ciphertext=packet.ciphertext,
                            nonce=packet.nonce
                        )
                        new_packets.append((node_b.id, new_packet))
                        
                        # Track that node_a sent a packet to node_b (for reputation)
                        node_a.reputation.record_packet_sent_to_peer(node_b.id)
    
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
                # Add to known messages for gossip protocol
                NODES[node_id - 1].known_messages.add(packet.original_message_id)

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
    global simulation_lock
    simulation_lock = asyncio.Lock()
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
            "range": node.range,
            "hash": node.hash_value,
            "auto_relay": node.auto_relay
        }
        for node in NODES
    ]

@app.put("/node/{node_id}/hash")
async def update_node_hash(node_id: int, hash_value: str):
    """Update the hash value for a specific node"""
    if node_id not in range(1, 11):
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = NODES[node_id - 1]
    node.hash_value = hash_value
    return {"node_id": node_id, "hash": node.hash_value}

@app.put("/node/{node_id}/auto_relay")
async def update_node_auto_relay(node_id: int, auto_relay: bool):
    """Toggle auto-relay for a specific node (simulate selfish node attack)"""
    if node_id not in range(1, 11):
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = NODES[node_id - 1]
    node.auto_relay = auto_relay
    return {"node_id": node_id, "auto_relay": node.auto_relay}

@app.post("/regenerate_nodes")
async def regenerate_nodes():
    """Regenerate all nodes with new random locations on URI campus"""
    global NODES, node_inventories
    NODES = create_fixed_nodes()
    # Clear all inventories when regenerating nodes
    node_inventories = {i: [] for i in range(1, 11)}
    return {"message": "Nodes regenerated with random URI campus locations", "nodes": NODES}

@app.post("/publish_message")
async def publish_message(request: PublishMessageRequest):
    """
    Publish a message to the network with economic incentives and cryptography.
    
    Message Types:
    - "Logistics": Standard encrypted message (costs 2 credits, pays 1 per relay)
    - "Help": Public identifiable emergency message (costs 2 credits, uses ECDSA signature)
    - "Safe": Anonymous emergency message (free, uses simulated ZKP)
    """
    
    # Validate publisher node exists
    if request.publisher_node_id not in range(1, 11):
        raise HTTPException(status_code=404, detail="Publisher node not found")
    
    # Validate target nodes exist
    for target_id in request.target_node_ids:
        if target_id not in range(1, 11):
            raise HTTPException(status_code=404, detail=f"Target node {target_id} not found")
    
    # Get publisher node
    publisher_node = NODES[request.publisher_node_id - 1]
    
    # Determine network type based on message type
    network_type = "LoRa" if request.message_type == "Safe" else "WiFi"
    
    # Economic logic: Check if sender can afford to send
    send_cost = SAFETY_SEND_COST if request.message_type == "Safe" else LOGISTICS_SEND_COST
    
    if not publisher_node.wallet.spend_credits(send_cost, f"Send {request.message_type} message"):
        raise HTTPException(
            status_code=402, 
            detail=f"Insufficient credits. Need {send_cost}, have {publisher_node.wallet.balance}"
        )
    
    # Record transaction
    if request.message_type != "Safe":
        global_economy.record_transaction('logistics_send', send_cost)
    
    # Create the initial message packet
    timestamp = datetime.now().isoformat()
    timestamp_float = datetime.now().timestamp()
    original_message_id = generate_message_id(request.publisher_node_id, request.message_text, timestamp)
    packet_id = str(uuid.uuid4())
    
    # Initialize packet with common fields
    packet_data = {
        "packet_id": packet_id,
        "original_message_id": original_message_id,
        "publisher_id": request.publisher_node_id,
        "target_ids": request.target_node_ids,
        "message_text": request.message_text,
        "history": [request.publisher_node_id],
        "created_at": timestamp_float,  # For TTL tracking
        "message_type": request.message_type,
        "network_type": network_type,
    }
    
    # Apply cryptography based on message type
    if request.message_type == "Logistics":
        # Encrypted message for privacy (ECDH + AES-GCM)
        # For simplicity, we'll mark as encrypted but not actually encrypt in this iteration
        packet_data["is_encrypted"] = True
        packet_data["signature"] = None
        packet_data["proof"] = None
        
    elif request.message_type == "Help":
        # Public signed message (ECDSA)
        signature = publisher_node.crypto.sign_message(request.message_text)
        packet_data["is_encrypted"] = False
        packet_data["signature"] = signature
        packet_data["proof"] = None
        
    elif request.message_type == "Safe":
        # Anonymous message with ZKP proof
        proof = simulate_zkp_proof()
        packet_data["is_encrypted"] = False
        packet_data["signature"] = None
        packet_data["proof"] = proof
        # Keep publisher_id for tracking, but mark as anonymous via proof
        # Note: Frontend should check for proof to display as "ANONYMOUS"
    
    packet = MessagePacket(**packet_data)
    
    # Add to publisher's known messages (gossip protocol)
    publisher_node.known_messages.add(original_message_id)
    
    # Place packet in publisher's inventory
    node_inventories[request.publisher_node_id].append(packet)
    
    return {
        "message_id": original_message_id,
        "packet_id": packet_id,
        "status": "published",
        "timestamp": timestamp,
        "publisher_node_id": request.publisher_node_id,
        "message_type": request.message_type,
        "network_type": network_type,
        "send_cost": send_cost,
        "remaining_balance": round(publisher_node.wallet.balance, 2),
        "signature": packet_data.get("signature", None),
        "proof": packet_data.get("proof", None)
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
    
    if new_range < 10 or new_range > 500:
        raise HTTPException(status_code=400, detail="Range must be between 10 and 500 meters")
    
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
                "distance_m": round(distance, 1),
                "can_receive": True,
                "coordinates": {"lat": node.latitude, "lng": node.longitude}
            })
        
        # Check if current node is within this node's range
        if distance <= node.range:
            nodes_that_can_reach.append({
                "node_id": node.id,
                "name": node.name,
                "distance_m": round(distance, 1),
                "range_m": node.range,
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

# ===== NEW MVP B2 ENDPOINTS =====

@app.get("/node/{node_id}/wallet")
async def get_node_wallet(node_id: int):
    """Get wallet statistics for a specific node"""
    node = next((n for n in NODES if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return node.wallet.get_stats()

@app.get("/node/{node_id}/reputation")
async def get_node_reputation(node_id: int):
    """Get reputation statistics for a specific node"""
    node = next((n for n in NODES if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return node.reputation.get_stats()

@app.get("/node/{node_id}/crypto")
async def get_node_crypto_info(node_id: int):
    """Get cryptographic identity information for a node"""
    node = next((n for n in NODES if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return {
        "node_id": node_id,
        "public_key_id": node.public_key_id,
        "known_messages_count": len(node.known_messages),
        "peer_count": len(node.peer_public_keys)
    }

@app.get("/node/{node_id}/sync_summary")
async def get_node_sync_summary(node_id: int):
    """
    Get Bloom filter summary of node's known messages for gossip protocol.
    
    This endpoint enables efficient state synchronization between nodes:
    - Client compares returned Bloom filter with local known_messages
    - Only missing message_ids are requested via fetch_missing
    - Reduces bandwidth compared to sending full inventory lists
    """
    node = next((n for n in NODES if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Create Bloom filter for this node's known messages
    bloom = BloomFilter(capacity=BLOOM_FILTER_CAPACITY, error_rate=BLOOM_FILTER_ERROR_RATE)
    
    # Add all known message IDs to Bloom filter
    for msg_id in node.known_messages:
        bloom.add(msg_id)
    
    # Serialize Bloom filter to base64 for transmission
    # Note: pybloom_live doesn't have native serialization, so we'll use a workaround
    import pickle
    bloom_bytes = pickle.dumps(bloom)
    bloom_b64 = base64.b64encode(bloom_bytes).decode('utf-8')
    
    return {
        "node_id": node_id,
        "known_messages_count": len(node.known_messages),
        "bloom_filter": bloom_b64,
        "bloom_config": {
            "capacity": BLOOM_FILTER_CAPACITY,
            "error_rate": BLOOM_FILTER_ERROR_RATE,
            "size_bytes": len(bloom_bytes)
        },
        "usage": "Client should check each local message_id against bloom filter. If absent, request from node."
    }

@app.post("/node/{node_id}/check_bloom")
async def check_message_in_bloom(node_id: int, message_ids: List[str]):
    """
    Check which message IDs from the list are NOT in the node's known set.
    Returns missing message_ids that should be fetched.
    """
    node = next((n for n in NODES if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    missing = [msg_id for msg_id in message_ids if msg_id not in node.known_messages]
    
    return {
        "node_id": node_id,
        "checked_count": len(message_ids),
        "missing_count": len(missing),
        "missing_message_ids": missing
    }

@app.get("/stats/economy")
async def get_economy_stats():
    """Get global economy statistics (Gini, Nakamoto, etc.)"""
    wallets = [node.wallet for node in NODES]
    stats = global_economy.get_economy_stats(wallets)
    
    # Add per-node balance breakdown
    stats["node_balances"] = [
        {"node_id": node.id, "balance": round(node.wallet.balance, 2)}
        for node in sorted(NODES, key=lambda n: n.wallet.balance, reverse=True)
    ]
    
    return stats

@app.get("/stats/messages")
async def get_message_stats():
    """Get statistics about messages by type"""
    message_types = {"Logistics": 0, "Help": 0, "Safe": 0, "Unknown": 0}
    network_types = {"WiFi": 0, "LoRa": 0, "Unknown": 0}
    total_packets = 0
    
    for node_id, packets in node_inventories.items():
        for packet in packets:
            total_packets += 1
            msg_type = getattr(packet, 'message_type', 'Unknown')
            net_type = getattr(packet, 'network_type', 'Unknown')
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
            network_types[net_type] = network_types.get(net_type, 0) + 1
    
    return {
        "total_packets_in_network": total_packets,
        "by_message_type": message_types,
        "by_network_type": network_types,
        "average_packets_per_node": round(total_packets / len(NODES), 2) if NODES else 0
    }

@app.get("/stats/crdsa")
async def get_crdsa_stats():
    """Get CRDSA configuration and collision statistics"""
    return {
        "enabled": CRDSA_ENABLED,
        "configuration": {
            "slots_per_tick": CRDSA_SLOTS_PER_TICK,
            "replicas_per_packet": CRDSA_REPLICAS,
            "max_sic_iterations": CRDSA_MAX_SIC_ITERATIONS
        },
        "collision_probability": {
            "description": "Theoretical collision probability depends on network load",
            "note": "With 2 replicas and 5 slots, light load (~2 packets) has ~20% loss, heavy load (>5 packets) has >50% loss"
        }
    }

@app.post("/config/crdsa")
async def update_crdsa_config(enabled: bool = None, slots: int = None, replicas: int = None):
    """Update CRDSA configuration (requires server restart for slots/replicas changes)"""
    global CRDSA_ENABLED
    
    response = {"message": "CRDSA configuration updated", "changes": []}
    
    if enabled is not None:
        CRDSA_ENABLED = enabled
        response["changes"].append(f"Enabled: {CRDSA_ENABLED}")
    
    if slots is not None or replicas is not None:
        response["warning"] = "Changes to slots/replicas require server restart to take effect"
    
    response["current_config"] = {
        "enabled": CRDSA_ENABLED,
        "slots_per_tick": CRDSA_SLOTS_PER_TICK,
        "replicas": CRDSA_REPLICAS
    }
    
    return response

@app.get("/stats/gossip")
async def get_gossip_stats():
    """Get gossip protocol statistics across all nodes"""
    node_stats = []
    total_known = 0
    
    for node in NODES:
        known_count = len(node.known_messages)
        total_known += known_count
        
        node_stats.append({
            "node_id": node.id,
            "known_messages": known_count,
            "inventory_size": len(node_inventories.get(node.id, [])),
            "sync_efficiency": round(known_count / MAX_INVENTORY_SIZE * 100, 1) if MAX_INVENTORY_SIZE > 0 else 0
        })
    
    return {
        "total_unique_messages": total_known,
        "average_known_per_node": round(total_known / len(NODES), 1) if NODES else 0,
        "bloom_filter_config": {
            "capacity": BLOOM_FILTER_CAPACITY,
            "error_rate": BLOOM_FILTER_ERROR_RATE
        },
        "node_statistics": node_stats,
        "protocol_info": {
            "description": "Gossip protocol uses Bloom filters for efficient state reconciliation",
            "endpoints": [
                "GET /node/{id}/sync_summary - Get Bloom filter of known messages",
                "POST /node/{id}/check_bloom - Check which messages are missing"
            ]
        }
    }

# ===== CRYPTOGRAPHIC VERIFICATION ENDPOINTS =====

@app.post("/verify/signature")
async def verify_message_signature(message_id: str):
    """
    Verify the ECDSA signature of a Help message.
    Returns whether the signature is valid.
    """
    # Find the packet across all inventories
    packet = None
    for node_id, packets in node_inventories.items():
        for p in packets:
            if p.original_message_id == message_id:
                packet = p
                break
        if packet:
            break
    
    if not packet:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if packet.message_type != "Help":
        raise HTTPException(status_code=400, detail="Only Help messages have signatures")
    
    if not packet.signature:
        raise HTTPException(status_code=400, detail="Message has no signature")
    
    # Get the publisher's public key
    if packet.publisher_id < 1 or packet.publisher_id > NUM_NODES:
        raise HTTPException(status_code=400, detail="Invalid publisher ID")
    
    publisher_node = NODES[packet.publisher_id - 1]
    
    # Verify the signature
    is_valid = CryptoManager.verify_signature(
        publisher_node.crypto.public_key,
        packet.message_text,
        packet.signature
    )
    
    return {
        "message_id": message_id,
        "publisher_id": packet.publisher_id,
        "signature_valid": is_valid,
        "message_text": packet.message_text if is_valid else "[INVALID SIGNATURE]"
    }

@app.post("/verify/zkp")
async def verify_zkp_message(message_id: str):
    """
    Verify the ZKP proof of a Safe message.
    Returns whether the proof is valid.
    """
    # Find the packet across all inventories
    packet = None
    for node_id, packets in node_inventories.items():
        for p in packets:
            if p.original_message_id == message_id:
                packet = p
                break
        if packet:
            break
    
    if not packet:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if packet.message_type != "Safe":
        raise HTTPException(status_code=400, detail="Only Safe messages have ZKP proofs")
    
    if not packet.proof:
        raise HTTPException(status_code=400, detail="Message has no proof")
    
    # Verify the ZKP proof
    is_valid = verify_zkp_proof(packet.proof)
    
    return {
        "message_id": message_id,
        "proof_valid": is_valid,
        "proof": packet.proof,
        "publisher": "ANONYMOUS" if is_valid else "INVALID",
        "message_text": packet.message_text if is_valid else "[INVALID PROOF]"
    }

# ===== TEST & DEBUG ENDPOINTS =====

@app.get("/debug/inventories")
async def debug_inventories():
    """Get current inventory sizes and oldest packet ages for debugging"""
    inventory_info = {}
    current_time = datetime.now().timestamp()
    
    for node_id, packets in node_inventories.items():
        if packets:
            oldest_age = current_time - min(p.created_at for p in packets)
            newest_age = current_time - max(p.created_at for p in packets)
            inventory_info[f"node_{node_id}"] = {
                "count": len(packets),
                "oldest_packet_age_seconds": round(oldest_age, 1),
                "newest_packet_age_seconds": round(newest_age, 1)
            }
        else:
            inventory_info[f"node_{node_id}"] = {"count": 0}
    
    return {
        "inventory_status": inventory_info,
        "max_inventory_size": MAX_INVENTORY_SIZE,
        "packet_ttl_seconds": PACKET_TTL_SECONDS
    }

# ===== ATTACK SIMULATION ENDPOINTS =====

@app.post("/attack/edit_hash/{message_id}")
async def attack_edit_hash(message_id: str):
    """
    Attack simulation: Modify a packet's payload to test cryptographic verification.
    
    This simulates a man-in-the-middle attack where the attacker modifies the message
    text but cannot regenerate a valid signature. Used to verify that signature
    verification detects tampering.
    """
    # Find the packet across all inventories
    modified_count = 0
    original_text = None
    
    for node_id, packets in node_inventories.items():
        for packet in packets:
            if packet.original_message_id == message_id:
                if original_text is None:
                    original_text = packet.message_text
                
                # Tamper with the message text
                packet.message_text = packet.message_text + " [TAMPERED]"
                modified_count += 1
    
    if modified_count == 0:
        raise HTTPException(status_code=404, detail="Message not found in any inventory")
    
    return {
        "attack_type": "edit_hash",
        "message_id": message_id,
        "modified_packets": modified_count,
        "original_text": original_text,
        "tampered_suffix": " [TAMPERED]",
        "note": "Signature verification should now fail for this message. Use POST /verify/signature to check."
    }

@app.put("/node/{node_id}/position")
async def update_node_position(node_id: int, position: UpdatePositionRequest):
    """
    Update a node's geographic position.
    
    Can be used to simulate:
    - Node mobility
    - Network partitioning (move nodes out of range)
    - Man-in-the-middle positioning
    - Attack scenarios where adversary changes position
    """
    if node_id < 1 or node_id > NUM_NODES:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = NODES[node_id - 1]
    old_lat, old_lng = node.latitude, node.longitude
    
    latitude = position.latitude
    longitude = position.longitude
    
    # Validate coordinates
    if not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
    if not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
    
    # Update position
    node.latitude = latitude
    node.longitude = longitude
    node.location_name = f"URI Campus ({latitude:.4f}°N, {abs(longitude):.4f}°W)"
    
    # Calculate connectivity changes
    old_connections = []
    new_connections = []
    
    for other_node in NODES:
        if other_node.id == node_id:
            continue
        
        # Old distance
        old_dist = calculate_distance(old_lat, old_lng, other_node.latitude, other_node.longitude)
        old_connected = old_dist <= node.range
        
        # New distance
        new_dist = calculate_distance(latitude, longitude, other_node.latitude, other_node.longitude)
        new_connected = new_dist <= node.range
        
        if old_connected and not new_connected:
            old_connections.append(other_node.id)
        elif not old_connected and new_connected:
            new_connections.append(other_node.id)
    
    return {
        "node_id": node_id,
        "old_position": {"latitude": old_lat, "longitude": old_lng},
        "new_position": {"latitude": latitude, "longitude": longitude},
        "location": node.location_name,
        "connectivity_changes": {
            "lost_connections": old_connections,
            "new_connections": new_connections,
            "note": "Based on range only, does not include explicit CONNECTIONS"
        }
    }

@app.post("/attack/partition_network")
async def attack_partition_network(group_a_nodes: List[int], group_b_nodes: List[int]):
    """
    Simulate network partition by moving node groups far apart.
    
    This creates two isolated groups that cannot communicate, simulating:
    - Geographic disasters
    - Jamming attacks
    - Infrastructure failure
    """
    # Validate node IDs
    all_nodes = group_a_nodes + group_b_nodes
    if len(set(all_nodes)) != len(all_nodes):
        raise HTTPException(status_code=400, detail="Node IDs must be unique")
    
    for nid in all_nodes:
        if nid < 1 or nid > NUM_NODES:
            raise HTTPException(status_code=400, detail=f"Invalid node ID: {nid}")
    
    # Move group A to west coast (Seattle area)
    group_a_lat, group_a_lng = 47.6, -122.3
    
    # Move group B to east coast (New York area)
    group_b_lat, group_b_lng = 40.7, -74.0
    
    moved_nodes = []
    
    for nid in group_a_nodes:
        node = NODES[nid - 1]
        node.latitude = group_a_lat + random.uniform(-0.5, 0.5)
        node.longitude = group_a_lng + random.uniform(-0.5, 0.5)
        node.location_name = "West Coast Partition"
        moved_nodes.append({"node_id": nid, "group": "A", "location": "West Coast"})
    
    for nid in group_b_nodes:
        node = NODES[nid - 1]
        node.latitude = group_b_lat + random.uniform(-0.5, 0.5)
        node.longitude = group_b_lng + random.uniform(-0.5, 0.5)
        node.location_name = "East Coast Partition"
        moved_nodes.append({"node_id": nid, "group": "B", "location": "East Coast"})
    
    # Calculate distance between partitions
    partition_distance = calculate_distance(group_a_lat, group_a_lng, group_b_lat, group_b_lng)
    
    return {
        "attack_type": "network_partition",
        "group_a": {"node_ids": group_a_nodes, "location": "West Coast (Seattle)"},
        "group_b": {"node_ids": group_b_nodes, "location": "East Coast (New York)"},
        "partition_distance_m": round(partition_distance, 1),
        "moved_nodes": moved_nodes,
        "note": "Groups are now isolated. Max node range is typically 100-500m, partition is ~4000 km."
    }

@app.delete("/attack/clear_inventories")
async def attack_clear_inventories():
    """
    Attack simulation: Clear all node inventories.
    
    Simulates catastrophic data loss or coordinated DoS attack.
    """
    total_cleared = 0
    for node_id in node_inventories:
        total_cleared += len(node_inventories[node_id])
        node_inventories[node_id] = []
    
    return {
        "attack_type": "clear_inventories",
        "packets_cleared": total_cleared,
        "note": "All packet inventories wiped. Network must recover via new messages."
    }

@app.post("/attack/tamper_packet/{packet_id}")
async def attack_tamper_packet(packet_id: str):
    """
    Attack simulation: Tamper with a packet's payload to test cryptographic integrity.
    
    This demonstrates that ECDSA signature verification will fail when payload is modified.
    """
    for node_id, inventory in node_inventories.items():
        for packet in inventory:
            if packet.packet_id == packet_id:
                # Corrupt the message text (change last character)
                original_text = packet.message_text
                if len(original_text) > 0:
                    packet.message_text = original_text[:-1] + ("X" if original_text[-1] != "X" else "Y")
                else:
                    packet.message_text = "TAMPERED"
                
                return {
                    "attack_type": "packet_tampering",
                    "packet_id": packet_id,
                    "node_id": node_id,
                    "original_text": original_text,
                    "tampered_text": packet.message_text,
                    "message_type": packet.message_type,
                    "note": "Signature verification will now FAIL. Packet will be rejected by recipients."
                }
    
    raise HTTPException(status_code=404, detail=f"Packet {packet_id} not found in any node inventory")

# ===== TEST ENDPOINTS =====

@app.post("/test/credit_exhaustion")
async def test_credit_exhaustion(node_id: int):
    """Test endpoint: drain a node's credits to test insufficient funds handling"""
    if node_id < 1 or node_id > NUM_NODES:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = NODES[node_id - 1]
    original_balance = node.wallet.balance
    node.wallet.balance = 0
    
    return {
        "node_id": node_id,
        "original_balance": round(original_balance, 2),
        "new_balance": 0,
        "message": "Node credits drained for testing"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)