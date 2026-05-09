import { useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, Tooltip, useMap, useMapEvents } from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from "leaflet";
import { useTheme } from "next-themes";
import type { Hospital } from "@/lib/api";

// Fix default marker icons
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

// Component to handle auto-panning when a hospital is selected from the list
function MapController({ 
  center, 
  selectedHospital 
}: { 
  center: [number, number]; 
  selectedHospital?: Hospital | null 
}) {
  const map = useMap();
  
  useEffect(() => {
    if (selectedHospital) {
      map.flyTo([selectedHospital.latitude, selectedHospital.longitude], 15, { duration: 0.8 });
    } else {
      map.flyTo(center, map.getZoom() < 11 ? 11 : map.getZoom(), { duration: 0.8 });
    }
  }, [center, selectedHospital, map]);
  
  return null;
}

// Component to detect when user pans/zooms the map
function MapEvents({ onBoundsChange }: { onBoundsChange?: (center: [number, number]) => void }) {
  useMapEvents({
    moveend: (e) => {
      const map = e.target;
      const center = map.getCenter();
      if (onBoundsChange) {
        onBoundsChange([center.lat, center.lng]);
      }
    },
  });
  return null;
}

interface Props {
  center: [number, number];
  hospitals: Hospital[];
  selectedHospital?: Hospital | null;
  onBoundsChange?: (center: [number, number]) => void;
}

export function HospitalMap({ center, hospitals, selectedHospital, onBoundsChange }: Props) {
  const mapRef = useRef<L.Map | null>(null);
  const { theme } = useTheme();
  
  const isDark = theme === "dark";
  const tileUrl = isDark 
    ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
    : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

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
        url={tileUrl}
      />
      <MapController center={center} selectedHospital={selectedHospital} />
      <MapEvents onBoundsChange={onBoundsChange} />
      
      <Marker position={center} icon={userIcon}>
        <Popup>Your location</Popup>
      </Marker>
      
      {hospitals.map((h, i) => (
        <Marker
          key={`${h.name}-${i}`}
          position={[h.latitude, h.longitude]}
          icon={hospitalIcon}
        >
          <Tooltip direction="top" offset={[0, -20]} permanent={i < 20} className="font-semibold text-xs text-foreground bg-background">
            {h.name}
          </Tooltip>
          <Popup>
            <div className="space-y-2">
              <div>
                <div className="font-semibold text-sm">{h.name}</div>
                {h.address && <div className="text-xs text-muted-foreground">{h.address}</div>}
              </div>
              
              <div className="text-xs space-y-1">
                {(h.distance_km ?? h.distance) != null && (
                  <div>📍 {(h.distance_km ?? h.distance)?.toFixed(2)} km away</div>
                )}
                {h.phone && <div>📞 <a href={`tel:${h.phone}`} className="hover:underline">{h.phone}</a></div>}
                {h.rating != null && <div>⭐ {h.rating} / 5.0</div>}
              </div>
              
              <div className="pt-1 border-t">
                <a 
                  href={`https://www.google.com/maps/dir/?api=1&destination=${h.latitude},${h.longitude}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex w-full items-center justify-center rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90"
                >
                  Get Directions
                </a>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
