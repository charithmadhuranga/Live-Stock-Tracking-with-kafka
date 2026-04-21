from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, timescale_engine, init_db
from app.models import Base
from app.api import telemetry, websocket, alerts, broadcast


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    from app.models import Paddock, Animal
    Base.metadata.create_all(bind=engine, tables=[Paddock.__table__, Animal.__table__])
    from app.models import Telemetry
    Base.metadata.create_all(bind=timescale_engine, tables=[Telemetry.__table__])
    yield

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry.router)
app.include_router(websocket.router)
app.include_router(alerts.router)
app.include_router(broadcast.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
