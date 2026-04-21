# Welcome to Livestock Tracking Platform

The **Livestock Tracking Platform** is a real-time monitoring system for tracking cattle and other livestock using GPS-enabled smart belts. The platform provides live location tracking, temperature monitoring, activity level tracking, and geofence breach alerts.

## Key Features

- **Real-time Location Tracking** - Live GPS coordinates of all tracked animals
- **Temperature Monitoring** - Continuous temperature monitoring with alerts
- **Activity Level Tracking** - Monitor animal movement and activity patterns
- **Geofence Alerts** - Instant notifications when animals leave designated areas
- **Interactive Dashboard** - Full-featured web interface with maps and charts
- **RESTful API** - Complete REST API for integration with other systems
- **WebSocket Support** - Real-time data updates via WebSocket connections

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework for building APIs
- **PostgreSQL** - Primary relational database with PostGIS
- **TimescaleDB** - Time-series database for telemetry data
- **Kafka** - Distributed event streaming platform
- **MQTT** - Lightweight messaging for IoT devices

### Frontend
- **Next.js** - React framework with server-side rendering
- **React-Leaflet** - Interactive maps
- **ECharts** - Data visualization
- **Zustand** - State management
- **Tailwind CSS** - Utility-first CSS framework

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/livestock-tracking
cd livestock-tracking

# Start all services
make up

# View the dashboard
open http://localhost:3000
```

## Project Structure

```
livestock-tracking/
├── app/                    # Backend application
│   ├── api/               # API endpoints
│   ├── core/              # Core configurations
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   └── worker/            # Background workers
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # Pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── docker/                # Docker configurations
```

## Documentation Sections

- **[Architecture](architecture.md)** - System architecture and component overview
- **[Data Flow](data-flow.md)** - How data moves through the system
- **[Backend](backend.md)** - FastAPI backend documentation
- **[Frontend](frontend.md)** - Next.js frontend documentation
- **[Database](database.md)** - Database schema and models
- **[Deployment](deployment.md)** - Deployment guide
- **[Contributing](contributing.md)** - How to contribute

## Need Help?

- Check the [API Reference](api-reference.md) for endpoint details
- Review the [Architecture](architecture.md) for system design
- See [Contributing](contributing.md) for development setup
