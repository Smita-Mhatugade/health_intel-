import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";

export interface LocationState {
  lat: number | null;
  lon: number | null;
  city: string | null;
  state: string | null;
  country: string | null;
  loading: boolean;
  error: string | null;
  source: "gps" | "manual" | null;
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

  const getLocation = useCallback(async () => {
    setLocation((prev) => ({ ...prev, loading: true, error: null }));

    // Check if geolocation API is available
    if (!navigator.geolocation) {
      const errorMsg = "Browser geolocation is not supported by your browser.";
      setLocation((prev) => ({ ...prev, error: errorMsg, loading: false }));
      toast.error(errorMsg);
      return;
    }

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
      // Browser geolocation failed
      let errorMsg = "Failed to retrieve location from browser.";
      if (geoError?.code === 1) {
        errorMsg = "Location access denied. Please grant location permissions in your browser settings.";
      } else if (geoError?.code === 2) {
        errorMsg = "Location unavailable. Ensure your device has location services enabled.";
      } else if (geoError?.code === 3) {
        errorMsg = "Location request timed out. Please try again.";
      }
      
      setLocation((prev) => ({ ...prev, error: errorMsg, loading: false }));
      toast.error(errorMsg);
    }
  }, []);

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
