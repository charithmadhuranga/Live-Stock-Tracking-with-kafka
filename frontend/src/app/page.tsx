"use client";

import { useEffect } from "react";
import { Activity, MapPin, Thermometer, AlertTriangle } from "lucide-react";
import dynamic from "next/dynamic";
import AnimalHealthChart from "@/components/AnimalHealthChart";
import AlertTable from "@/components/AlertTable";

const MapView = dynamic(() => import("@/components/MapView"), {
  ssr: false,
  loading: () => (
    <div className="h-[500px] bg-stone-100 rounded-lg flex items-center justify-center text-muted-foreground">
      Loading map...
    </div>
  ),
});
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { connectTelemetryWebSocket, disconnectTelemetryWebSocket, useTelemetryStore } from "@/lib/telemetry";

export default function Dashboard() {
  const animalPositions = useTelemetryStore((s) => s.animalPositions);
  const alerts = useTelemetryStore((s) => s.alerts);
  const isConnected = useTelemetryStore((s) => s.isConnected);

  useEffect(() => {
    connectTelemetryWebSocket();
    return () => {
      disconnectTelemetryWebSocket();
    };
  }, []);

  let avgTemp = 0;
  let avgActivity = 0;
  try {
    const positions = Array.from(animalPositions.values());
    if (positions.length > 0) {
      const temps = positions.map((p) => Number(p.temperature)).filter((t) => !isNaN(t));
      if (temps.length > 0) avgTemp = temps.reduce((a, b) => a + b, 0) / temps.length;
      
      const acts = positions.map((p) => Number(p.activity_level)).filter((a) => !isNaN(a));
      if (acts.length > 0) avgActivity = acts.reduce((a, b) => a + b, 0) / acts.length;
    }
  } catch (e) {
    console.error("Error calculating averages:", e);
  }

  return (
    <div className="min-h-screen bg-stone-50">
      <header className="bg-gradient-to-r from-green-800 to-green-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Activity className="h-7 w-7" />
                Livestock Tracking Platform
              </h1>
              <p className="text-green-100 text-sm mt-1">
                Real-time monitoring & geofence management
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Badge
                variant={isConnected ? "secondary" : "destructive"}
                className={isConnected ? "bg-green-500 text-white" : "bg-red-500 text-white"}
              >
                {isConnected ? "● Live" : "○ Disconnected"}
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-white border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-800 flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Active Animals
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-700">
                {animalPositions.size}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Connected to system
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-800 flex items-center gap-2">
                <Thermometer className="h-4 w-4" />
                Avg Temperature
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600">
                {avgTemp.toFixed(1)}°C
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Across all animals
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-800 flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Avg Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {avgActivity.toFixed(1)}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Movement index
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-800 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Active Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">{alerts.length}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Geofence breaches
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MapView />
          <AnimalHealthChart />
        </div>

        <AlertTable />
      </main>
    </div>
  );
}
