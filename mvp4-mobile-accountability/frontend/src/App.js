import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

const API_BASE = 'http://localhost:8000';

// ============================================================================
// CUSTOM MAP MARKERS
// ============================================================================

const createCustomIcon = (responseType, status) => {
  const colors = {
    grey: '#9ca3af',
    yellow: '#f59e0b',
    green: '#10b981',
    red: '#ef4444'
  };

  const color = colors[responseType] || '#9ca3af';
  const shouldPulse = responseType === 'red' || status === 'In Danger' || status === 'Needs Help';

  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background-color: ${color};
      border: 3px solid white;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
      ${shouldPulse ? 'animation: pulse 2s infinite;' : ''}
    "></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -10]
  });
};

// ============================================================================
// NOTIFICATION TOAST COMPONENT
// ============================================================================

const NotificationToast = ({ notification, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(notification.id);
    }, 2000); // Changed to 2 seconds

    return () => clearTimeout(timer);
  }, [notification.id, onClose]);

  const statusClass = notification.status === 'Needs Help' ? 'help' : 
                      notification.status === 'Unresponsive' ? 'unresponsive' : 'safe';

  return (
    <div className={`notification-toast ${statusClass}`}>
      <div className="notification-header">
        <div className="notification-title">
          {notification.status === 'Needs Help' ? '🚨 Help Requested' : 
           notification.status === 'Unresponsive' ? '⚠️ Employee Unresponsive' :
           '✅ Status Update'}
        </div>
        <button className="notification-close" onClick={() => onClose(notification.id)}>
          ×
        </button>
      </div>
      <div className="notification-message">{notification.message}</div>
      <div className="notification-time">{getRelativeTime(notification.timestamp)}</div>
    </div>
  );
};

// ============================================================================
// NOTIFICATION PANEL COMPONENT
// ============================================================================

const NotificationPanel = ({ notifications, onClose }) => {
  return (
    <div className="notification-panel">
      {notifications.map((notif) => (
        <NotificationToast key={notif.id} notification={notif} onClose={onClose} />
      ))}
    </div>
  );
};

// ============================================================================
// EMPLOYEE PORTAL COMPONENT
// ============================================================================

