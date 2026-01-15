import React, { useState } from "react";
import { MapContainer, TileLayer, Circle, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { TextField, Button, Box, Typography } from "@mui/material";
import { DateTimePicker } from "@mui/lab";
import { formatISO } from "date-fns";

const DEFAULT_CENTER = [39.0997, -94.5786]; // Kansas City
const DEFAULT_RADIUS = 1000000; // meters

function AreaSelector({ area, setArea }) {
  useMapEvents({
    click(e) {
      setArea({ ...area, center: [e.latlng.lat, e.latlng.lng] });
    },
  });
  return (
    <Circle center={area.center} radius={area.radius} pathOptions={{ color: "blue" }} />
  );
}

export default function App() {
  const [area, setArea] = useState({ center: DEFAULT_CENTER, radius: DEFAULT_RADIUS });
  const [responses, setResponses] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);

  const handleQuery = async () => {
    setResponses([]); // Clear responses immediately
    const query = {
      center_lat: area.center[0],
      center_lon: area.center[1],
      radius_km: area.radius / 1000,
      message: "Report if you were in the area!",
    };
    await fetch("http://localhost:8000/publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(query),
    });
    setTimeout(async () => {
      const resp = await fetch("http://localhost:8000/responses");
      const data = await resp.json();
      setResponses(data);
      setLastUpdated(new Date().toLocaleString());
    }, 500);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Personnel Accountability MVP
      </Typography>
  <MapContainer center={area.center} zoom={4} style={{ height: "800px", width: "100vw" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <AreaSelector area={area} setArea={setArea} />
      </MapContainer>
      <Box sx={{ mt: 1, display: "flex", gap: 1 }}>
        <TextField
          label="Radius (km)"
          type="number"
          value={area.radius / 1000}
          inputProps={{ min: 0, step: 10 }}
          onChange={e => setArea({ ...area, radius: Number(e.target.value) * 1000 })}
        />
        <Button variant="contained" onClick={handleQuery}>
          Send Query
        </Button>
        <Button variant="outlined" color="secondary" onClick={() => setResponses([])} sx={{ ml: 2 }}>
          Clear Responses
        </Button>
      </Box>
      <Box sx={{ mt: 2 }}>
        <Typography variant="h6">Roster & Responses</Typography>
        {lastUpdated && (
          <Typography variant="body2" sx={{ mb: 1 }}>
            Last updated: {lastUpdated}
          </Typography>
        )}
        <Box>
          {responses.slice(0, 9).map((node, idx) => (
            <Box key={idx} sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1, minHeight: 32 }}>
              <Typography sx={{ minWidth: 90 }}>{node.name}</Typography>
              <Typography variant="body2" sx={{ minWidth: 150 }}>{node.contact_info}</Typography>
              <Typography color={node.response === "Yes" ? "green" : "red"} sx={{ minWidth: 40 }}>{node.response}</Typography>
              <Button size="small" disabled>Add</Button>
              <Button size="small" disabled sx={{ ml: 1 }}>Delete</Button>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
}
