import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import axios from "axios";

export interface LocationState {
  lat: number | null;
  lon: number | null;
  city: string | null;
  state: string | null;
  country: string | null;
  loading: boolean;
  error: string | null;
  source: "gps" | "ip" | "manual" | null;
}

/**
 * Fallback: use free IP-geolocation APIs to get approximate location.
 * Tries multiple providers in order so at least one should work.
 */
async function ipGeolocate(): Promise<{
  lat: number;
  lon: number;
  city?: string;
  state?: string;
  country?: string;
}> {
  // Provider 1: ipapi.co (free, no key needed, 1000/day) — HTTPS, most reliable
  try {
    const r = await axios.get("https://ipapi.co/json/", { timeout: 6000 });
    if (r.data?.latitude && r.data?.longitude) {
      return {
        lat: r.data.latitude,
        lon: r.data.longitude,
        city: r.data.city,
        state: r.data.region,
        country: r.data.country_name,
      };
    }
  } catch (e) {
    console.warn("[useGeolocation] ipapi.co failed:", e);
  }

  // Provider 2: ipwho.is (free, unlimited, no key, HTTPS)
  try {
    const r = await axios.get("https://ipwho.is/", { timeout: 6000 });
    if (r.data?.latitude && r.data?.longitude) {
      return {
        lat: r.data.latitude,
        lon: r.data.longitude,
        city: r.data.city,
        state: r.data.region,
        country: r.data.country,
      };
    }
  } catch (e) {
    console.warn("[useGeolocation] ipwho.is failed:", e);
  }

  // Provider 3: freeipapi.com (free, HTTPS, no key)
  try {
    const r = await axios.get("https://freeipapi.com/api/json", { timeout: 6000 });
    if (r.data?.latitude && r.data?.longitude) {
      return {
        lat: r.data.latitude,
        lon: r.data.longitude,
        city: r.data.cityName,
        state: r.data.regionName,
        country: r.data.countryName,
      };
    }
  } catch (e) {
    console.warn("[useGeolocation] freeipapi.com failed:", e);
  }

  // Provider 4: ip-api.com via HTTPS (requires paid plan, but try anyway)
  try {
    const r = await axios.get("https://ip-api.com/json/?fields=lat,lon,city,regionName,country", {
      timeout: 5000,
    });
    if (r.data?.lat && r.data?.lon) {
      return {
        lat: r.data.lat,
        lon: r.data.lon,
        city: r.data.city,
        state: r.data.regionName,
        country: r.data.country,
      };
    }
  } catch (e) {
    console.warn("[useGeolocation] ip-api.com failed:", e);
  }

  throw new Error("All IP geolocation providers failed");
}

export function useGeolocation() {
  const [location, setLocation] = useState<LocationState>({
    lat: null,
    lon: null,
    city: null,
    state: null,
    country: null,
    loading: false,
    error: null,
    source: null,
  });

  /**
   * Apply IP-based geolocation as a fallback.
   */
  const fallbackToIpLocation = useCallback(async () => {
    try {
      const ipData = await ipGeolocate();
      // Optionally enrich via backend reverse-geocode
      let city = ipData.city ?? null;
      let state = ipData.state ?? null;
      let country = ipData.country ?? null;

      try {
        const geoData = await apiClient.reverseGeocode(ipData.lat, ipData.lon);
        city = geoData.city !== "Unknown" ? geoData.city : city;
        state = geoData.state !== "Unknown" ? geoData.state : state;
        country = geoData.country !== "Unknown" ? geoData.country : country;
      } catch {
        // keep IP data as-is
      }

      setLocation({
        lat: ipData.lat,
        lon: ipData.lon,
        city,
        state,
        country,
        loading: false,
        error: null,
        source: "ip",
      });

      toast.success(
        `Approximate location: ${city ?? "Unknown city"}${state ? `, ${state}` : ""} (via IP)`
      );
      return true;
    } catch (e) {
      console.error("[useGeolocation] IP fallback failed:", e);
      return false;
    }
  }, []);

  const getLocation = useCallback(async () => {
    setLocation((prev) => ({ ...prev, loading: true, error: null }));

    // Check if geolocation API is available
    if (!navigator.geolocation) {
      console.warn("[useGeolocation] Browser geolocation unavailable, trying IP fallback");
      const ok = await fallbackToIpLocation();
      if (!ok) {
        const errorMsg = "Geolocation is not supported and IP fallback failed";
        setLocation((prev) => ({ ...prev, error: errorMsg, loading: false }));
        toast.error(errorMsg);
      }
      return;
    }

    // Try browser geolocation with a Promise wrapper for cleaner flow
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 600000, // Accept cached position up to 10 min old
        });
      });

      const { latitude, longitude } = position.coords;
      try {
        // Verify city using backend reverse-geocoding API
        const geoData = await apiClient.reverseGeocode(latitude, longitude);
        setLocation({
          lat: latitude,
          lon: longitude,
          city: geoData.city !== "Unknown" ? geoData.city : null,
          state: geoData.state !== "Unknown" ? geoData.state : null,
          country: geoData.country !== "Unknown" ? geoData.country : null,
          loading: false,
          error: null,
          source: "gps",
        });

        if (geoData.city && geoData.city !== "Unknown") {
          toast.success(`Location set to ${geoData.city}`);
        } else {
          toast.success("Coordinates acquired, but exact city is unknown.");
        }
      } catch (err) {
        console.error("Reverse geocoding failed", err);
        setLocation({
          lat: latitude,
          lon: longitude,
          city: null,
          state: null,
          country: null,
          loading: false,
          error: "Failed to verify city name",
          source: "gps",
        });
        toast.success("Coordinates acquired (Reverse geocoding offline)");
      }
    } catch (geoError: any) {
      // Browser geolocation failed — fall back to IP geolocation
      console.warn(
        `[useGeolocation] Browser geolocation failed (code=${geoError?.code}), trying IP fallback`
      );

      const ok = await fallbackToIpLocation();
      if (!ok) {
        let errorMsg = "Failed to retrieve location";
        if (geoError?.code === 1) {
          errorMsg = "Location access denied. IP fallback also failed.";
        } else if (geoError?.code === 2) {
          errorMsg = "Location unavailable. IP fallback also failed.";
        } else if (geoError?.code === 3) {
          errorMsg = "Location request timed out. IP fallback also failed.";
        }
        setLocation((prev) => ({ ...prev, error: errorMsg, loading: false }));
        toast.error(errorMsg);
      }
    }
  }, [fallbackToIpLocation]);

  // Update coordinates manually (e.g., from address geocoding)
  const setCoordinates = useCallback(async (lat: number, lon: number) => {
    setLocation((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const geoData = await apiClient.reverseGeocode(lat, lon);
      setLocation({
        lat,
        lon,
        city: geoData.city !== "Unknown" ? geoData.city : null,
        state: geoData.state !== "Unknown" ? geoData.state : null,
        country: geoData.country !== "Unknown" ? geoData.country : null,
        loading: false,
        error: null,
        source: "manual",
      });
    } catch (err) {
      setLocation({
        lat,
        lon,
        city: null,
        state: null,
        country: null,
        loading: false,
        error: "Failed to verify city name",
        source: "manual",
      });
    }
  }, []);

  return { location, getLocation, setCoordinates };
}
