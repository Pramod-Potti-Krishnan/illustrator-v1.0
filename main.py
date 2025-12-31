#!/usr/bin/env python3
"""
Illustrator Service v1.0 - Main Application Entry Point

Simple FastAPI service that loads HTML+CSS templates, fills them with data,
applies theme colors, and returns HTML or PNG.

Run with:
    uvicorn main:app --reload --port 8000

Or:
    python3 main.py
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.routes import router
from app.api_routes.pyramid_routes import router as pyramid_router
from app.api_routes.funnel_routes import router as funnel_router
from app.api_routes.concentric_circles_routes import router as concentric_circles_router
from app.api_routes.concept_spread_routes import router as concept_spread_router
from app.api_routes.layout_service_routes import router as layout_service_router
# Director Integration endpoints (Phase 1-3)
from app.api_routes.capabilities_routes import router as capabilities_router
from app.api_routes.can_handle_routes import router as can_handle_router
from app.api_routes.recommend_routes import router as recommend_router
from app.api_routes.star_diagram_routes import router as star_diagram_router

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Illustrator Service v1.0",
    description="Pre-built, human-validated templates for professional PowerPoint illustrations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(pyramid_router)
app.include_router(funnel_router)
app.include_router(concentric_circles_router)
app.include_router(concept_spread_router)
app.include_router(layout_service_router)  # Layout Service integration
# Director Integration endpoints (Phase 1-3)
app.include_router(capabilities_router)    # GET /capabilities
app.include_router(can_handle_router)      # POST /v1.0/can-handle
app.include_router(recommend_router)
app.include_router(star_diagram_router)       # POST /v1.0/recommend-visual


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Illustrator Service",
        "version": "1.1.0",
        "architecture": "Template-based + Dynamic SVG generation",
        "endpoints": {
            # Director Integration (Phase 1-3)
            "capabilities": "GET /capabilities (Director coordination)",
            "can_handle": "POST /v1.0/can-handle (Director coordination)",
            "recommend_visual": "POST /v1.0/recommend-visual (Director coordination)",
            # Layout Service Integration
            "layout_service_generate": "POST /api/ai/illustrator/generate (Layout Service)",
            "layout_service_types": "GET /api/ai/illustrator/types",
            "layout_service_type_details": "GET /api/ai/illustrator/types/{type}",
            # Visual Generation endpoints
            "generate": "POST /v1.0/generate",
            "pyramid_generate": "POST /v1.0/pyramid/generate (LLM-powered)",
            "funnel_generate": "POST /v1.0/funnel/generate (LLM-powered)",
            "concentric_circles_generate": "POST /v1.0/concentric_circles/generate (LLM-powered)",
            "concept_spread_generate": "POST /concept-spread/generate (LLM-powered)",
            "list_illustrations": "GET /v1.0/illustrations",
            "illustration_details": "GET /v1.0/illustration/{type}",
            "list_themes": "GET /v1.0/themes",
            "list_sizes": "GET /v1.0/sizes",
            "health_check": "GET /health"
        },
        "features": {
            "template_based_generation": True,
            "dynamic_svg_generation": True,
            "html_css_rendering": True,
            "png_conversion": False,
            "theme_support": 4,
            "size_presets": 3,
            "infographic_types": 14,
            "director_integration": True
        },
        "phase": "Phase 3 - Director Integration"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if templates directory exists
        templates_dir = Path(__file__).parent / "templates"
        templates_exist = templates_dir.exists()

        return {
            "status": "healthy",
            "version": "1.0.0",
            "templates_directory": str(templates_dir),
            "templates_exist": templates_exist,
            "phase": "Phase 1 - Infrastructure Setup"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    # Railway sets PORT, fallback to API_PORT or 8000
    port = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    # Default to false for production (Railway), set API_RELOAD=true for local dev
    reload = os.getenv("API_RELOAD", "false").lower() == "true"

    logger.info("=" * 80)
    logger.info("Illustrator Service v1.0 - Starting Up")
    logger.info("=" * 80)
    logger.info(f"Starting server at {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
