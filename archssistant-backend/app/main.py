"""Main FastAPI server for Arch-Assistant.

This is the application entry point. Configures the FastAPI application,
registers API routers and enables CORS.

Business logic and endpoints are organized in separate modules
to maintain clean, maintainable, and scalable code.

Architecture layers:
- Routes (app/api/routes.py)                : HTTP endpoints
- Orchestrator (app/services/orchestrator/) : Flow orchestration
- Elicitation Machine, Decision Maker, Recommendation Explainer: Specialized services
"""

import logging
from app.core.logging.logging import setup_logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.core import config


setup_logging()
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
logger.info("API routers registered")
