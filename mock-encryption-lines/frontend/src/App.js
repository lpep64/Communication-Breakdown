import React, { useState, useEffect, useRef } from 'react';
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
  const [targetNodes, setTargetNodes] = useState([]);
  const [loading, setLoading] = useState(false);
  // connection states for demo
  // connections are undirected pairs stored as { a, b } with a < b
  const [connections, setConnections] = useState([]); // { a, b }
  const [isConnectMode, setIsConnectMode] = useState(false);
  const [drawingConnection, setDrawingConnection] = useState(null); // { fromId, toLatLng }
  const mapRef = useRef(null);

  useEffect(() => {
    fetchNodes();
    // fetch backend-stored connections on load
    fetchBackendConnections();
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

  const onMapMouseMove = (e) => {
    if (!drawingConnection) return;
    setDrawingConnection(prev => prev ? { ...prev, toLatLng: [e.latlng.lat, e.latlng.lng] } : prev);
  };

  const cleanupDrawing = () => {
    if (mapRef.current) {
      try { mapRef.current.off('mousemove', onMapMouseMove); } catch (e) {}
    }
    setDrawingConnection(null);
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

  const fetchNodeInventory = async (nodeId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/node/${nodeId}/inventory`);
      setNodePackets(response.data.packets);
    } catch (error) {
      console.error('Error fetching node inventory:', error);
    }
  };


  const handleNodeClick = (node) => {
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
        target_node_ids: targetNodes
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

  const availableTargets = nodes.filter(node => node.node_id !== selectedNode?.node_id);

  return (
    <div className="app">
      <div className="map-container">
        <div className="map-controls">
          <label>
            <input
              type="checkbox"
              checked={isConnectMode}
              onChange={(e) => setIsConnectMode(e.target.checked)}
            />
            Connect Mode (drag from one node to another)
          </label>
          <button style={{ marginLeft: 8 }} onClick={() => setConnections([])}>Clear Connections</button>
        </div>
        <MapContainer
          whenCreated={(map) => { mapRef.current = map; map.on('mouseup', cleanupDrawing); }}
          center={[41.58, -71.45]} // Center of Rhode Island
          zoom={10}
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
                eventHandlers={{
                  click: () => handleNodeClick(node),
                  mousedown: (e) => {
                    if (!isConnectMode) return;
                    setDrawingConnection({ fromId: node.node_id, toLatLng: [e.latlng.lat, e.latlng.lng] });
                    if (mapRef.current) mapRef.current.on('mousemove', onMapMouseMove);
                  },
                  mouseup: (e) => {
                    if (!isConnectMode || !drawingConnection) return;
                    const toId = node.node_id;
                    const fromId = drawingConnection.fromId;
                    if (fromId && toId && fromId !== toId) {
                      const a = Math.min(fromId, toId);
                      const b = Math.max(fromId, toId);
                      const exists = connections.some(c => c.a === a && c.b === b);
                      if (!exists) {
                        // optimistically update UI
                        setConnections(prev => [...prev, { a, b }]);
                        // persist to backend
                        axios.post(`${API_BASE_URL}/connections`, { node_a: a, node_b: b }).catch(err => {
                          console.warn('Failed to persist connection to backend:', err.message || err);
                        });
                      }
                    }
                    cleanupDrawing();
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
          {/* temporary drawing */}
          {drawingConnection && (() => {
            const fromNode = nodes.find(n => n.node_id === drawingConnection.fromId);
            if (!fromNode) return null;
            return <Polyline positions={[[fromNode.lat, fromNode.lng], drawingConnection.toLatLng]} pathOptions={{ color: '#888', dashArray: '4', weight: 2 }} />;
          })()}
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
            <div className="connection-control-section">
              <h3>Connections (demo)</h3>
              <div className="connection-controls">
                <small>Connect Mode is {isConnectMode ? 'ON' : 'OFF'}. Drag from one node to another on the map to create a connection.</small>
                <div style={{ marginTop: 8 }}>
                  <button onClick={() => setConnections([])}>Clear All Connections</button>
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
              <textarea
                className="message-input"
                placeholder="Enter your message..."
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
              />
              
              <div className="target-selection">
                <h4>Select Target Nodes:</h4>
                <div className="target-checkboxes">
                  {availableTargets.map((node) => (
                    <label key={node.node_id} className="target-checkbox">
                      <input
                        type="checkbox"
                        checked={targetNodes.includes(node.node_id)}
                        onChange={() => handleTargetToggle(node.node_id)}
                      />
                      {node.name}
                    </label>
                  ))}
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
    </div>
  );
}

export default App;