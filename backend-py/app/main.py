import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, bedrock, agent, test, agent_dispatch

logging.basicConfig(level=logging.INFO)
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(bedrock.router)
app.include_router(agent.router)
app.include_router(test.router)
app.include_router(agent_dispatch.router)
