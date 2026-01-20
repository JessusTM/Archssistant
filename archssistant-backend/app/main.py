"""Main FastAPI server for Arch-Assistant.

This is the application entry point. Configures the FastAPI application,
registers API routers, enables CORS, mounts static files from the frontend.

Business logic and endpoints are organized in separate modules
to maintain clean, maintainable, and scalable code.

Architecture layers:
- Routes (app/api/routes.py): HTTP endpoints
- Orchestrator (app/services/orchestrator/): Flow orchestration
- Elicitation Machine, Decision Maker, Recommendation Explainer: Specialized services
"""

from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core import config, get_logger
from app.api import router


logger = get_logger(__name__)

app = FastAPI(
    title       = config.APP_NAME,
    version     = '1.0.0',
    description = 'API for the software architecture recommendation assistant'
)

logger.info(f"Initializing API: {config.APP_NAME}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins       = ['*'],
    allow_credentials   = True,
    allow_methods       = ['*'],
    allow_headers       = ['*'],
)
logger.info("CORS middleware enabled for all origins")

# Register routers
app.include_router(router)
logger.info("API routers registered")

# Mount static frontend
project_root = Path(__file__).resolve().parents[2]
frontend_dir = project_root / 'archssistant-frontend'
app.mount(
    '/',
    StaticFiles(directory=frontend_dir, html=True),
    name='static'
)
logger.info(f"Static files mounted from: {frontend_dir}")
logger.info(f"API {config.APP_NAME} ready to receive requests")


if __name__ == "__main__":
    """Run the FastAPI server using uvicorn."""
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True  # Auto-reload on code changes (development)
    )