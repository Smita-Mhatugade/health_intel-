import { useEffect, useMemo, useState } from "react";
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
import { Loader2, MapPin, Search, Locate, Phone, Star } from "lucide-react";
import { apiClient, Hospital } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { HospitalMap } from "@/components/HospitalMap";
import { CATEGORY_LABELS } from "@/components/AnalysisForm";
import { useStore } from "@/store/useStore";
import { toast } from "sonner";
import axios from "axios";

type Mode = "geo" | "address" | "manual";

export default function Hospitals() {
  const [mode, setMode] = useState<Mode>("geo");
  const [lat, setLat] = useState<number>(40.7128);
  const [lng, setLng] = useState<number>(-74.006);
  const [address, setAddress] = useState("");
  const [radius, setRadius] = useState<number>(25);
  const [searching, setSearching] = useState(false);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);

  const history = useStore((s) => s.history);
  const defaultCat = history[0]?.diseaseCategory || "heart_disease";
  const [category, setCategory] = useState<string>(defaultCat);

  const { data: diseases } = useQuery({
    queryKey: ["disease-config"],
    queryFn: apiClient.diseaseConfig,
  });

  const categoryOptions = useMemo(() => {
    const fromApi = (diseases ?? []).map((d: any) => d.id || d.category || d.name).filter(Boolean);
    return Array.from(new Set([...fromApi, ...Object.keys(CATEGORY_LABELS)]));
  }, [diseases]);

  const useMyLocation = () => {
    if (!navigator.geolocation) return toast.error("Geolocation not available");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(pos.coords.latitude);
        setLng(pos.coords.longitude);
        toast.success("Location set");
      },
      () => toast.error("Could not get your location")
    );
  };

  const geocode = async () => {
    if (!address.trim()) return;
    try {
      const r = await axios.get("https://nominatim.openstreetmap.org/search", {
        params: { q: address, format: "json", limit: 1 },
      });
      if (r.data?.[0]) {
        setLat(parseFloat(r.data[0].lat));
        setLng(parseFloat(r.data[0].lon));
        toast.success(`Located: ${r.data[0].display_name}`);
      } else {
        toast.error("Address not found");
      }
    } catch {
      toast.error("Geocoding failed");
    }
  };

  const search = async () => {
    setSearching(true);
    try {
      const data = await apiClient.recommendHospitals({
        latitude: lat,
        longitude: lng,
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

  useEffect(() => {
    // Try to fetch user location on mount
    if (mode === "geo" && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLat(pos.coords.latitude);
          setLng(pos.coords.longitude);
        },
        () => {} // ignore silently
      );
    }
  }, []); // eslint-disable-line

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
          <CardTitle className="text-base">Location & filters</CardTitle>
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
            <Button onClick={useMyLocation} variant="secondary" className="gap-2">
              <Locate className="h-4 w-4" /> Use my current location
            </Button>
          )}

          {mode === "address" && (
            <div className="flex gap-2">
              <Input
                placeholder="Enter city or address (e.g., Boston, MA)"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && geocode()}
              />
              <Button onClick={geocode} variant="secondary">Locate</Button>
            </div>
          )}

          {mode === "manual" && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs">Latitude</Label>
                <Input type="number" step="any" value={lat} onChange={(e) => setLat(Number(e.target.value))} />
              </div>
              <div>
                <Label className="text-xs">Longitude</Label>
                <Input type="number" step="any" value={lng} onChange={(e) => setLng(Number(e.target.value))} />
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

          <Button onClick={search} disabled={searching} size="lg" className="w-full gap-2">
            {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            Find Hospitals
          </Button>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div className="overflow-hidden rounded-xl shadow-card">
          <HospitalMap center={[lat, lng]} hospitals={hospitals} />
        </div>

        <Card className="shadow-card">
          <CardHeader className="border-b">
            <CardTitle className="text-base">
              Results {hospitals.length > 0 && <span className="text-muted-foreground">({hospitals.length})</span>}
            </CardTitle>
          </CardHeader>
          <CardContent className="max-h-[520px] space-y-3 overflow-y-auto p-4">
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
            {hospitals.map((h, i) => {
              const dist = h.distance_km ?? h.distance;
              return (
                <div
                  key={`${h.name}-${i}`}
                  className="rounded-lg border bg-card p-3 transition-colors hover:bg-accent/50"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <h4 className="truncate font-semibold">{h.name}</h4>
                      {h.address && (
                        <p className="line-clamp-2 text-xs text-muted-foreground">{h.address}</p>
                      )}
                    </div>
                    {dist != null && (
                      <span className="shrink-0 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                        {dist.toFixed(1)} km
                      </span>
                    )}
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                    {h.phone && (
                      <a href={`tel:${h.phone}`} className="inline-flex items-center gap-1 hover:text-primary">
                        <Phone className="h-3 w-3" /> {h.phone}
                      </a>
                    )}
                    {h.rating != null && (
                      <span className="inline-flex items-center gap-1">
                        <Star className="h-3 w-3 fill-warning text-warning" /> {h.rating}
                      </span>
                    )}
                    {h.specialties && h.specialties.length > 0 && (
                      <span className="truncate">{h.specialties.slice(0, 3).join(", ")}</span>
                    )}
                  </div>
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
