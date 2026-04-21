# Frontend Documentation

The frontend is a **Next.js** application that provides the user interface for monitoring livestock in real-time.

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Main dashboard page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui components
│   │   ├── MapView.tsx       # Interactive map
│   │   ├── AnimalHealthChart.tsx  # Health charts
│   │   └── AlertTable.tsx    # Alerts display
│   └── lib/                  # Utilities
│       ├── telemetry.ts       # WebSocket & state management
│       └── utils.ts          # Helper functions
├── public/                   # Static assets
├── package.json              # Dependencies
└── next.config.ts           # Next.js configuration
```

## Technology Stack

- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript
- **State Management:** Zustand
- **Maps:** React-Leaflet with OpenStreetMap
- **Charts:** Apache ECharts
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **Icons:** Lucide React

## Running the Frontend

### Using Docker

```bash
# Build and run with docker-compose
docker-compose up -d frontend
```

The frontend will be available at http://localhost:3000

### Locally (Development)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Building for Production

```bash
cd frontend
npm run build
npm start
```

## Key Components

### Dashboard (page.tsx)

The main dashboard page that displays:

- **Header** - Application title and connection status
- **Stats Cards** - Active animals, average temperature, activity, alerts
- **Map View** - Interactive map with animal markers
- **Health Chart** - Temperature and activity visualization
- **Alert Table** - Geofence breach alerts

### MapView Component

The interactive map component using React-Leaflet:

**Features:**
- Displays paddocks as GeoJSON polygons
- Shows animal positions as markers
- Updates in real-time via WebSocket
- Click markers for animal details

**Props:**
- No props required (uses Zustand store)

**Key Functions:**
- `parseWKTToCoords()` - Converts WKT geometry to Leaflet coordinates
- `PaddocksLayer` - Renders paddock polygons
- `AnimalMarkers` - Renders animal position markers
- `MapUpdater` - Centers map on average animal position

### AnimalHealthChart Component

ECharts-based chart showing:

- Temperature trends over time
- Activity level trends
- Selectable belt IDs

### AlertTable Component

Displays geofence breach alerts:

- Belt ID that triggered alert
- Location coordinates
- Expected paddock
- Timestamp

### Telemetry Store (telemetry.ts)

Zustand store for managing telemetry state:

```typescript
interface TelemetryState {
  animalPositions: Map<string, TelemetryData>;
  telemetryHistory: Map<string, TelemetryData[]>;
  alerts: AlertData[];
  isConnected: boolean;

  // Actions
  setConnected: (connected: boolean) => void;
  updatePosition: (data: TelemetryData) => void;
  addAlert: (alert: AlertData) => void;
  clearAlerts: () => void;
}
```

## WebSocket Integration

The frontend connects to the WebSocket for real-time updates:

```typescript
// Connect to WebSocket
connectTelemetryWebSocket();

// Disconnect
disconnectTelemetryWebSocket();

// WebSocket URL
ws://localhost:8000/ws/telemetry
```

**Message Types:**

1. **Telemetry:**
```json
{
  "type": "telemetry",
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "temperature": 38.5,
  "activity_level": 5.0,
  "timestamp": 1713724800
}
```

2. **Alert:**
```json
{
  "type": "alert",
  "belt_id": "BELT-001",
  "latitude": -36.595,
  "longitude": 144.945,
  "paddock_id": "paddock-1",
  "timestamp": 1713724800
}
```

## API Integration

### Fetching Paddocks

```typescript
const paddocks = await fetchPaddocks();
// Returns GeoJSON FeatureCollection
```

### Fetching Alerts

```typescript
const alerts = await fetchAlerts();
// Returns AlertData[]
```

### Fetching Telemetry History

```typescript
const history = await fetchTelemetryHistory(beltId, hours);
// Returns TelemetryData[]
```

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Styling

The project uses Tailwind CSS with a custom theme:

- Primary color: Green (livestock theme)
- Background: Stone/cream
- Cards: White with green borders

## Adding New Components

1. Create component in `src/components/`
2. Use shadcn/ui components from `src/components/ui/`
3. Add to page in `src/app/page.tsx`
4. Use Zustand store for state management

## Troubleshooting

### Map not loading

- Check API is running at port 8000
- Verify paddocks have valid geometry
- Check browser console for errors

### WebSocket disconnected

- Check API is accessible at localhost:8000
- Verify WebSocket endpoint is working
- Check browser console for connection errors

### No data displayed

- Verify telemetry data exists in database
- Check API responses at /api/telemetry/latest
- Check worker is processing Kafka messages
