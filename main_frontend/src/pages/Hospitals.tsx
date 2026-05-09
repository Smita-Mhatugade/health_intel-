import { useEffect, useMemo, useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, MapPin, Search, Locate, Phone, Star, Navigation } from "lucide-react";
import { apiClient, Hospital } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { HospitalMap } from "@/components/HospitalMap";
import { CATEGORY_LABELS } from "@/components/AnalysisForm";
import { useStore } from "@/store/useStore";
import { toast } from "sonner";
import axios from "axios";
import { useGeolocation } from "@/hooks/useGeolocation";

type Mode = "geo" | "address" | "manual";

export default function Hospitals() {
  const [mode, setMode] = useState<Mode>("geo");
  const { location, getLocation, setCoordinates } = useGeolocation();
  
  const [lat, setLat] = useState<number>(40.7128);
  const [lng, setLng] = useState<number>(-74.006);

  // Sync coords from hook or localStorage
  useEffect(() => {
    const savedLat = localStorage.getItem("hi_lat");
    const savedLng = localStorage.getItem("hi_lng");
    if (location.lat && location.lon) {
      setLat(location.lat);
      setLng(location.lon);
      localStorage.setItem("hi_lat", location.lat.toString());
      localStorage.setItem("hi_lng", location.lon.toString());
    } else if (savedLat && savedLng && !location.loading) {
      setLat(parseFloat(savedLat));
      setLng(parseFloat(savedLng));
    }
  }, [location.lat, location.lon, location.loading]);

  const [address, setAddress] = useState("");
  const [radius, setRadius] = useState<number>(10);
  const [searching, setSearching] = useState(false);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  
  // New UI states
  const [selectedHospital, setSelectedHospital] = useState<Hospital | null>(null);
  const [mapBoundsCenter, setMapBoundsCenter] = useState<[number, number] | null>(null);
  const [minRating, setMinRating] = useState<number>(0);

  const history = useStore((s) => s.history);
  const defaultCat = history[0]?.diseaseCategory || "heart_disease";
  const [category, setCategory] = useState<string>(defaultCat);

  const listRef = useRef<HTMLDivElement>(null);

  const { data: diseases } = useQuery({
    queryKey: ["disease-config"],
    queryFn: apiClient.diseaseConfig,
  });

  const categoryOptions = useMemo(() => {
    const fromApi = (diseases ?? []).map((d: any) => d.id || d.category || d.name).filter(Boolean);
    return Array.from(new Set([...fromApi, ...Object.keys(CATEGORY_LABELS)]));
  }, [diseases]);

  const geocode = async () => {
    if (!address.trim()) return;
    try {
      const r = await axios.get("https://nominatim.openstreetmap.org/search", {
        params: { q: address, format: "json", limit: 1 },
      });
      if (r.data?.[0]) {
        await setCoordinates(parseFloat(r.data[0].lat), parseFloat(r.data[0].lon));
        toast.success(`Located: ${r.data[0].display_name}`);
      } else {
        toast.error("Address not found");
      }
    } catch {
      toast.error("Geocoding failed");
    }
  };

  const search = async (searchLat = lat, searchLng = lng) => {
    setSearching(true);
    setSelectedHospital(null);
    setMapBoundsCenter(null);
    try {
      const data = await apiClient.recommendHospitals({
        latitude: searchLat,
        longitude: searchLng,
        disease_category: category,
        radius_km: radius,
      });
      setHospitals(data);
      if (data.length === 0) toast.info("No hospitals found in this radius");
      else toast.success(`Found ${data.length} hospitals`);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Search failed — backend may be offline");
    } finally {
      setSearching(false);
    }
  };

  // Search this area logic
  const handleSearchThisArea = () => {
    if (mapBoundsCenter) {
      setCoordinates(mapBoundsCenter[0], mapBoundsCenter[1]);
      search(mapBoundsCenter[0], mapBoundsCenter[1]);
    }
  };

  const handleMapBoundsChange = (center: [number, number]) => {
    // Only show button if moved significantly (approx 500m)
    if (Math.abs(center[0] - lat) > 0.005 || Math.abs(center[1] - lng) > 0.005) {
      setMapBoundsCenter(center);
    } else {
      setMapBoundsCenter(null);
    }
  };

  useEffect(() => {
    if (mode === "geo" && !location.lat && !location.loading && !localStorage.getItem("hi_lat")) {
      getLocation();
    }
  }, []); // eslint-disable-line

  const filteredHospitals = useMemo(() => {
    return hospitals.filter(h => (h.rating ?? 0) >= minRating);
  }, [hospitals, minRating]);

  return (
    <div className="mx-auto w-full max-w-7xl px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Find Hospitals</h1>
        <p className="text-sm text-muted-foreground">
          Locate specialized hospitals near you for the chosen condition.
        </p>
      </div>

      <Card className="mb-6 shadow-card">
        <CardHeader className="border-b">
          <CardTitle className="text-base flex justify-between items-center flex-wrap gap-2">
            <span>Location & filters</span>
            {location.city && (
              <span className="text-sm font-normal text-muted-foreground flex items-center gap-1.5">
                <MapPin className="h-3 w-3" />
                Detected: {location.city}{location.state ? `, ${location.state}` : ''}
                {location.source && (
                  <span className={`ml-1 rounded-full px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${
                    location.source === "gps"
                      ? "bg-green-500/15 text-green-600"
                      : location.source === "ip"
                      ? "bg-amber-500/15 text-amber-600"
                      : "bg-blue-500/15 text-blue-600"
                  }`}>
                    {location.source}
                  </span>
                )}
              </span>
            )}
            {location.error && !location.city && (
              <span className="text-xs font-normal text-destructive flex items-center gap-1">
                ⚠ {location.error}
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 pt-6">
          <div className="flex flex-wrap gap-2">
            <Button
              variant={mode === "geo" ? "default" : "outline"}
              size="sm"
              onClick={() => setMode("geo")}
              className="gap-1.5"
            >
              <Locate className="h-4 w-4" /> My location
            </Button>
            <Button
              variant={mode === "address" ? "default" : "outline"}
              size="sm"
              onClick={() => setMode("address")}
              className="gap-1.5"
            >
              <MapPin className="h-4 w-4" /> By address
            </Button>
            <Button
              variant={mode === "manual" ? "default" : "outline"}
              size="sm"
              onClick={() => setMode("manual")}
            >
              Manual lat/lng
            </Button>
          </div>

          {mode === "geo" && (
            <Button onClick={getLocation} disabled={location.loading} variant="secondary" className="gap-2">
              {location.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Locate className="h-4 w-4" />}
              {location.loading ? "Acquiring Location..." : "Refresh my current location"}
            </Button>
          )}

          {mode === "address" && (
            <div className="flex gap-2">
              <Input
                placeholder="Enter city or address (e.g., Mumbai, MH)"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && geocode()}
              />
              <Button onClick={geocode} disabled={location.loading} variant="secondary">
                {location.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Locate"}
              </Button>
            </div>
          )}

          {mode === "manual" && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs">Latitude</Label>
                <Input 
                  type="number" 
                  step="any" 
                  value={lat} 
                  onChange={(e) => setCoordinates(Number(e.target.value), lng)} 
                />
              </div>
              <div>
                <Label className="text-xs">Longitude</Label>
                <Input 
                  type="number" 
                  step="any" 
                  value={lng} 
                  onChange={(e) => setCoordinates(lat, Number(e.target.value))} 
                />
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <Label className="text-xs">Disease category</Label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {categoryOptions.map((c) => (
                    <SelectItem key={c} value={c}>{CATEGORY_LABELS[c] ?? c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between">
                <Label className="text-xs">Radius</Label>
                <span className="text-xs font-medium">{radius} km</span>
              </div>
              <Slider
                value={[radius]}
                onValueChange={(v) => setRadius(v[0])}
                min={5}
                max={200}
                step={5}
              />
            </div>
          </div>

          <Button onClick={() => search(lat, lng)} disabled={searching || location.loading} size="lg" className="w-full gap-2">
            {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            Find Hospitals
          </Button>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div className="relative overflow-hidden rounded-xl shadow-card h-[500px] lg:h-auto z-10">
          <HospitalMap 
            center={[lat, lng]} 
            hospitals={filteredHospitals} 
            selectedHospital={selectedHospital}
            onBoundsChange={handleMapBoundsChange}
          />
          
          {mapBoundsCenter && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000]">
              <Button 
                onClick={handleSearchThisArea} 
                className="shadow-lg rounded-full px-6 bg-background text-foreground hover:bg-accent border border-border"
                size="sm"
              >
                <Search className="w-4 h-4 mr-2" />
                Search this area
              </Button>
            </div>
          )}
        </div>

        <Card className="shadow-card flex flex-col h-[600px] lg:h-auto">
          <CardHeader className="border-b pb-4 shrink-0">
            <CardTitle className="text-base flex justify-between items-center">
              <span>Results <span className="text-muted-foreground font-normal text-sm">({filteredHospitals.length})</span></span>
              
              {hospitals.length > 0 && (
                <div className="flex gap-1.5">
                  <Button 
                    variant={minRating === 0 ? "default" : "outline"} 
                    size="sm" 
                    className="h-7 text-xs px-2"
                    onClick={() => setMinRating(0)}
                  >
                    All
                  </Button>
                  <Button 
                    variant={minRating === 4.0 ? "default" : "outline"} 
                    size="sm" 
                    className="h-7 text-xs px-2"
                    onClick={() => setMinRating(4.0)}
                  >
                    ⭐ 4.0+
                  </Button>
                  <Button 
                    variant={minRating === 4.5 ? "default" : "outline"} 
                    size="sm" 
                    className="h-7 text-xs px-2"
                    onClick={() => setMinRating(4.5)}
                  >
                    ⭐ 4.5+
                  </Button>
                </div>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent 
            className="flex-1 overflow-y-auto p-4 space-y-3"
            ref={listRef}
          >
            {searching && (
              <div className="flex items-center justify-center py-12 text-muted-foreground">
                <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Searching…
              </div>
            )}
            {!searching && hospitals.length === 0 && (
              <p className="py-12 text-center text-sm text-muted-foreground">
                No hospitals yet. Set a location and click <em>Find Hospitals</em>.
              </p>
            )}
            {filteredHospitals.map((h, i) => {
              const dist = h.distance_km ?? h.distance;
              const isSelected = selectedHospital?.name === h.name;
              
              return (
                <div
                  key={`${h.name}-${i}`}
                  onClick={() => setSelectedHospital(h)}
                  className={`cursor-pointer rounded-lg border p-3 transition-colors ${
                    isSelected 
                      ? "bg-primary/5 border-primary/50 shadow-sm" 
                      : "bg-card hover:bg-accent/50"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <h4 className="truncate font-semibold">{h.name}</h4>
                      {h.address && (
                        <p className="line-clamp-2 text-xs text-muted-foreground mt-0.5">{h.address}</p>
                      )}
                    </div>
                    {dist != null && (
                      <span className="shrink-0 rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
                        {dist.toFixed(1)} km
                      </span>
                    )}
                  </div>
                  
                  <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2 text-xs text-muted-foreground">
                    {h.phone && (
                      <a 
                        href={`tel:${h.phone}`} 
                        className="inline-flex items-center gap-1 hover:text-primary transition-colors"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Phone className="h-3 w-3" /> {h.phone}
                      </a>
                    )}
                    {h.rating != null && (
                      <span className="inline-flex items-center gap-1 text-foreground font-medium">
                        <Star className="h-3 w-3 fill-warning text-warning" /> {h.rating}
                      </span>
                    )}
                    {h.specialties && h.specialties.length > 0 && (
                      <span className="truncate opacity-75">{h.specialties.slice(0, 2).join(", ")}</span>
                    )}
                  </div>
                  
                  {isSelected && (
                    <div className="mt-3 pt-2 border-t flex justify-end">
                      <a 
                        href={`https://www.google.com/maps/dir/?api=1&destination=${h.latitude},${h.longitude}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center rounded-md bg-primary/10 text-primary hover:bg-primary/20 px-3 py-1.5 text-xs font-medium transition-colors"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Navigation className="w-3 h-3 mr-1.5" />
                        Get Directions
                      </a>
                    </div>
                  )}
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>

      <p className="mt-6 text-center text-xs text-muted-foreground">
        Hospital data depends on the backend. For informational purposes only.
      </p>
    </div>
  );
}
