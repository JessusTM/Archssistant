"""Main FastAPI server for Arch-Assistant.

This is the application entry point. Configures the FastAPI application,
registers API routers, enables CORS, mounts static files from the frontend.

Business logic and endpoints are organized in separate modules
to maintain clean, maintainable, and scalable code.

Architecture layers:
- Routes (app/api/routes.py)                : HTTP endpoints
- Orchestrator (app/services/orchestrator/) : Flow orchestration
- Elicitation Machine, Decision Maker, Recommendation Explainer: Specialized services
"""

from app.core.logging.logging import setup_logging

# Configure logging before importing routers/modules that may log at import time.
setup_logging()

import logging
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core import config
from app.api import router


logger = logging.getLogger(__name__)

app = FastAPI(
    title=config.APP_NAME,
    version="1.0.0",
    description="API for the software architecture recommendation assistant",
)


@app.exception_handler(PermissionError)
async def permission_error_handler(_: Request, exc: PermissionError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected internal error processing the message..."},
    )


logger.info(f"Initializing API: {config.APP_NAME}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware enabled for all origins")

app.include_router(router)
logger.info("API routers registered")

project_root = Path(__file__).resolve().parents[2]
frontend_dir = project_root / "archssistant-frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
logger.info(f"Static files mounted from: {frontend_dir}")
logger.info(f"API {config.APP_NAME} ready to receive requests")


if __name__ == "__main__":
    """Run the FastAPI server using uvicorn.
    
    Starts the development server with auto-reload enabled.
    """
    uvicorn.run("app.main:app", host=config.HOST, port=config.PORT, reload=True)
