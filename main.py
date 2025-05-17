from fastapi import FastAPI
from contextlib import asynccontextmanager
from app import database
from app.routers import routers
from app.middlewares.limiters import add_limiters
from app.middlewares.exception_handlers import add_exception_handlers
from app.middlewares.cors import apply_cors
from config.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    add_exception_handlers(app)

    # INIT DATABASE
    await database.initialize()

    # ADD ROUTES
    for router in routers:
        app.include_router(**router)
    yield

app = FastAPI(title="NetworkAttackClassificationAPI", lifespan=lifespan)    
apply_cors(app, origins=settings.allowed_origins.split(","))
add_limiters(app)
add_exception_handlers(app)