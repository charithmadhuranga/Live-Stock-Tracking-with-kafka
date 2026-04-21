# Contributing Guide

Thank you for your interest in contributing to the Livestock Tracking Platform! This guide will help you get started.

## Getting Started

### Prerequisites

- **Python 3.11+** - Backend development
- **Node.js 20+** - Frontend development
- **Docker & Docker Compose** - Running services
- **Git** - Version control

### Setup Development Environment

1. **Fork the repository**

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/livestock-tracking
   cd livestock-tracking
   ```

3. **Start the services**
   ```bash
   make up
   ```

4. **Verify services are running**
   ```bash
   docker-compose ps
   ```

## Project Structure

```
livestock-tracking/
├── app/                    # Backend (Python/FastAPI)
│   ├── api/               # API endpoints
│   ├── core/              # Config & database
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   └── worker/            # Background workers
├── frontend/              # Frontend (Next.js)
│   ├── src/
│   │   ├── app/          # Pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   └── package.json
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── docker/                # Docker configs
├── Makefile              # Build commands
└── docker-compose.yml    # Container orchestration
```

## Making Changes

### Backend Changes

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make your changes**
   - Follow existing code style
   - Add type hints
   - Write docstrings for new functions

4. **Test locally**
   ```bash
   # Run the API
   python -m uvicorn app.main:app --reload --port 8000
   ```

### Frontend Changes

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Make your changes**
   - Follow React best practices
   - Use TypeScript
   - Follow existing component patterns

3. **Test locally**
   ```bash
   npm run dev
   ```

### Database Changes

If you modify models:

1. **Generate migration**
   ```bash
   # Not implemented yet - manual SQL required
   ```

2. **Update database directly**
   ```bash
   docker exec -it livestock-postgres psql -U livestock -d livestock_db
   ```

## Code Style

### Python

- Follow **PEP 8**
- Use **type hints**
- Use **Black** for formatting
- Use **isort** for imports

```bash
pip install black isort
black .
isort .
```

### TypeScript/JavaScript

- Use **ESLint** and **Prettier**
- Follow **Airbnb** style guide

```bash
cd frontend
npm run lint
```

## Testing

### Backend Tests

```bash
# Not implemented yet
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Submitting Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make commits**
   ```bash
   git add .
   git commit -m "Add your feature"
   ```

3. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request**

## Common Tasks

### Add a New API Endpoint

1. Create or modify endpoint in `app/api/telemetry.py`
2. Add Pydantic schema in `app/schemas/__init__.py`
3. Test endpoint at http://localhost:8000/docs

### Add a New Component

1. Create component in `frontend/src/components/`
2. Import in `frontend/src/app/page.tsx`
3. Use existing UI components from `frontend/src/components/ui/`

### Add a New Database Model

1. Add model in `app/models/__init__.py`
2. Create table manually or via migration
3. Add schema in `app/schemas/__init__.py`

## Debugging

### Backend Debugging

```python
# Add logging
import logging
logger = logging.getLogger(__name__)
logger.info("Your message")
```

### Frontend Debugging

```typescript
// Add console logs
console.log('Your message', data);

// Use React DevTools
```

### Docker Debugging

```bash
# View logs
docker-compose logs -f api

# Enter container
docker exec -it livestock-api sh

# Check environment
docker-compose exec api env
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [React-Leaflet Documentation](https://react-leaflet.js.org/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)

## Questions?

- Open an issue for bugs or feature requests
- Join the discussion in GitHub Discussions
- Check existing issues before creating new ones
