import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';
import './index.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;

// Create custom icons for selected and unselected states
const defaultIcon = new L.Icon({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Use a green marker for selected state
const selectedIcon = new L.Icon({
  iconRetinaUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [30, 48], // Slightly larger for selected state
  iconAnchor: [15, 48],
  popupAnchor: [1, -34],
  shadowSize: [48, 48]
});

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [nodePackets, setNodePackets] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [messageType, setMessageType] = useState('Logistics'); // "Logistics", "Help", "Safe"
  const [targetNodes, setTargetNodes] = useState([]);
  const [loading, setLoading] = useState(false);
  // connection states for demo
  // connections are undirected pairs stored as { a, b } with a < b
  const [connections, setConnections] = useState([]); // { a, b }
  const [economyStats, setEconomyStats] = useState(null);
  const [showEconomyPanel, setShowEconomyPanel] = useState(false);
  
  // URI Kingston Campus center coordinates
  const uriCenter = [41.4852, -71.5268]; // URI Kingston Campus center

  useEffect(() => {
    fetchNodes();
    // fetch backend-stored connections on load
    fetchBackendConnections();
    fetchEconomyStats();
    
    // Poll economy stats every 5 seconds
    const economyInterval = setInterval(() => {
      fetchEconomyStats();
    }, 5000);
    
    // Add escape key handler
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setSelectedNode(null);
      }
    };
    document.addEventListener('keydown', handleEscape);
    
    return () => {
      clearInterval(economyInterval);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  const fetchBackendConnections = async () => {
    try {
      const resp = await axios.get(`${API_BASE_URL}/connections`);
      // resp is [{a,b}, ...]
      setConnections(resp.data.map(c => ({ a: c.a, b: c.b })));
    } catch (err) {
      console.warn('Unable to fetch backend connections:', err.message || err);
    }
  };

  const fetchEconomyStats = async () => {
    try {
      const resp = await axios.get(`${API_BASE_URL}/stats/economy`);
      setEconomyStats(resp.data);
    } catch (err) {
      console.warn('Unable to fetch economy stats:', err.message || err);
    }
  };

  useEffect(() => {
    if (selectedNode) {
      fetchNodeInventory(selectedNode.node_id);
      // Auto-refresh inventory every 3 seconds while a node is selected
      const interval = setInterval(() => {
        fetchNodeInventory(selectedNode.node_id);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [selectedNode]);

  const fetchNodes = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/nodes`);
      setNodes(response.data); // API now returns array directly
    } catch (error) {
      console.error('Error fetching nodes:', error);
    }
  };

  // remove a connection (undirected) and notify backend
  const removeConnection = async (id1, id2) => {
    const a = Math.min(id1, id2);
    const b = Math.max(id1, id2);
    try {
      await axios.delete(`${API_BASE_URL}/connections`, { data: { node_a: a, node_b: b } });
    } catch (err) {
      console.warn('Failed to remove backend connection:', err.message || err);
    }
    setConnections(prev => prev.filter(c => !(c.a === a && c.b === b)));
  };

  // clear all connections for a specific node
  const clearNodeConnections = async (nodeId) => {
    const nodeConnections = connections.filter(c => c.a === nodeId || c.b === nodeId);
    
    // Remove each connection from backend
    for (const conn of nodeConnections) {
      try {
        await axios.delete(`${API_BASE_URL}/connections`, { data: { node_a: conn.a, node_b: conn.b } });
      } catch (err) {
        console.warn('Failed to remove backend connection:', err.message || err);
      }
    }
    
    // Update local state - remove all connections involving this node
    setConnections(prev => prev.filter(c => c.a !== nodeId && c.b !== nodeId));
  };

  const fetchNodeInventory = async (nodeId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/node/${nodeId}/inventory`);
      setNodePackets(response.data.packets);
    } catch (error) {
      console.error('Error fetching node inventory:', error);
    }
  };


  const handleNodeClick = (node, shiftKey = false) => {
    // Shift+click to create/remove connection
    if (shiftKey && selectedNode && selectedNode.node_id !== node.node_id) {
      const a = Math.min(selectedNode.node_id, node.node_id);
      const b = Math.max(selectedNode.node_id, node.node_id);
      const exists = connections.some(c => c.a === a && c.b === b);
      
      if (exists) {
        // Remove connection
        removeConnection(a, b);
      } else {
        // Add connection
        setConnections(prev => [...prev, { a, b }]);
        // persist to backend
        axios.post(`${API_BASE_URL}/connections`, { node_a: a, node_b: b }).catch(err => {
          console.warn('Failed to persist connection to backend:', err.message || err);
        });
      }
      // Select the shift-clicked node
      setSelectedNode(node);
      setMessageText('');
      setTargetNodes([]);
      return;
    }
    
    // Normal click - select node
    setSelectedNode(node);
    setMessageText('');
    setTargetNodes([]);
  };

  const handleTargetToggle = (nodeId) => {
    setTargetNodes(prev => 
      prev.includes(nodeId) 
        ? prev.filter(id => id !== nodeId)
        : [...prev, nodeId]
    );
  };

  const handleHashUpdate = async (nodeId, newHash) => {
    try {
      await axios.put(`${API_BASE_URL}/node/${nodeId}/hash`, { hash_value: newHash }, {
        headers: { 'Content-Type': 'application/json' }
      });
      // Update local state
      setNodes(prev => prev.map(n => 
        n.node_id === nodeId ? { ...n, hash: newHash } : n
      ));
      if (selectedNode?.node_id === nodeId) {
        setSelectedNode(prev => ({ ...prev, hash: newHash }));
      }
    } catch (error) {
      console.error('Error updating hash:', error);
    }
  };

  const handleAutoRelayToggle = async (nodeId, autoRelay) => {
    try {
      await axios.put(`${API_BASE_URL}/node/${nodeId}/auto_relay`, { auto_relay: autoRelay });
      // Update local state
      setNodes(prev => prev.map(n => 
        n.node_id === nodeId ? { ...n, auto_relay: autoRelay } : n
      ));
      if (selectedNode?.node_id === nodeId) {
        setSelectedNode(prev => ({ ...prev, auto_relay: autoRelay }));
      }
    } catch (error) {
      console.error('Error toggling auto-relay:', error);
    }
  };

  const handleTamperMessage = async (packetId) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/attack/tamper_packet/${packetId}`);
      console.log('Message tampered:', response.data);
      alert(`Message tampered! Original: "${response.data.original_text}" → Tampered: "${response.data.tampered_text}"\n\n${response.data.note}`);
      // Refresh inventory to show tampered message
      if (selectedNode) {
        const inventoryRes = await axios.get(`${API_BASE_URL}/node/${selectedNode.node_id}/inventory`);
        setNodePackets(inventoryRes.data.packets);
      }
    } catch (error) {
      console.error('Error updating auto-relay:', error);
    }
  };

  const handleNodeDragEnd = async (node, newLatLng) => {
    try {
      await axios.put(`${API_BASE_URL}/node/${node.node_id}/position`, {
        latitude: newLatLng.lat,
        longitude: newLatLng.lng
      });
      // Refresh nodes to get updated position
      await fetchNodes();
    } catch (error) {
      console.error('Error updating node position:', error);
      alert('Error updating node position. Please try again.');
    }
  };

  const handlePublishMessage = async () => {
    if (!messageText.trim() || targetNodes.length === 0) {
      alert('Please enter a message and select at least one target node.');
      return;
    }

    setLoading(true);
    
    try {
      await axios.post(`${API_BASE_URL}/publish_message`, {
        publisher_node_id: selectedNode.node_id,
        message_text: messageText.trim(),
        target_node_ids: targetNodes,
        message_type: messageType
      });

      // Refresh inventory for the current node
      await fetchNodeInventory(selectedNode.node_id);
      
      // Clear form
      setMessageText('');
      setTargetNodes([]);
      
    } catch (error) {
      console.error('Error publishing message:', error);
      alert('Error publishing message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClearMessages = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/messages/clear`);
      setNodePackets([]);
      alert('All messages cleared successfully!');
    } catch (error) {
      console.error('Error clearing messages:', error);
      alert('Error clearing messages. Please try again.');
    }
  };

  const getPacketClass = (packet) => {
    if (packet.publisher_id === selectedNode.node_id) {
      return 'sent';
    }
    return packet.can_decrypt ? 'decrypted' : 'encrypted';
  };

  // Include all nodes (including self) for consistency
  const availableTargets = nodes;

  return (
    <div className="app">
      <div className="map-container">
        <div className="map-controls">
          <div style={{ color: '#666', fontSize: '14px' }}>
            <strong>Controls:</strong> Click to select | Shift+Click to connect/disconnect | Escape to deselect | Drag to move
          </div>
          <button style={{ marginLeft: 16 }} onClick={() => setShowEconomyPanel(!showEconomyPanel)}>
            {showEconomyPanel ? 'Hide' : 'Show'} Economy Stats
          </button>
          <button style={{ marginLeft: 8 }} onClick={() => setConnections([])}>Clear Connections</button>
        </div>
        <MapContainer
          center={uriCenter}
          zoom={16}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {nodes.map((node) => {
            const isSelected = selectedNode?.node_id === node.node_id;
            
            return (
              <Marker
                key={node.node_id}
                position={[node.lat, node.lng]}
                icon={isSelected ? selectedIcon : defaultIcon}
                draggable={true}
                eventHandlers={{
                  click: (e) => handleNodeClick(node, e.originalEvent.shiftKey),
                  dragend: (e) => {
                    const newLatLng = e.target.getLatLng();
                    handleNodeDragEnd(node, newLatLng);
                  }
                }}
              />
            );
          })}
          {/* render connections */}
          {connections.map((c, idx) => {
            const from = nodes.find(n => n.node_id === c.a);
            const to = nodes.find(n => n.node_id === c.b);
            if (!from || !to) return null;
            // highlight if selected node participates in this connection
            const isEndpoint = selectedNode && (selectedNode.node_id === c.a || selectedNode.node_id === c.b);
            const color = isEndpoint ? '#00aa00' : '#4466ff';
            return <Polyline key={`${c.a}-${c.b}-${idx}`} positions={[[from.lat, from.lng], [to.lat, to.lng]]} pathOptions={{ color, weight: isEndpoint ? 4 : 3 }} />;
          })}
        </MapContainer>
      </div>

      {selectedNode && (
        <div className="inventory-panel">
          <div className="inventory-header">
            <h2>{selectedNode.name} Inventory</h2>
            <small>Location: {selectedNode.lat.toFixed(4)}°N, {Math.abs(selectedNode.lng).toFixed(4)}°W</small>
            <button 
              className="close-button"
              onClick={() => setSelectedNode(null)}
            >
              ×
            </button>
          </div>

          <div className="inventory-content">
            <div className="node-settings-section">
              <h3>Node Settings</h3>
              <div className="setting-item">
                <label>
                  Hash:
                  <input
                    type="text"
                    value={selectedNode.hash || ''}
                    onChange={(e) => handleHashUpdate(selectedNode.node_id, e.target.value)}
                    style={{ marginLeft: 8, width: 150 }}
                  />
                </label>
              </div>
              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={selectedNode.auto_relay !== false}
                    onChange={(e) => handleAutoRelayToggle(selectedNode.node_id, e.target.checked)}
                  />
                  Auto-relay messages (uncheck to simulate selfish node attack)
                </label>
              </div>
            </div>

            <div className="connection-control-section">
              <h3>Connections</h3>
              <div className="connection-controls">
                <small>Hold <strong>Shift</strong> and click another node to connect/disconnect. Press <strong>Escape</strong> to deselect.</small>
                <div style={{ marginTop: 8 }}>
                  <button onClick={() => clearNodeConnections(selectedNode.node_id)}>Clear This Node's Connections</button>
                </div>
              </div>

              <div className="network-subsection">
                <h4>Connected Nodes ({connections.filter(c => c.a === selectedNode.node_id || c.b === selectedNode.node_id).length})</h4>
                {connections.filter(c => c.a === selectedNode.node_id || c.b === selectedNode.node_id).length === 0 ? (
                  <p className="no-connections">No connected nodes</p>
                ) : (
                  <div className="node-list">
                    {connections.filter(c => c.a === selectedNode.node_id || c.b === selectedNode.node_id).map(c => {
                      const otherId = c.a === selectedNode.node_id ? c.b : c.a;
                      const node = nodes.find(n => n.node_id === otherId);
                      if (!node) return null;
                      return (
                        <div key={`conn-${c.a}-${c.b}`} className="network-node">
                          <div className="node-info">
                            <span className="node-name">{node.name}</span>
                            <small className="node-coords">{node.lat.toFixed(4)}°N, {Math.abs(node.lng).toFixed(4)}°W</small>
                          </div>
                          <div style={{ display: 'flex', gap: 8 }}>
                            <button onClick={() => removeConnection(selectedNode.node_id, otherId)}>Remove</button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            <div className="messages-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3>Message Packets ({nodePackets.length})</h3>
                <button 
                  className="clear-messages-button"
                  onClick={handleClearMessages}
                >
                  Clear All Messages
                </button>
              </div>
              
              {nodePackets.length === 0 ? (
                <p>No message packets received yet.</p>
              ) : (
                nodePackets.slice().reverse().map((packet) => (
                  <div key={packet.packet_id} className="message-item">
                    <div className="message-header">
                      <span>From: Node {packet.publisher_id}</span>
                      <span>Path: {packet.path_string}</span>
                      <button 
                        className="tamper-button"
                        onClick={() => handleTamperMessage(packet.packet_id)}
                        title="Tamper with this message to break hash integrity"
                      >
                        🔨 Tamper
                      </button>
                    </div>
                    <div className={`message-content ${getPacketClass(packet)}`}>
                      {packet.content}
                    </div>
                    {packet.can_decrypt && (
                      <div className="message-meta">
                        <small>✓ You can decrypt this message</small>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="publish-section">
              <h3>Publish New Message</h3>
              
              <div className="message-type-selection">
                <label>Message Type:</label>
                <select 
                  value={messageType} 
                  onChange={(e) => setMessageType(e.target.value)}
                  className="message-type-select"
                >
                  <option value="Logistics">Logistics (Encrypted, 2 credits)</option>
                  <option value="Help">Help (Signed, 2 credits)</option>
                  <option value="Safe">Safe (Anonymous ZKP, Free)</option>
                </select>
              </div>
              
              <textarea
                className="message-input"
                placeholder="Enter your message..."
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
              />
              
              <div className="target-selection">
                <h4>Select Target Nodes:</h4>
                <div className="target-checkboxes">
                  {availableTargets.map((node) => {
                    const isSelf = node.node_id === selectedNode.node_id;
                    return (
                      <label 
                        key={node.node_id} 
                        className="target-checkbox"
                        style={{ opacity: isSelf ? 0.5 : 1, cursor: isSelf ? 'not-allowed' : 'pointer' }}
                      >
                        <input
                          type="checkbox"
                          checked={targetNodes.includes(node.node_id)}
                          onChange={() => handleTargetToggle(node.node_id)}
                          disabled={isSelf}
                        />
                        {node.name} {isSelf && '(self)'}
                      </label>
                    );
                  })}
                </div>
              </div>

              <button 
                className="publish-button"
                onClick={handlePublishMessage}
                disabled={loading || !messageText.trim() || targetNodes.length === 0}
              >
                {loading ? 'Publishing...' : 'Publish Message'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showEconomyPanel && economyStats && (
        <div className="economy-panel">
          <div className="economy-header">
            <h2>Economy Statistics</h2>
            <button 
              className="close-button"
              onClick={() => setShowEconomyPanel(false)}
            >
              ×
            </button>
          </div>
          
          <div className="economy-content">
            <div className="economy-metrics">
              <div className="metric-card">
                <h4>Gini Coefficient</h4>
                <div className="metric-value">{economyStats.gini_coefficient?.toFixed(4) || 'N/A'}</div>
                <small>Wealth inequality (0=perfect equality, 1=total inequality)</small>
              </div>
              
              <div className="metric-card">
                <h4>Nakamoto Coefficient</h4>
                <div className="metric-value">{economyStats.nakamoto_coefficient || 'N/A'}</div>
                <small>Nodes needed to control 51% of credits</small>
              </div>
              
              <div className="metric-card">
                <h4>Total Credits</h4>
                <div className="metric-value">{economyStats.total_credits?.toFixed(0) || 'N/A'}</div>
                <small>Economy health: {economyStats.economy_health || 'Unknown'}</small>
              </div>
              
              <div className="metric-card">
                <h4>Tick Count</h4>
                <div className="metric-value">{economyStats.tick_count || 0}</div>
                <small>Simulation cycles elapsed</small>
              </div>
            </div>
            
            <div className="node-balances">
              <h3>Node Balances</h3>
              <div className="balance-list">
                {economyStats.node_balances?.map((item) => (
                  <div key={item.node_id} className="balance-item">
                    <span className="node-name">Node {item.node_id}</span>
                    <span className="balance-value">{item.balance} credits</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;