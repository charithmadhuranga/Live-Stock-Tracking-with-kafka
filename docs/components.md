# Components Documentation

This document describes the React components used in the frontend.

## UI Components

The frontend uses shadcn/ui components located in `frontend/src/components/ui/`.

### Card

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
```

**Usage:**
```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    Content here
  </CardContent>
</Card>
```

### Badge

```tsx
import { Badge } from "@/components/ui/badge";
```

**Usage:**
```tsx
<Badge variant="outline">Status</Badge>
<Badge variant="secondary">Label</Badge>
<Badge variant="destructive">Alert</Badge>
```

## Custom Components

### MapView

Interactive map component showing animal positions and paddocks.

**Location:** `frontend/src/components/MapView.tsx`

**Features:**
- Leaflet map with OpenStreetMap tiles
- Paddock polygons rendered from GeoJSON
- Animal markers with custom icons
- Popup details on marker click
- Auto-centering on animal positions

**Props:** None (uses Zustand store)

### AnimalHealthChart

ECharts component for visualizing temperature and activity data.

**Location:** `frontend/src/components/AnimalHealthChart.tsx`

**Features:**
- Line chart for temperature over time
- Line chart for activity level
- Belt ID selector
- Responsive design

**Props:** None

### AlertTable

Table displaying geofence breach alerts.

**Location:** `frontend/src/components/AlertTable.tsx`

**Features:**
- Sortable columns
- Belt ID, location, paddock, timestamp
- Responsive design

**Props:** None

## Creating New Components

### Step 1: Create Component File

```tsx
// frontend/src/components/MyComponent.tsx
"use client";

import { useState } from "react";

interface MyComponentProps {
  title: string;
}

export default function MyComponent({ title }: MyComponentProps) {
  const [count, setCount] = useState(0);

  return (
    <div>
      <h1>{title}</h1>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

### Step 2: Add to Page

```tsx
// frontend/src/app/page.tsx
import MyComponent from "@/components/MyComponent";

export default function Page() {
  return (
    <main>
      <MyComponent title="My Component" />
    </main>
  );
}
```

## State Management

### Using Zustand Store

```typescript
// frontend/src/lib/myStore.ts
import { create } from 'zustand';

interface MyStoreState {
  data: string[];
  setData: (data: string[]) => void;
}

export const useMyStore = create<MyStoreState>((set) => ({
  data: [],
  setData: (data) => set({ data }),
}));
```

### Using in Components

```tsx
import { useMyStore } from "@/lib/myStore";

function MyComponent() {
  const { data, setData } = useMyStore();
  
  return (
    <div>
      {data.map(item => <div key={item}>{item}</div>)}
    </div>
  );
}
```

## Event Handling

### WebSocket Events

```typescript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update store
  useTelemetryStore.getState().updatePosition(data);
};
```

### Form Events

```typescript
<form onSubmit={handleSubmit}>
  <input onChange={handleChange} />
  <button type="submit">Submit</button>
</form>
```

## Styling

### Tailwind CSS

```tsx
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <span className="text-green-700">Content</span>
</div>
```

### Conditional Classes

```tsx
<div className={`p-4 ${isActive ? 'bg-green-100' : 'bg-gray-100'}`}>
```
