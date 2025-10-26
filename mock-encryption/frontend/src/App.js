import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Circle } from 'react-leaflet';
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
  const [nodeNetwork, setNodeNetwork] = useState(null);
  const [messageText, setMessageText] = useState('');
  const [targetNodes, setTargetNodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showRanges, setShowRanges] = useState(true);

  useEffect(() => {
    fetchNodes();
  }, []);

  useEffect(() => {
    if (selectedNode) {
      fetchNodeInventory(selectedNode.node_id);
      fetchNodeNetwork(selectedNode.node_id);
      // Auto-refresh inventory and network every 3 seconds while a node is selected
      const interval = setInterval(() => {
        fetchNodeInventory(selectedNode.node_id);
        fetchNodeNetwork(selectedNode.node_id);
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

  const fetchNodeInventory = async (nodeId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/node/${nodeId}/inventory`);
      setNodePackets(response.data.packets);
    } catch (error) {
      console.error('Error fetching node inventory:', error);
    }
  };

  const fetchNodeNetwork = async (nodeId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/node/${nodeId}/network`);
      setNodeNetwork(response.data);
    } catch (error) {
      console.error('Error fetching node network:', error);
    }
  };

  const updateNodeRange = async (nodeId, newRange) => {
    try {
      await axios.put(`${API_BASE_URL}/node/${nodeId}/range?new_range=${newRange}`);
      // Update the local nodes state
      setNodes(prevNodes => 
        prevNodes.map(node => 
          node.node_id === nodeId 
            ? { ...node, range: newRange }
            : node
        )
      );
      // Update selected node if it's the one being modified
      if (selectedNode && selectedNode.node_id === nodeId) {
        setSelectedNode(prev => ({ ...prev, range: newRange }));
        // Refresh network info when range changes
        fetchNodeNetwork(nodeId);
      }
    } catch (error) {
      console.error('Error updating node range:', error);
      alert('Error updating node range. Please try again.');
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
              checked={showRanges}
              onChange={(e) => setShowRanges(e.target.checked)}
            />
            Show Node Ranges
          </label>
        </div>
        <MapContainer 
          center={[41.58, -71.45]} // Center of Rhode Island
          zoom={10} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {nodes.map((node) => (
            <React.Fragment key={node.node_id}>
              <Marker 
                position={[node.lat, node.lng]}
                icon={selectedNode?.node_id === node.node_id ? selectedIcon : defaultIcon}
                eventHandlers={{
                  click: () => handleNodeClick(node),
                }}
              />
              {showRanges && (
                <Circle
                  center={[node.lat, node.lng]}
                  radius={node.range * 1000} // Convert km to meters
                  pathOptions={{
                    color: selectedNode?.node_id === node.node_id ? '#ff0000' : '#3388ff',
                    fillColor: selectedNode?.node_id === node.node_id ? '#ff0000' : '#3388ff',
                    fillOpacity: 0.1,
                    weight: 2
                  }}
                />
              )}
            </React.Fragment>
          ))}
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
            <div className="range-control-section">
              <h3>Broadcast Range Control</h3>
              <div className="range-slider-container">
                <label htmlFor="range-slider">
                  Broadcast Range: {selectedNode.range}km
                </label>
                <input
                  id="range-slider"
                  type="range"
                  min="1"
                  max="50"
                  value={selectedNode.range}
                  onChange={(e) => updateNodeRange(selectedNode.node_id, parseInt(e.target.value))}
                  className="range-slider"
                />
                <div className="range-labels">
                  <span>1km</span>
                  <span>50km</span>
                </div>
              </div>
            </div>

            <div className="network-section">
              <h3>Current Network</h3>
              {nodeNetwork ? (
                <div className="network-info">
                  <div className="node-coordinates">
                    <small>Node Location: {nodeNetwork.node_coordinates.lat.toFixed(4)}°N, {Math.abs(nodeNetwork.node_coordinates.lng).toFixed(4)}°W</small>
                  </div>
                  
                  <div className="network-subsection">
                    <h4>Nodes I Can Reach ({nodeNetwork.total_reachable})</h4>
                    {nodeNetwork.nodes_in_my_range.length === 0 ? (
                      <p className="no-connections">No nodes within broadcast range</p>
                    ) : (
                      <div className="node-list">
                        {nodeNetwork.nodes_in_my_range.map(node => (
                          <div key={node.node_id} className="network-node">
                            <div className="node-info">
                              <span className="node-name">{node.name}</span>
                              <small className="node-coords">
                                {node.coordinates.lat.toFixed(4)}°N, {Math.abs(node.coordinates.lng).toFixed(4)}°W
                              </small>
                            </div>
                            <span className="node-distance">{node.distance_km}km</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="network-subsection">
                    <h4>Nodes That Can Reach Me ({nodeNetwork.total_can_reach_me})</h4>
                    {nodeNetwork.nodes_that_can_reach_me.length === 0 ? (
                      <p className="no-connections">No nodes can reach me</p>
                    ) : (
                      <div className="node-list">
                        {nodeNetwork.nodes_that_can_reach_me.map(node => (
                          <div key={node.node_id} className="network-node">
                            <div className="node-info">
                              <span className="node-name">{node.name}</span>
                              <small className="node-coords">
                                {node.coordinates.lat.toFixed(4)}°N, {Math.abs(node.coordinates.lng).toFixed(4)}°W
                              </small>
                            </div>
                            <span className="node-distance">{node.distance_km}km (range: {node.range_km}km)</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <p>Loading network information...</p>
              )}
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