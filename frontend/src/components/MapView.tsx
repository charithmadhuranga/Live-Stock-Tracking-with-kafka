"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useTelemetryStore } from "@/lib/telemetry";

const createIcon = (color: string) => new L.Icon({
  iconUrl: `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 41"><path fill="${color}" d="M12 0C5 0 0 7 0 14c0 10 12 27 12 27s12-17 12-27c0-7-5-14-12-14z"/></svg>`)}`,
  shadowUrl: "data:image/svg+xml,encoded",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const livestockIcon = createIcon("#22c55e");
const breachedIcon = createIcon("#ef4444");

interface Paddock {
  id: string;
  name: string;
  geometry: string;
}

function parseWKTToCoords(wkt: string): number[][] {
  try {
    const match = wkt.match(/POLYGON\(\((.+)\)\)/);
    if (!match) return [];
    return match[1].split(",").map((pair) => {
      const coords = pair.trim().split(/\s+/);
      if (coords.length < 2) return [0, 0];
      const lon = Number(coords[0]);
      const lat = Number(coords[1]);
      if (isNaN(lat) || isNaN(lon)) return [0, 0];
      return [lat, lon];
    });
  } catch (e) {
    console.error("Error parsing WKT:", e);
    return [];
  }
}

function PaddocksLayer({ paddocks }: { paddocks: Paddock[] }) {
  const geoJsonData: GeoJSON.FeatureCollection = {
    type: "FeatureCollection",
    features: paddocks.map((p) => ({
      type: "Feature" as const,
      properties: { id: p.id, name: p.name },
      geometry: {
        type: "Polygon" as const,
        coordinates: [parseWKTToCoords(p.geometry)],
      },
    })),
  };

  const style = {
    fillColor: "#22c55e",
    fillOpacity: 0.2,
    color: "#166534",
    weight: 2,
  };

  const onEachFeature = (feature: GeoJSON.Feature, layer: L.Layer) => {
    if (feature.properties?.name) {
      layer.bindPopup(`<strong>${feature.properties.name}</strong>`);
    }
  };

  return <GeoJSON data={geoJsonData} style={style} onEachFeature={onEachFeature} />;
}

function AnimalMarkers() {
  const { animalPositions, alerts } = useTelemetryStore();
  const breachedBeltIds = new Set(alerts.map((a) => a.belt_id));

  return (
    <>
      {Array.from(animalPositions.entries()).map(([beltId, data]) => {
        const isBreached = breachedBeltIds.has(beltId);
        return (
          <Marker
            key={beltId}
            position={[data.latitude, data.longitude]}
            icon={isBreached ? breachedIcon : livestockIcon}
          >
            <Popup>
              <div className="p-2">
                <strong className="text-lg">{beltId}</strong>
                <div className="mt-2 space-y-1 text-sm">
                  <p>Temp: {data.temperature?.toFixed(1) ?? "N/A"}°C</p>
                  <p>Activity: {data.activity_level?.toFixed(1) ?? "N/A"}</p>
                  <p>
                    Time: {new Date(data.timestamp * 1000).toLocaleTimeString()}
                  </p>
                </div>
                {isBreached && (
                  <Badge variant="destructive" className="mt-2">
                    Geofence Breach
                  </Badge>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
}

function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    if (center[0] !== 0 && center[1] !== 0) {
      map.setView(center, map.getZoom());
    }
  }, [center, map]);
  return null;
}

export default function MapView() {
  const [paddocks, setPaddocks] = useState<Paddock[]>([]);
  const [center, setCenter] = useState<[number, number]>([-36.5987, 144.9405]);
  const [mapError, setMapError] = useState<string | null>(null);
  const animalPositions = useTelemetryStore((s) => s.animalPositions);

  useEffect(() => {
    fetch("/api/paddocks")
      .then((res) => res.json())
      .then((data) => {
        setPaddocks(data);
        if (data.length > 0) {
          const coords = parseWKTToCoords(data[0].geometry);
          if (coords.length > 0 && !isNaN(coords[0][0]) && !isNaN(coords[0][1])) {
            setCenter([coords[0][0], coords[0][1]]);
          }
        }
      })
      .catch((e) => {
        console.error("Failed to load paddocks:", e);
        setMapError("Failed to load paddocks");
      });
  }, []);

  useEffect(() => {
    if (animalPositions.size > 0) {
      const positions = Array.from(animalPositions.values());
      const validPositions = positions.filter(p => !isNaN(p.latitude) && !isNaN(p.longitude));
      if (validPositions.length > 0) {
        const avgLat = validPositions.reduce((sum, p) => sum + p.latitude, 0) / validPositions.length;
        const avgLng = validPositions.reduce((sum, p) => sum + p.longitude, 0) / validPositions.length;
        if (!isNaN(avgLat) && !isNaN(avgLng)) {
          setCenter([avgLat, avgLng]);
        }
      }
    }
  }, [animalPositions]);

  return (
    <Card className="h-[500px]">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center justify-between">
          <span>Live Tracking Map</span>
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            {animalPositions.size} Animals
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {mapError ? (
          <div className="h-[420px] flex items-center justify-center bg-stone-100 text-stone-500">
            <p>{mapError}</p>
          </div>
        ) : (
        <MapContainer
          center={center}
          zoom={14}
          style={{ height: "420px", width: "100%" }}
          whenReady={() => {
            console.log("Map ready");
          }}
        >
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <PaddocksLayer paddocks={paddocks} />
          <AnimalMarkers />
          <MapUpdater center={center} />
        </MapContainer>
        )}
      </CardContent>
    </Card>
  );
}
