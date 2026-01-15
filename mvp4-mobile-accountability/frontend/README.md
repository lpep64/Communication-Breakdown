# Guardian Protocol - Frontend

Mobile-responsive React application for personnel accountability with OpenStreetMap visualization.

## Features

- **Employee Portal**: Self-service status updates (Safe/Help/Unknown)
- **Manager Dashboard**: Real-time roster view with statistics
- **Map Visualization**: OpenStreetMap with color-coded employee markers
- **Notification System**: Toast alerts for status changes
- **Mobile-First Design**: Responsive layout optimized for all devices
- **Real-Time Updates**: Auto-refresh every 5 seconds

## Setup

### 1. Install Dependencies

```powershell
cd frontend
npm install
```

### 2. Start Development Server

```powershell
npm start
```

Application opens at `http://localhost:3000`

## Views

### Manager Dashboard (`/`)
- **Roster View**: Grid of employee cards with status badges
- **Map View**: Interactive OpenStreetMap with markers
- **Statistics**: Live counts of Safe/Help/Unknown employees
- **Auto-refresh**: Polls backend every 5 seconds

### Employee Portal
Select "Employee 1-10" from header dropdown to access:
- Current status display (color-coded)
- Quick action buttons (Mark Safe, Send Help, Clear)
- Last update timestamp
- Location coordinates (hidden from manager in production)
- Signature status indicator

## Components

### App.js
Main application with routing and notification system:
- `<ManagerDashboard />` - Aggregated personnel view
- `<EmployeePortal />` - Individual employee interface
- `<NotificationPanel />` - Toast notification system

### RosterView
Grid layout of employee cards:
- Color-coded left border (green/red/gray)
- Status badge with emoji indicator
- Relative timestamp ("2 minutes ago")
- Click to view details (future enhancement)

### MapView
OpenStreetMap integration with custom markers:
- Green circle = Safe
- Red circle (pulsing) = Needs Help
- Gray circle = Unknown
- Click markers for popup with employee info
- Auto-centers on employee cluster

### NotificationToast
Auto-dismissing alerts (5 second timeout):
- 🚨 Red border for "Needs Help"
- ✅ Green border for "Safe" updates
- Manual dismiss with × button
- Slide-in animation from right

## Styling

### Mobile-First Approach
Base styles target 320px (small phones), then scale up:
- 320px: Single column, stacked buttons
- 768px: Two-column roster, horizontal buttons
- 1024px: Full desktop layout, larger map

### Touch-Friendly
- Minimum 44x44px tap targets
- Large buttons with clear spacing
- Swipe-friendly card layouts
- High contrast text (WCAG AA compliant)

### Status Colors
- **Green** (`#10b981`): Safe
- **Red** (`#ef4444`): Needs Help
- **Gray** (`#9ca3af`): Unknown
- **Blue** (`#2563eb`): Primary actions

## API Integration

Uses `axios` for HTTP requests to `http://localhost:8000`:

```javascript
// Get all employees
GET /employees

// Update employee status
POST /employee/{id}/status
Body: { "status": "Safe" }

// Get roster summary
GET /roster

// Get notifications
GET /notifications?unread_only=true
```

## Configuration

### API Base URL
Edit `API_BASE` constant in `App.js`:
```javascript
const API_BASE = 'http://localhost:8000';
```

### Poll Intervals
- Employee data: 5000ms (5 seconds)
- Notifications: 3000ms (3 seconds)

### Map Settings
- Default center: URI Kingston Campus (41.4880°N, 71.5304°W)
- Default zoom: 14
- Tile provider: OpenStreetMap (free, no API key)

## Development

### Hot Reload
React dev server auto-refreshes on file changes.

### Browser Console
Check for API errors and notification logs.

### Testing Status Updates
1. Open Manager Dashboard in one browser tab
2. Open Employee Portal (Employee 1) in another tab
3. Click "Send Help Request" in employee view
4. Watch notification appear on manager dashboard
5. See roster card turn red with pulsing indicator

## Troubleshooting

### Map not loading
- Check browser console for tile errors
- Verify internet connection (OSM tiles require network)
- Clear browser cache

### Notifications not appearing
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Try hard refresh (Ctrl+Shift+R)

### Status updates not saving
- Confirm backend API is accessible
- Check POST request in Network tab
- Verify employee ID is valid (1-10)

## Future Enhancements

- WebSocket for real-time updates (remove polling)
- Push notifications (browser API)
- Offline support (Service Worker + IndexedDB)
- Dark mode toggle
- Custom geofence drawing on map
- Employee search and filtering
- Export roster to CSV
- Print-friendly layouts
