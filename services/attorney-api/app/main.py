from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.core.config import get_settings
from app.core.database import build_session_factory
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.sessions=build_session_factory(get_settings().database_url)
    yield
app=FastAPI(title="Attorney API",version="0.1.0",lifespan=lifespan)
app.include_router(router)