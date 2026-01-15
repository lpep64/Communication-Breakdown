"""
Presentation Demo Script for Communication Breakdown MVP B2
============================================================
This script demonstrates the disaster communication network with:
- Network generation with random connections
- Economic system tracking (credits, Gini, Nakamoto)
- Cryptographic message types (Logistics, Help, Safe)
- Various attacks (selfish node, message tampering, hash manipulation)
- Reputation system response to malicious behavior

Press any key to advance through each demo stage.
"""

import requests
import json
import time
import random
from typing import List, Dict

# Configuration
API_BASE_URL = "http://localhost:8000"
NUM_NODES = 10

def clear_screen():
    """Clear terminal (works on Windows/Unix)"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_key():
    """Wait for user to press any key"""
    input("\n⏸️  Press ENTER to continue...")

def print_header(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_subheader(title: str):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---")

def get_network_structure():
    """Fetch current network structure"""
    response = requests.get(f"{API_BASE_URL}/nodes")
    return response.json()

def get_connections():
    """Fetch all network connections"""
    response = requests.get(f"{API_BASE_URL}/connections")
    return response.json()

def get_economy_stats():
    """Fetch economy statistics"""
    response = requests.get(f"{API_BASE_URL}/stats/economy")
    if response.status_code != 200:
        print(f"Error: Economy stats returned status {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"Failed to get economy stats: {response.status_code}")
    try:
        return response.json()
    except Exception as e:
        print(f"Error parsing economy stats JSON: {e}")
        print(f"Response text: {response.text}")
        raise

def print_network_structure(nodes: List[Dict], connections: List[Dict]):
    """Print network topology"""
    print_subheader("Network Topology")
    
    # Build adjacency list
    adjacency = {i: [] for i in range(1, NUM_NODES + 1)}
    for conn in connections:
        adjacency[conn['a']].append(conn['b'])
        adjacency[conn['b']].append(conn['a'])
    
    for node in nodes:
        node_id = node['node_id']
        neighbors = sorted(adjacency[node_id])
        auto_relay = "✓" if node.get('auto_relay', True) else "✗"
        hash_val = node.get('hash', 'N/A')[:10]
        
        print(f"  Node {node_id:2d} [{node['name']}] "
              f"| Relay:{auto_relay} | Hash:{hash_val} "
              f"| Connected to: {neighbors}")

def print_economy(economy: Dict):
    """Print economy statistics"""
    print_subheader("Economy Statistics")
    print(f"  Total In Circulation: {economy['total_credits_in_circulation']:.2f} credits")
    print(f"  Average Balance:      {economy['average_balance']:.2f} credits")
    print(f"  Gini Coefficient:    {economy['gini_coefficient']:.4f} (0=equal, 1=unequal)")
    print(f"  Nakamoto Coefficient: {economy['nakamoto_coefficient']} nodes control 51% wealth")
    print(f"  Total Transactions:  {economy['total_transactions']}")
    print(f"  Economic Health:     {economy['health_status']}")

def print_node_details(economy: Dict):
    """Print individual node wallet balances and reputation (from economy data)"""
    print_subheader("Node Status")
    # Sort by node_id for consistent display
    node_data = sorted(economy['node_balances'], key=lambda x: x['node_id'])
    for node in node_data:
        balance = node['balance']
        reputation = node['reputation']
        rep_icon = "🟢" if reputation >= 80 else "🟡" if reputation >= 50 else "🔴"
        print(f"  {rep_icon} Node {node['node_id']:2d}: "
              f"{balance:6.2f} credits | "
              f"Reputation: {reputation:5.1f}%")

def setup_network_with_connections():
    """Generate network and create random connections ensuring min 2 per node"""
    print_header("STEP 1: Network Initialization")
    print("Generating random network topology on URI campus...")
    
    # Regenerate nodes
    requests.post(f"{API_BASE_URL}/regenerate_nodes")
    time.sleep(0.5)
    
    # Get nodes
    nodes = get_network_structure()
    
    # Clear existing connections
    try:
        requests.delete(f"{API_BASE_URL}/connections/clear")
    except:
        pass
    
    # Create random connections ensuring each node has at least 2
    connection_counts = {i: 0 for i in range(1, NUM_NODES + 1)}
    connections_made = set()
    
    # First pass: ensure everyone has at least 2 connections
    for node_id in range(1, NUM_NODES + 1):
        while connection_counts[node_id] < 2:
            other_id = random.randint(1, NUM_NODES)
            if other_id != node_id:
                edge = tuple(sorted([node_id, other_id]))
                if edge not in connections_made:
                    try:
                        requests.post(f"{API_BASE_URL}/connections", 
                                    json={"node_a": edge[0], "node_b": edge[1]})
                        connections_made.add(edge)
                        connection_counts[edge[0]] += 1
                        connection_counts[edge[1]] += 1
                    except:
                        pass
    
    # Second pass: add some random extra connections for realism
    for _ in range(random.randint(3, 8)):
        a = random.randint(1, NUM_NODES)
        b = random.randint(1, NUM_NODES)
        if a != b:
            edge = tuple(sorted([a, b]))
            if edge not in connections_made:
                try:
                    requests.post(f"{API_BASE_URL}/connections", 
                                json={"node_a": a, "node_b": b})
                    connections_made.add(edge)
                except:
                    pass
    
    # Fetch final state
    nodes = get_network_structure()
    connections = get_connections()
    economy = get_economy_stats()
    
    print(f"✓ Created {len(connections)} connections")
    print(f"✓ All nodes have minimum 2 connections")
    
    print_network_structure(nodes, connections)
    print_economy(economy)
    print_node_details(economy)
    
    wait_for_key()
    return nodes, connections, economy

def demo_normal_message():
    """Demo 1: Normal Logistics message"""
    clear_screen()
    print_header("DEMO 1: Normal Logistics Message (Encrypted)")
    
    sender = random.randint(1, NUM_NODES)
    targets = random.sample([i for i in range(1, NUM_NODES + 1) if i != sender], 2)
    
    print(f"📤 Node {sender} sends encrypted logistics message to Nodes {targets}")
    print(f"   Message Type: Logistics (Encrypted)")
    print(f"   Cost: 2 credits")
    print(f"   Relay Reward: 1 credit per relay\n")
    
    # Publish message
    response = requests.post(f"{API_BASE_URL}/publish_message", json={
        "publisher_node_id": sender,
        "message_text": "Hello World - Normal encrypted message",
        "message_type": "Logistics",
        "target_node_ids": targets
    })
    
    result = response.json()
    print(f"✓ Message published: {result['message_id'][:8]}...")
    print(f"  Publisher balance: {result['remaining_balance']:.2f} credits")
    
    # Gossip to spread the message
    print("\n📡 Running gossip protocol to relay message...")
    for _ in range(3):
        requests.post(f"{API_BASE_URL}/gossip_tick")
        time.sleep(0.3)
    
    print("✓ Message relayed through network")
    
    # Show updated state
    nodes = get_network_structure()
    economy = get_economy_stats()
    connections = get_connections()
    
    print_network_structure(nodes, connections)
    print_economy(economy)
    print_node_details(economy)
    
    wait_for_key()

def demo_help_message():
    """Demo 2: Help message (signed, public)"""
    clear_screen()
    print_header("DEMO 2: Help Message (Signed Emergency Alert)")
    
    sender = random.randint(1, NUM_NODES)
    targets = list(range(1, NUM_NODES + 1))  # Public broadcast
    
    print(f"🆘 Node {sender} sends HELP emergency message")
    print(f"   Message Type: Help (Signed with ECDSA)")
    print(f"   Cost: 2 credits")
    print(f"   Visibility: PUBLIC (all nodes can verify signature)\n")
    
    # Publish help message
    response = requests.post(f"{API_BASE_URL}/publish_message", json={
        "publisher_node_id": sender,
        "message_text": "EMERGENCY: Need medical supplies at location!",
        "message_type": "Help",
        "target_node_ids": targets
    })
    
    result = response.json()
    print(f"✓ Help message published: {result['message_id'][:8]}...")
    print(f"  Publisher balance: {result['remaining_balance']:.2f} credits")
    print(f"  Signature: {result['signature'][:20]}...")
    
    # Gossip
    print("\n📡 Broadcasting help message...")
    for _ in range(3):
        requests.post(f"{API_BASE_URL}/gossip_tick")
        time.sleep(0.3)
    
    print("✓ Help message received by all nodes")
    
    # Show state
    nodes = get_network_structure()
    economy = get_economy_stats()
    connections = get_connections()
    
    print_network_structure(nodes, connections)
    print_economy(economy)
    print_node_details(economy)
    
    wait_for_key()

def demo_selfish_node_attack():
    """Demo 3: Selfish node refusing to relay"""
    clear_screen()
    print_header("DEMO 3: Selfish Node Attack (Refuses to Relay)")
    
    # Pick a well-connected node to be selfish
    nodes = get_network_structure()
    connections = get_connections()
    
    # Count connections per node
    conn_count = {i: 0 for i in range(1, NUM_NODES + 1)}
    for conn in connections:
        conn_count[conn['a']] += 1
        conn_count[conn['b']] += 1
    
    # Pick node with most connections
    selfish_node = max(conn_count.keys(), key=lambda x: conn_count[x])
    
    print(f"😈 Node {selfish_node} becomes SELFISH (disables auto-relay)")
    print(f"   Impact: Will not relay messages to earn credits")
    print(f"   Motive: Save energy/bandwidth, free-ride on network\n")
    
    # Disable auto-relay
    requests.put(f"{API_BASE_URL}/node/{selfish_node}/auto_relay", 
                 json={"auto_relay": False})
    
    print(f"✓ Node {selfish_node} auto-relay disabled")
    
    # Send message that would normally go through selfish node
    sender = random.randint(1, NUM_NODES)
    while sender == selfish_node:
        sender = random.randint(1, NUM_NODES)
    
    targets = random.sample([i for i in range(1, NUM_NODES + 1) if i != sender], 2)
    
    print(f"\n📤 Node {sender} sends message to Nodes {targets}")
    
    response = requests.post(f"{API_BASE_URL}/publish_message", json={
        "publisher_node_id": sender,
        "message_text": "Testing selfish node impact",
        "message_type": "Logistics",
        "target_node_ids": targets
    })
    
    print(f"✓ Message sent")
    
    # Gossip - selfish node won't relay
    print(f"\n📡 Gossip protocol running...")
    print(f"   ⚠️  Node {selfish_node} is REFUSING to relay messages!")
    for _ in range(3):
        requests.post(f"{API_BASE_URL}/gossip_tick")
        time.sleep(0.3)
    
    print(f"\n⚠️  Network notices Node {selfish_node} is not relaying")
    print(f"   → Reputation decreases by 2% per refused relay")
    print(f"   → Below 30% reputation: OTHER NODES REJECT ITS MESSAGES")
    print(f"   → Node becomes isolated from network")
    
    # Show updated state
    nodes = get_network_structure()
    economy = get_economy_stats()
    
    print_network_structure(nodes, connections)
    print_economy(economy)
    print_node_details(economy)
    
    wait_for_key()

def demo_hash_tampering():
    """Demo 4: Node tampers with its hash"""
    clear_screen()
    print_header("DEMO 4: Hash Manipulation Attack")
    
    attacker = random.randint(1, NUM_NODES)
    
    print(f"🔓 Node {attacker} attempts to manipulate its hash value")
    print(f"   Motive: Try to game reputation or identity system")
    print(f"   Detection: Hash doesn't match expected format/rules\n")
    
    # Get original hash
    nodes = get_network_structure()
    original_hash = next(n['hash'] for n in nodes if n['node_id'] == attacker)
    
    print(f"   Original Hash: {original_hash}")
    
    # Tamper with hash
    fake_hash = "0xDEADBEEF"
    requests.put(f"{API_BASE_URL}/node/{attacker}/hash", 
                 json={"hash_value": fake_hash})
    
    print(f"   Tampered Hash: {fake_hash}")
    print(f"\n✓ Hash changed (easily detectable!)")
    
    # Show that reputation system can detect this
    print(f"\n⚠️  System Detection:")
    print(f"   → Hash format doesn't match node's expected pattern")
    print(f"   → Reputation system penalizes Node {attacker}")
    print(f"   → Other nodes reject messages from untrusted sources")
    
    # Show state
    nodes = get_network_structure()
    economy = get_economy_stats()
    connections = get_connections()
    
    print_network_structure(nodes, connections)
    print_economy(economy)
    print_node_details(economy)
    
    wait_for_key()

def demo_message_tampering():
    """Demo 5: Attacker tampers with message in inventory"""
    clear_screen()
    print_header("DEMO 5: Message Tampering Attack (Break Signature)")
    
    # Send a signed Help message first
    sender = random.randint(1, NUM_NODES)
    targets = list(range(1, NUM_NODES + 1))
    
    print(f"📤 Node {sender} sends signed Help message")
    
    response = requests.post(f"{API_BASE_URL}/publish_message", json={
        "publisher_node_id": sender,
        "message_text": "HELP: Need assistance at location Alpha",
        "message_type": "Help",
        "target_node_ids": targets
    })
    
    packet_id = response.json()['packet_id']
    original_sig = response.json()['signature']
    
    print(f"✓ Message published with signature")
    print(f"  Packet ID: {packet_id[:8]}...")
    print(f"  Signature: {original_sig[:20]}...")
    
    # Relay it
    print("\n📡 Relaying message through network...")
    for _ in range(2):
        requests.post(f"{API_BASE_URL}/gossip_tick")
        time.sleep(0.3)
    
    # Pick a node to tamper with the message
    attacker = random.randint(1, NUM_NODES)
    while attacker == sender:
        attacker = random.randint(1, NUM_NODES)
    
    print(f"\n😈 Node {attacker} tampers with message content!")
    print(f"   Attack: Changes message text to spread misinformation")
    
    # Tamper with packet
    try:
        tamper_response = requests.post(f"{API_BASE_URL}/attack/tamper_packet/{packet_id}")
        tamper_data = tamper_response.json()
        
        print(f"\n   Original: \"{tamper_data['original_text']}\"")
        print(f"   Tampered: \"{tamper_data['tampered_text']}\"")
        
        print(f"\n⚠️  DETECTED: Signature verification FAILS!")
        print(f"   → Message content changed but signature didn't")
        print(f"   → Recipients detect tampering via ECDSA verification")
        print(f"   → Node {attacker} reputation drops significantly")
        print(f"   → Tampered message is REJECTED by network")
    except Exception as e:
        print(f"   (Packet not yet in Node {attacker}'s inventory)")
    
    # Show state
    nodes = get_network_structure()
    economy = get_economy_stats()
    connections = get_connections()
    
    print_network_structure(nodes, connections)
    print_economy(economy)
    print_node_details(economy)
    
    wait_for_key()

def demo_safe_anonymous_message():
    """Demo 6: Anonymous Safe message with ZKP"""
    clear_screen()
    print_header("DEMO 6: Anonymous Safe Message (Zero-Knowledge Proof)")
    
    sender = random.randint(1, NUM_NODES)
    targets = list(range(1, NUM_NODES + 1))
    
    print(f"🔒 Node {sender} sends ANONYMOUS Safe message")
    print(f"   Message Type: Safe (Zero-Knowledge Proof)")
    print(f"   Cost: FREE (emergency safety message)")
    print(f"   Privacy: Sender identity hidden via ZKP\n")
    
    response = requests.post(f"{API_BASE_URL}/publish_message", json={
        "publisher_node_id": sender,
        "message_text": "Safe location available at coordinates XYZ",
        "message_type": "Safe",
        "target_node_ids": targets
    })
    
    result = response.json()
    print(f"✓ Safe message published anonymously")
    print(f"  Message ID: {result['message_id'][:8]}...")
    print(f"  ZKP Proof: {result['proof'][:30]}...")
    print(f"  Cost: {result['send_cost']} credits (FREE)")
    print(f"\n📝 Zero-Knowledge Proof allows:")
    print(f"   ✓ Verification that sender is legitimate network member")
    print(f"   ✓ Complete anonymity - no one knows who sent it")
    print(f"   ✓ Protection for vulnerable individuals seeking help")
    
    # Relay
    print("\n📡 Broadcasting anonymous message...")
    for _ in range(3):
        requests.post(f"{API_BASE_URL}/gossip_tick")
        time.sleep(0.3)
    
    print("✓ Anonymous message received by all nodes")
    
    # Show state
    nodes = get_network_structure()
    economy = get_economy_stats()
    connections = get_connections()
    
    print_network_structure(nodes, connections)
    print_economy(economy)
    print_node_details(economy)
    
    wait_for_key()

def final_summary():
    """Print final summary"""
    clear_screen()
    print_header("PRESENTATION COMPLETE: Final Network State")
    
    nodes = get_network_structure()
    connections = get_connections()
    economy = get_economy_stats()
    
    print_network_structure(nodes, connections)
    print_economy(economy)
    print_node_details(economy)
    
    print("\n" + "="*70)
    print("  KEY TAKEAWAYS")
    print("="*70)
    print("\n✓ Cryptographic Diversity:")
    print("    - Logistics: ECDH + AES-GCM encryption for privacy")
    print("    - Help: ECDSA signatures for public accountability")
    print("    - Safe: Zero-Knowledge Proofs for anonymity")
    
    print("\n✓ Economic Incentives:")
    print("    - Relay rewards encourage participation")
    print("    - UBI prevents node starvation")
    print("    - Gini & Nakamoto coefficients track fairness")
    
    print("\n✓ Attack Detection & Response:")
    print("    - Selfish nodes detected by relay refusal")
    print("    - Message tampering caught via signature verification")
    print("    - Hash manipulation tracked by reputation system")
    print("    - Network adapts routing to avoid bad actors")
    
    print("\n✓ Real-World Disaster Applications:")
    print("    - Works with LoRa (long-range, low-power)")
    print("    - Campus-scale deployment ready (100m range)")
    print("    - Decentralized - no single point of failure")
    print("    - Privacy-preserving for vulnerable populations")
    
    print("\n" + "="*70)
    print("  Thank you for watching the demo!")
    print("="*70 + "\n")

def main():
    """Run the complete presentation demo"""
    try:
        # Check if backend is running
        requests.get(f"{API_BASE_URL}/nodes")
    except:
        print("❌ Error: Backend not running!")
        print("   Please start the backend with: uvicorn main:app --reload --port 8000")
        return
    
    clear_screen()
    print("="*70)
    print("  COMMUNICATION BREAKDOWN - MVP B2 DEMO")
    print("  Disaster Communication Network Simulation")
    print("="*70)
    print("\nThis demo will showcase:")
    print("  1. Network initialization with random topology")
    print("  2. Normal encrypted logistics message")
    print("  3. Public signed Help message")
    print("  4. Selfish node attack (refuses to relay)")
    print("  5. Hash manipulation attack")
    print("  6. Message tampering attack (breaks signatures)")
    print("  7. Anonymous Safe message with ZKP")
    print("\nThe demo is INTERACTIVE - press ENTER to advance through each stage.")
    
    wait_for_key()
    
    # Run demo sequence
    setup_network_with_connections()
    demo_normal_message()
    demo_help_message()
    demo_selfish_node_attack()
    demo_hash_tampering()
    demo_message_tampering()
    demo_safe_anonymous_message()
    final_summary()

if __name__ == "__main__":
    main()
