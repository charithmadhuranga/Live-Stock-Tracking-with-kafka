import { create } from "zustand";

export interface TelemetryData {
  belt_id: string;
  latitude: number;
  longitude: number;
  temperature: number;
  activity_level: number;
  timestamp: number;
}

export interface AlertData {
  id: string;
  belt_id: string;
  latitude: number;
  longitude: number;
  paddock_id: string;
  timestamp: number;
  type: "geofence_breach";
  expected_paddock_id?: string;
}

interface TelemetryState {
  animalPositions: Map<string, TelemetryData>;
  telemetryHistory: Map<string, TelemetryData[]>;
  alerts: AlertData[];
  isConnected: boolean;
  setConnected: (connected: boolean) => void;
  updatePosition: (data: unknown) => void;
  addAlert: (alert: AlertData) => void;
  clearAlerts: () => void;
}

export const useTelemetryStore = create<TelemetryState>((set) => ({
  animalPositions: new Map(),
  telemetryHistory: new Map(),
  alerts: [],
  isConnected: false,

  setConnected: (connected) => set({ isConnected: connected }),

  updatePosition: (data) =>
    set((state) => {
      try {
        const d = data as TelemetryData;
        if (!d?.belt_id) return state;
        
        const newPositions = new Map(state.animalPositions);
        newPositions.set(d.belt_id, {
          belt_id: String(d.belt_id || ""),
          latitude: Number(d.latitude) || 0,
          longitude: Number(d.longitude) || 0,
          temperature: Number(d.temperature) || 0,
          activity_level: Number(d.activity_level) || 0,
          timestamp: Number(d.timestamp) || 0,
        });

        const newHistory = new Map(state.telemetryHistory);
        const history = newHistory.get(d.belt_id) || [];
        const updatedHistory = [...history, d].slice(-100);
        newHistory.set(d.belt_id, updatedHistory);

        return { animalPositions: newPositions, telemetryHistory: newHistory };
      } catch {
        return state;
      }
    }),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts].slice(0, 100),
    })),

  clearAlerts: () => set({ alerts: [] }),
}));

let ws: WebSocket | null = null;
let wsReconnectTimeout: NodeJS.Timeout | null = null;
let pollInterval: NodeJS.Timeout | null = null;

function getWsUrl(): string {
  const wsPort = "8000";
  return `ws://localhost:${wsPort}/ws/telemetry`;
}

export function connectTelemetryWebSocket() {
  if (typeof window === "undefined") return null;
  
  const wsUrl = getWsUrl();
  
  if (ws?.readyState === WebSocket.OPEN) return ws;

  try {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("WebSocket connected");
      useTelemetryStore.getState().setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("WebSocket message:", data);
        
        if (data.type === "telemetry") {
          useTelemetryStore.getState().updatePosition(data);
        } else if (data.type === "alert") {
          useTelemetryStore.getState().addAlert(data);
        }
      } catch (e) {
        console.error("Error parsing WebSocket message:", e);
      }
    };

    ws.onclose = (event) => {
      console.log("WebSocket disconnected", event.code, event.reason);
      useTelemetryStore.getState().setConnected(false);
      
      if (!event.wasClean) {
        scheduleReconnect();
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      useTelemetryStore.getState().setConnected(false);
    };

    return ws;
  } catch (e) {
    console.error("Failed to create WebSocket:", e);
    useTelemetryStore.getState().setConnected(false);
    return null;
  }
}

function scheduleReconnect() {
  if (wsReconnectTimeout) return;
  
  console.log("Scheduling WebSocket reconnect in 3 seconds...");
  wsReconnectTimeout = setTimeout(() => {
    wsReconnectTimeout = null;
    ws = null;
    connectTelemetryWebSocket();
  }, 3000);
}

function startPolling() {
  if (pollInterval) return;
  
  const poll = async () => {
    try {
      const res = await fetch("/api/telemetry/latest");
      if (res.ok) {
        const data = await res.json();
        useTelemetryStore.getState().setConnected(true);
        data.forEach((item: TelemetryData) => {
          if (item.belt_id) {
            useTelemetryStore.getState().updatePosition(item);
          }
        });
      } else {
        useTelemetryStore.getState().setConnected(false);
      }
    } catch (e) {
      console.error("Polling error:", e);
      useTelemetryStore.getState().setConnected(false);
    }
  };
  
  poll();
  pollInterval = setInterval(poll, 3000);
}

export function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}

export function disconnectTelemetryWebSocket() {
  if (wsReconnectTimeout) {
    clearTimeout(wsReconnectTimeout);
    wsReconnectTimeout = null;
  }
  
  if (ws) {
    ws.close();
    ws = null;
  }
  
  stopPolling();
}

export async function fetchPaddocks() {
  const res = await fetch("/api/paddocks");
  const paddocks = await res.json();
  return {
    type: "FeatureCollection",
    features: paddocks.map((p: any) => ({
      type: "Feature",
      properties: { id: p.id, name: p.name },
      geometry: {
        type: "Polygon",
        coordinates: [parseWKTToGeoJSON(p.geometry)],
      },
    })),
  };
}

function parseWKTToGeoJSON(wkt: string): number[][] {
  const match = wkt.match(/POLYGON\(\((.+)\)\)/);
  if (!match) return [];
  return match[1].split(", ").map((pair) => {
    const [lon, lat] = pair.split(" ").map(Number);
    return [lon, lat];
  });
}

export async function fetchAlerts(): Promise<AlertData[]> {
  const res = await fetch("/api/alerts");
  return res.json();
}

export async function fetchTelemetryHistory(beltId: string, hours = 24): Promise<TelemetryData[]> {
  const res = await fetch(`/api/telemetry/${beltId}?hours=${hours}`);
  return res.json();
}
