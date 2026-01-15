# Terminal-Based Presentation Demo

## Overview
`presentation_demo.py` is an **interactive terminal-based demonstration** of the Communication Breakdown disaster network. It's designed for easy presentation without needing to use the web UI.

## Why This Demo?
- ✅ **Easier to present** - Just run in terminal, press ENTER to advance
- ✅ **Clear narrative flow** - Walks through 7 demo stages automatically
- ✅ **Shows all key features** - Cryptography, economics, attacks, detection
- ✅ **Professional output** - Clean formatted display of network state
- ✅ **No UI juggling** - No need to click around the web interface

## Features Demonstrated

### 1. Network Initialization
- Random network topology on URI campus
- Ensures all nodes have minimum 2 connections
- Shows initial economic state

### 2. Normal Logistics Message
- Encrypted message (ECDH + AES-GCM simulation)
- Shows credit deduction and relay rewards
- Demonstrates gossip protocol

### 3. Help Message (Public Emergency)
- Signed with ECDSA for accountability
- Public broadcast to all nodes
- Shows signature for verification

### 4. Selfish Node Attack
- Node disables auto-relay (refuses to forward)
- Shows impact on network
- Demonstrates reputation system response

### 5. Hash Manipulation Attack
- Node changes its hash value
- Shows easy detection
- Demonstrates integrity tracking

### 6. Message Tampering Attack
- Attacker modifies message content
- Signature verification fails
- Shows cryptographic protection

### 7. Anonymous Safe Message
- Zero-Knowledge Proof for anonymity
- Free emergency message
- Privacy-preserving for vulnerable users

## How to Run

### Prerequisites
Make sure the backend is running:
```bash
cd C:\Users\lukep\Documents\Communication-Breakdown\mvp2-crypto\backend
..\crypto-env\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

### Run the Demo
In a **separate terminal**:
```bash
cd C:\Users\lukep\Documents\Communication-Breakdown\mvp2-crypto\backend
..\crypto-env\Scripts\Activate.ps1
python presentation_demo.py
```

### Controls
- **ENTER** - Advance to next stage
- **Ctrl+C** - Exit demo early (if needed)

## What You'll See

### Network Topology Display
```
Node  1 [Alpha]      | Relay:✓ | Hash:0x3a9f2b... | Connected to: [2, 5, 7]
Node  2 [Bravo]      | Relay:✓ | Hash:0x7c4e1d... | Connected to: [1, 3, 6]
...
```

### Economy Statistics
```
Total Supply:        1000.00 credits
Total In Circulation: 987.34 credits
Gini Coefficient:    0.1234 (0=equal, 1=unequal)
Nakamoto Coefficient: 4 nodes control 51% wealth
Total Transactions:  23
```

### Node Status
```
🟢 Node  1:  98.50 credits | Reputation:  95.0%
🟢 Node  2: 102.30 credits | Reputation:  98.2%
🟡 Node  3:  89.20 credits | Reputation:  67.5%  ← Under suspicion
🔴 Node  4:  76.10 credits | Reputation:  42.1%  ← Malicious detected
...
```

## Demo Flow (7 Stages)

1. **STEP 1**: Network Initialization
   - Shows random topology generation
   - Displays connections and initial economy

2. **DEMO 1**: Normal Logistics Message
   - Encrypted message costs 2 credits
   - Shows relay rewards in action

3. **DEMO 2**: Help Message
   - Public signed emergency alert
   - Demonstrates ECDSA signature

4. **DEMO 3**: Selfish Node Attack
   - Node refuses to relay
   - Shows detection and impact

5. **DEMO 4**: Hash Manipulation
   - Node changes its hash
   - Shows easy detection

6. **DEMO 5**: Message Tampering
   - Attacker modifies message content
   - Signature verification catches it

7. **DEMO 6**: Anonymous Safe Message
   - Zero-Knowledge Proof demo
   - Shows free emergency messaging

8. **FINAL**: Summary & Takeaways
   - Complete network state
   - Key features recap

## Presentation Tips

### Time Management
- Full demo: ~5-7 minutes (with explanations)
- Can skip stages if time is tight
- Each stage is self-contained

### What to Emphasize
1. **Cryptographic diversity** - Different message types use different crypto
2. **Economic incentives** - Rewards for good behavior
3. **Attack detection** - System catches malicious actors
4. **Real-world ready** - Campus-scale, LoRa-compatible

### Common Questions Ready
- **Q: How does ZKP work?** A: Proves membership without revealing identity
- **Q: Why economic incentives?** A: Encourages participation in disaster scenarios
- **Q: Can it scale?** A: Yes, gossip protocol is designed for distributed scale
- **Q: What about battery life?** A: LoRa network type uses minimal power

## Troubleshooting

### Backend Not Running
```
❌ Error: Backend not running!
   Please start the backend with: uvicorn main:app --reload --port 8000
```
→ Start the backend first (see Prerequisites)

### Port Already in Use
→ Make sure no other process is using port 8000

### Virtual Environment Issues
→ Make sure you activated crypto-env before running

## Customization

### Change Number of Demos
Edit `main()` function - comment out stages you don't need

### Change Node Count
Modify `NUM_NODES = 10` at the top of the file

### Adjust Network Density
Edit connection generation logic in `setup_network_with_connections()`

### Add New Demos
Follow the pattern of existing `demo_*()` functions

## Output Example

```
======================================================================
  STEP 1: Network Initialization
======================================================================

Generating random network topology on URI campus...
✓ Created 18 connections
✓ All nodes have minimum 2 connections

--- Network Topology ---
  Node  1 [Alpha]      | Relay:✓ | Hash:0x3a9f2b... | Connected to: [2, 5, 7]
  Node  2 [Bravo]      | Relay:✓ | Hash:0x7c4e1d... | Connected to: [1, 3, 6]
  ...

--- Economy Statistics ---
  Total Supply:        1000.00 credits
  Total In Circulation: 1000.00 credits
  Gini Coefficient:    0.0000 (0=equal, 1=unequal)
  Nakamoto Coefficient: 5 nodes control 51% wealth
  Total Transactions:  0

--- Node Status ---
  🟢 Node  1: 100.00 credits | Reputation: 100.0%
  🟢 Node  2: 100.00 credits | Reputation: 100.0%
  ...

⏸️  Press ENTER to continue...
```

## Advantages Over Web UI Demo

| Feature | Web UI | Terminal Demo |
|---------|--------|---------------|
| Setup time | Manual clicking | Automated |
| Narrative flow | Manual | Sequential & clear |
| Attack demos | Hard to coordinate | One keystroke each |
| Professional look | Depends on presenter | Consistent output |
| Reproducibility | Manual steps vary | Same every time |
| Screen sharing | Need to show mouse | Just show terminal |

## Perfect For
- ✅ Class presentations
- ✅ Technical demos
- ✅ Quick showcases
- ✅ Recorded demos
- ✅ Conference presentations
- ✅ Investor pitches

---

**Ready to present!** Just run the script and press ENTER to advance through each stage. 🎬
