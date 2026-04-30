import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import type { Hospital } from "@/lib/api";

// Fix default marker icons (Leaflet expects file paths)
const defaultIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const userIcon = L.divIcon({
  className: "",
  html: `<div style="width:18px;height:18px;border-radius:50%;background:#2563eb;border:3px solid white;box-shadow:0 0 0 2px #2563eb;"></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

const hospitalIcon = L.divIcon({
  className: "",
  html: `<div style="width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:50% 50% 50% 0;transform:rotate(-45deg);background:#ef4444;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3)"><span style="transform:rotate(45deg);color:white;font-weight:bold;font-size:14px">+</span></div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -28],
});

function Recenter({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lng], map.getZoom() < 11 ? 11 : map.getZoom());
  }, [lat, lng, map]);
  return null;
}

interface Props {
  center: [number, number];
  hospitals: Hospital[];
  onSelectHospital?: (h: Hospital) => void;
}

export function HospitalMap({ center, hospitals }: Props) {
  const mapRef = useRef<L.Map | null>(null);
  return (
    <MapContainer
      center={center}
      zoom={11}
      scrollWheelZoom
      style={{ height: "100%", width: "100%", minHeight: 420 }}
      className="rounded-xl border"
      ref={(m) => (mapRef.current = m as any)}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Recenter lat={center[0]} lng={center[1]} />
      <Marker position={center} icon={userIcon}>
        <Popup>Your location</Popup>
      </Marker>
      {hospitals.map((h, i) => (
        <Marker
          key={`${h.name}-${i}`}
          position={[h.latitude, h.longitude]}
          icon={hospitalIcon}
        >
          <Popup>
            <div className="space-y-1">
              <div className="font-semibold">{h.name}</div>
              {h.address && <div className="text-xs text-muted-foreground">{h.address}</div>}
              {(h.distance_km ?? h.distance) != null && (
                <div className="text-xs">
                  📍 {(h.distance_km ?? h.distance)?.toFixed(2)} km away
                </div>
              )}
              {h.phone && <div className="text-xs">📞 {h.phone}</div>}
              {h.rating != null && <div className="text-xs">⭐ {h.rating}</div>}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