const EmployeePortal = ({ employeeId }) => {
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [locationHidden, setLocationHidden] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);

  useEffect(() => {
    fetchEmployee();
    const interval = setInterval(fetchEmployee, 5000);
    return () => clearInterval(interval);
  }, [employeeId]);

  const fetchEmployee = async () => {
    try {
      const response = await axios.get(`${API_BASE}/employee/${employeeId}`);
      setEmployee(response.data);
      setLocationHidden(response.data.location_hidden);
      
      // Calculate remaining time if request is pending
      if (response.data.request_pending && response.data.request_sent_time) {
        const sentTime = new Date(response.data.request_sent_time);
        const now = new Date();
        const elapsedSeconds = Math.floor((now - sentTime) / 1000);
        const remaining = Math.max(0, 60 - elapsedSeconds); // 60 seconds = 1 minute
        setTimerSeconds(remaining);
      } else {
        setTimerSeconds(0);
      }
      
      setLoading(false);
      setError(null);
    } catch (err) {
      setError('Failed to load employee data');
      setLoading(false);
    }
  };

  useEffect(() => {
    if (timerSeconds > 0) {
      const timer = setInterval(() => {
        setTimerSeconds(prev => {
          if (prev <= 1) {
            // Timer expired - will be handled by backend on next poll
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [timerSeconds]);

  const toggleLocationPrivacy = async () => {
    try {
      await axios.put(`${API_BASE}/employee/${employeeId}/location_privacy`, null, {
        params: { hidden: !locationHidden }
      });
      setLocationHidden(!locationHidden);
    } catch (err) {
      setError('Failed to update location privacy');
    }
  };

  const updateStatus = async (status) => {
    setUpdating(true);
    try {
      await axios.post(`${API_BASE}/employee/${employeeId}/status`, {
        status: status
      });
      await fetchEmployee();
    } catch (err) {
      setError('Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!employee) {
    return <div className="error-message">Employee not found</div>;
  }

  const statusClass = employee.status === 'Safe' ? 'safe' : 
                      employee.status === 'Needs Help' ? 'help' : 'unknown';

  const formatTimer = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="employee-portal">
      <div className={`employee-card ${employee.request_pending ? 'request-pending' : ''}`}>
        {employee.request_pending && (
          <>
            <div className="request-indicator">
              ⚠️ Status Update Requested
            </div>
            {timerSeconds > 0 && (
              <div className="employee-timer">
                ⏱️ Time remaining: {formatTimer(timerSeconds)}
              </div>
            )}
          </>
        )}

        <div className="employee-header">
          <h2>{employee.name}</h2>
          <div className="employee-id">Employee ID: {employee.id}</div>
        </div>

        <div className={`status-display ${statusClass}`}>
          {employee.status === 'Safe' && '✅ You are marked as SAFE'}
          {employee.status === 'Needs Help' && '🚨 HELP REQUESTED'}
          {employee.status === 'In Danger' && '🆘 IN DANGER'}
          {employee.status === 'Unknown' && '❓ Status Unknown'}
        </div>

        <div className="action-buttons">
          <button 
            className="btn btn-safe" 
            onClick={() => updateStatus('Safe')}
            disabled={updating}
          >
            ✅ Mark as Safe
          </button>
          <button 
            className="btn btn-help" 
            onClick={() => updateStatus('Needs Help')}
            disabled={updating}
          >
            🚨 Send Help Request
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={() => updateStatus('Unknown')}
            disabled={updating}
          >
            ❓ Clear Status
          </button>
        </div>

        <div className="location-privacy-toggle">
          <div className="privacy-toggle-header">
            <strong style={{ color: '#1f2937' }}>📍 Location Privacy</strong>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={locationHidden}
                onChange={toggleLocationPrivacy}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
          <p className="privacy-description">
            {locationHidden 
              ? '🔒 Your location is hidden from managers' 
              : '🔓 Your location is visible to managers'}
          </p>
        </div>

        <div className="info-section">
          <div className="info-item">
            <span className="info-label">Last Update:</span>
            <span className="info-value">
              {employee.last_update ? getRelativeTime(employee.last_update) : 'Never'}
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Location:</span>
            <span className="info-value">
              {employee.location.lat.toFixed(4)}°N, {Math.abs(employee.location.lon).toFixed(4)}°W
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Signature:</span>
            <span className="info-value">
              {employee.signature ? '🔒 Signed' : '🔓 Not signed'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// ROSTER VIEW COMPONENT
// ============================================================================

const RosterView = ({ employees, selectedEmployees, onToggleEmployee }) => {
  return (
    <div className="roster-grid">
      {employees.map((emp) => {
        // Use response_type for color - yellow/orange for pending requests
        const responseTypeClass = emp.response_type || 'grey';
        const statusClass = responseTypeClass === 'green' ? 'safe' :
                          responseTypeClass === 'red' ? 'help' :
                          responseTypeClass === 'yellow' ? 'pending' :
                          'unknown';
        const isSelected = selectedEmployees.includes(emp.id);
        
        return (
          <div 
            key={emp.id} 
            className={`roster-card ${statusClass}`}
          >
            <input
              type="checkbox"
              className="roster-checkbox"
              checked={isSelected}
              onChange={() => onToggleEmployee(emp.id)}
            />
            <div className="roster-card-content">
              <div className="roster-card-header">
                <div>
                  <div className="roster-name">{emp.name}</div>
                  <div className="roster-id">ID: {emp.id}</div>
                </div>
                <div className={`status-badge ${statusClass}`}>
                  {emp.status === 'Safe' && '✅ Safe'}
                  {emp.status === 'Needs Help' && '🚨 Help'}
                  {emp.status === 'In Danger' && '🆘 Danger'}
                  {emp.status === 'Unknown' && '❓ Unknown'}
                </div>
              </div>
              <div className="roster-timestamp">
                {emp.last_update ? `Updated ${getRelativeTime(emp.last_update)}` : 'No updates yet'}
              </div>
              {emp.last_checkin && (
                <div className="checkin-info">
                  <span className="checkin-label">Last Check-in: </span>
                  <span className="checkin-time">{getRelativeTime(emp.last_checkin)}</span>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ============================================================================
// MAP VIEW COMPONENT
// ============================================================================

const MapView = ({ employees, selectedEmployees, onToggleEmployee }) => {
  // Calculate center point from visible employees
  const visibleEmployees = employees.filter(emp => !emp.location_hidden);
  const centerLat = visibleEmployees.length > 0 
    ? visibleEmployees.reduce((sum, emp) => sum + emp.location.lat, 0) / visibleEmployees.length 
    : 41.4880;
  const centerLon = visibleEmployees.length > 0 
    ? visibleEmployees.reduce((sum, emp) => sum + emp.location.lon, 0) / visibleEmployees.length 
    : -71.5304;

  return (
    <div className="map-container">
      <MapContainer
        center={[centerLat, centerLon]}
        zoom={14}
        style={{ width: '100%', height: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {employees.map((emp) => {
          if (emp.location_hidden) return null; // Don't show hidden locations
          
          const isSelected = selectedEmployees.includes(emp.id);
          
          return (
            <Marker
              key={emp.id}
              position={[emp.location.lat, emp.location.lon]}
              icon={createCustomIcon(emp.response_type || 'grey', emp.status)}
              eventHandlers={{
                click: () => onToggleEmployee(emp.id)
              }}
            >
              <Popup>
                <div style={{ minWidth: '200px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => onToggleEmployee(emp.id)}
                      style={{ width: '18px', height: '18px' }}
                    />
                    <h3 style={{ margin: 0 }}>{emp.name}</h3>
                  </div>
                  <p><strong>Status:</strong> {emp.status}</p>
                  <p><strong>ID:</strong> {emp.id}</p>
                  {emp.last_update && (
                    <p><strong>Updated:</strong> {getRelativeTime(emp.last_update)}</p>
                  )}
                  {emp.last_checkin && (
                    <p><strong>Last Check-in:</strong> {getRelativeTime(emp.last_checkin)}</p>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

// ============================================================================
// MANAGER DASHBOARD COMPONENT
// ============================================================================

const ManagerDashboard = () => {
  const [employees, setEmployees] = useState([]);
  const [roster, setRoster] = useState(null);
  const [view, setView] = useState('roster'); // 'roster' or 'map'
  const [loading, setLoading] = useState(true);
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [requestHistory, setRequestHistory] = useState([]);
  const [expandedRequests, setExpandedRequests] = useState(new Set());
  const [currentTime, setCurrentTime] = useState(Date.now());

  const toggleRequestExpanded = (requestId) => {
    setExpandedRequests(prev => {
      const newSet = new Set(prev);
      if (newSet.has(requestId)) {
        newSet.delete(requestId);
      } else {
        newSet.add(requestId);
      }
      return newSet;
    });
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Auto-expand the most recent request when history updates
  useEffect(() => {
    if (requestHistory.length > 0) {
      const mostRecentId = requestHistory[0].id;
      setExpandedRequests(prev => {
        const newSet = new Set(prev);
        newSet.add(mostRecentId);
        return newSet;
      });
    }
  }, [requestHistory.length]);

  // Update current time every second for live timers
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(Date.now());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Check for expired requests and mark non-responders
  useEffect(() => {
    const checkExpiredRequests = async () => {
      for (const request of requestHistory) {
        const requestTime = new Date(request.timestamp);
        const elapsedSeconds = Math.floor((Date.now() - requestTime) / 1000);
        
        if (elapsedSeconds >= 60) {
          // Check each employee in this request
          for (const [empId, response] of Object.entries(request.responses)) {
            const emp = employees.find(e => e.id === parseInt(empId));
            if (emp && emp.request_pending) {
              try {
                await axios.post(`${API_BASE}/employee/${empId}/timeout`);
              } catch (err) {
                console.error(`Failed to mark employee ${empId} as timeout:`, err);
              }
            }
          }
        }
      }
    };
    
    if (requestHistory.length > 0 && employees.length > 0) {
      checkExpiredRequests();
    }
  }, [currentTime, requestHistory, employees]);

  const fetchData = async () => {
    try {
      const [empResponse, rosterResponse, historyResponse] = await Promise.all([
        axios.get(`${API_BASE}/employees`),
        axios.get(`${API_BASE}/roster`),
        axios.get(`${API_BASE}/request_history`)
      ]);
      setEmployees(empResponse.data);
      setRoster(rosterResponse.data);
      setRequestHistory(historyResponse.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
  };

  const toggleEmployeeSelection = (employeeId) => {
    setSelectedEmployees(prev => 
      prev.includes(employeeId) 
        ? prev.filter(id => id !== employeeId)
        : [...prev, employeeId]
    );
  };

  const selectAll = () => {
    setSelectedEmployees(employees.map(emp => emp.id));
  };

  const clearSelection = () => {
    setSelectedEmployees([]);
  };

  const sendRequestForResponse = async () => {
    if (selectedEmployees.length === 0) return;
    
    try {
      await axios.post(`${API_BASE}/request_response`, selectedEmployees);
      setSelectedEmployees([]); // Clear selection after sending request
      await fetchData(); // Refresh to get new request history
    } catch (err) {
      console.error('Failed to send request:', err);
    }
  };

  const calculateRemainingTime = (timestamp) => {
    const requestTime = new Date(timestamp);
    const elapsedSeconds = Math.floor((Date.now() - requestTime) / 1000);
    const remaining = Math.max(0, 60 - elapsedSeconds);
    return remaining;
  };

  const formatTimer = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="manager-dashboard">
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-label">Total Employees</div>
          <div className="stat-value">{roster?.total_employees || 0}</div>
        </div>
        <div className="stat-card safe">
          <div className="stat-label">✅ Safe</div>
          <div className="stat-value">{roster?.status_counts?.Safe || 0}</div>
        </div>
        <div className="stat-card help">
          <div className="stat-label">🚨 Needs Help</div>
          <div className="stat-value">{roster?.status_counts['Needs Help'] || 0}</div>
        </div>
        <div className="stat-card unknown">
          <div className="stat-label">❓ Unknown</div>
          <div className="stat-value">{roster?.status_counts?.Unknown || 0}</div>
        </div>
      </div>

      <div className="request-response-section">
        <div className="request-response-header">
          <div>
            <h3>Request Status Update</h3>
            <div className="selected-count">
              {selectedEmployees.length} employee{selectedEmployees.length !== 1 ? 's' : ''} selected
            </div>
          </div>
          <div className="request-controls">
            <button className="btn btn-secondary" onClick={selectAll}>
              Select All
            </button>
            <button className="btn btn-secondary" onClick={clearSelection}>
              Clear
            </button>
            <button 
              className="btn btn-safe" 
              onClick={sendRequestForResponse}
              disabled={selectedEmployees.length === 0}
            >
              📢 Request Response
            </button>
          </div>
        </div>

        {/* Request History Table */}
        {requestHistory.length > 0 && (
          <div className="request-history-container">
            {requestHistory.map((request, index) => {
              const isExpanded = expandedRequests.has(request.id);
              const employeeCount = Object.keys(request.responses).length;
              const remainingTime = calculateRemainingTime(request.timestamp);
              const timerDisplay = formatTimer(remainingTime);
              const isExpired = remainingTime === 0;
              return (
                <div key={request.id} className="request-cycle">
                  <div 
                    className="request-cycle-header" 
                    onClick={() => toggleRequestExpanded(request.id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <span className="accordion-icon">{isExpanded ? '▼' : '▶'}</span>
                    Request #{request.id} - {new Date(request.timestamp).toLocaleString()}
                    <span className="employee-count"> ({employeeCount} employees)</span>
                    <span className={`request-timer ${isExpired ? 'expired' : ''}`}>
                      ⏱️ {timerDisplay}
                    </span>
                  </div>
                  {isExpanded && (
                    <table className="response-table">
                      <thead>
                        <tr>
                          <th>Employee ID</th>
                          <th>Employee</th>
                          <th>Status</th>
                          <th>Response Time</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(request.responses).map(([empId, response]) => (
                          <tr key={empId}>
                            <td><strong>#{empId}</strong></td>
                            <td>{response.employee_name}</td>
                            <td>
                              <span className={`response-indicator ${response.response_type}`}></span>
                              {response.status}
                            </td>
                            <td>
                              {response.response_time 
                                ? formatExactTime(response.response_time)
                                : <span style={{ color: '#f59e0b' }}>No response yet</span>}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="dashboard-views">
        <button 
          className={`view-toggle ${view === 'roster' ? 'active' : ''}`}
          onClick={() => setView('roster')}
        >
          📋 Roster View
        </button>
        <button 
          className={`view-toggle ${view === 'map' ? 'active' : ''}`}
          onClick={() => setView('map')}
        >
          🗺️ Map View
        </button>
      </div>

      {view === 'roster' && (
        <RosterView 
          employees={employees} 
          selectedEmployees={selectedEmployees}
          onToggleEmployee={toggleEmployeeSelection}
        />
      )}
      {view === 'map' && (
        <MapView 
          employees={employees}
          selectedEmployees={selectedEmployees}
          onToggleEmployee={toggleEmployeeSelection}
        />
      )}
    </div>
  );
};

// ============================================================================
// MAIN APP COMPONENT
// ============================================================================

function App() {
  const [currentView, setCurrentView] = useState('manager'); // 'manager' or 'employee'
  const [employeeId, setEmployeeId] = useState(1);
  const [employees, setEmployees] = useState([]);

  // Fetch employee data for dropdown
  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const response = await axios.get(`${API_BASE}/employees`);
        setEmployees(response.data);
      } catch (err) {
        console.error('Failed to fetch employees:', err);
      }
    };
    
    fetchEmployees();
    const interval = setInterval(fetchEmployees, 5000);
    return () => clearInterval(interval);
  }, []);

  const getEmployeeStatusColor = (emp) => {
    if (!emp) return '#6b7280'; // grey default
    
    const responseType = emp.response_type || 'grey';
    if (responseType === 'green') return '#10b981'; // green
    if (responseType === 'red') return '#ef4444'; // red
    if (responseType === 'yellow') return '#f59e0b'; // yellow/orange
    return '#9ca3af'; // grey
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>⚡ Rapid Response</h1>
          <div className="nav-links">
            <select
              className="nav-link employee-dropdown"
              style={{ cursor: 'pointer' }}
              value={currentView === 'manager' ? 'manager' : employeeId}
              onChange={(e) => {
                const value = e.target.value;
                if (value === 'manager') {
                  setCurrentView('manager');
                } else {
                  setEmployeeId(parseInt(value));
                  setCurrentView('employee');
                }
              }}
            >
              <option value="manager">Manager Dashboard</option>
              {employees.map(emp => (
                <option 
                  key={emp.id} 
                  value={emp.id}
                  style={{ color: getEmployeeStatusColor(emp) }}
                >
                  Employee {emp.id}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <main className="main-content">
        {currentView === 'manager' && <ManagerDashboard />}
        {currentView === 'employee' && <EmployeePortal employeeId={employeeId} />}
      </main>
    </div>
  );
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function getRelativeTime(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}

function formatExactTime(timestamp) {
  const date = new Date(timestamp);
  let hours = date.getHours();
  const minutes = date.getMinutes();
  const seconds = date.getSeconds();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  
  hours = hours % 12;
  hours = hours ? hours : 12; // 0 becomes 12
  
  const minutesStr = minutes < 10 ? '0' + minutes : minutes;
  const secondsStr = seconds < 10 ? '0' + seconds : seconds;
  
  return `${hours}:${minutesStr}:${secondsStr} ${ampm}`;
}

export default App;
