"""
Layout Service Integration Routes

Unified endpoint for generating infographics from the Layout Service orchestrator.
Supports 14 infographic types with dual output mode (HTML templates + dynamic SVG).
"""

import time
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException

from app.models.layout_service_request import InfographicGenerateRequest, InfographicType
from app.models.layout_service_response import (
    InfographicGenerateResponse,
    ResponseData,
    RenderedOutput,
    InfographicMetadata,
    InfographicData,
    EditInfo,
    ErrorResponse,
    InfographicItem,
)
from app.core.type_router import get_router
from app.core.type_constraints import (
    INFOGRAPHIC_TYPE_CONSTRAINTS,
    list_all_types,
    get_template_types,
    get_svg_types,
    GRID_UNIT_PIXELS,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/illustrator", tags=["layout-service"])


@router.post("/generate", response_model=InfographicGenerateResponse)
async def generate_infographic(request: InfographicGenerateRequest) -> InfographicGenerateResponse:
    """
    Generate an infographic for the Layout Service.

    This unified endpoint supports 14 infographic types:

    **Template-based (HTML):** pyramid, funnel, concentric_circles, concept_spread, venn, comparison

    **Dynamic SVG (Gemini 2.5 Pro):** timeline, process, statistics, hierarchy, list, cycle, matrix, roadmap

    The endpoint automatically routes to the appropriate generator based on type.

    Args:
        request: InfographicGenerateRequest with prompt, type, constraints, and options

    Returns:
        InfographicGenerateResponse with rendered SVG/HTML and structured data
    """
    start_time = time.time()

    try:
        logger.info(
            f"Generating infographic: type={request.type.value}, "
            f"grid={request.constraints.gridWidth}x{request.constraints.gridHeight}, "
            f"prompt='{request.prompt[:50]}...'"
        )

        # Get router and validate request
        type_router = get_router()
        is_valid, error = type_router.validate_request(request)

        if not is_valid:
            logger.warning(f"Request validation failed: {error}")
            return InfographicGenerateResponse(
                success=False,
                error=ErrorResponse(
                    code="CONSTRAINT_VIOLATION",
                    message=error,
                    retryable=False,
                    suggestion="Check the grid constraints for this infographic type"
                ),
                presentationId=request.presentationId,
                slideId=request.slideId,
                elementId=request.elementId,
                generationTimeMs=int((time.time() - start_time) * 1000)
            )

        # Get generator for this type
        generator = type_router.get_generator(request.type)

        # Generate
        result = await generator.generate(request)

        # Calculate timing
        generation_time_ms = int((time.time() - start_time) * 1000)

        if not result.success:
            logger.error(f"Generation failed: {result.error}")
            return InfographicGenerateResponse(
                success=False,
                error=ErrorResponse(
                    code=result.error_code or "GENERATION_FAILED",
                    message=result.error,
                    retryable=result.retryable
                ),
                presentationId=request.presentationId,
                slideId=request.slideId,
                elementId=request.elementId,
                generationTimeMs=generation_time_ms
            )

        # Build response data
        width_px, height_px = generator.calculate_dimensions(
            request.constraints.gridWidth,
            request.constraints.gridHeight
        )

        colors = result.metadata.get("colors", []) if result.metadata else []

        response_data = generator.build_response_data(
            generation_id=generator.generate_id(),
            svg_content=result.svg,
            html_content=result.html,
            items=result.items or [],
            width_px=width_px,
            height_px=height_px,
            color_palette=colors,
            icons_used=result.metadata.get("icons_used") if result.metadata else None
        )

        logger.info(
            f"Successfully generated {request.type.value} infographic "
            f"in {generation_time_ms}ms"
        )

        return InfographicGenerateResponse(
            success=True,
            data=response_data,
            presentationId=request.presentationId,
            slideId=request.slideId,
            elementId=request.elementId,
            generationTimeMs=generation_time_ms
        )

    except ValueError as e:
        logger.error(f"Value error: {e}")
        return InfographicGenerateResponse(
            success=False,
            error=ErrorResponse(
                code="INVALID_REQUEST",
                message=str(e),
                retryable=False
            ),
            presentationId=request.presentationId,
            slideId=request.slideId,
            elementId=request.elementId,
            generationTimeMs=int((time.time() - start_time) * 1000)
        )

    except Exception as e:
        logger.exception(f"Unexpected error generating infographic: {e}")
        return InfographicGenerateResponse(
            success=False,
            error=ErrorResponse(
                code="INTERNAL_ERROR",
                message=f"Unexpected error: {str(e)}",
                retryable=True
            ),
            presentationId=request.presentationId,
            slideId=request.slideId,
            elementId=request.elementId,
            generationTimeMs=int((time.time() - start_time) * 1000)
        )


@router.get("/types")
async def list_infographic_types():
    """
    List all supported infographic types with their constraints.

    Returns constraints including:
    - Minimum and maximum grid sizes
    - Aspect ratio requirements
    - Output mode (html or svg)
    - Item limits (min, max, default)
    """
    return {
        "total_types": len(INFOGRAPHIC_TYPE_CONSTRAINTS),
        "template_types": get_template_types(),
        "svg_types": get_svg_types(),
        "grid_unit_pixels": GRID_UNIT_PIXELS,
        "types": list_all_types()
    }


@router.get("/types/{infographic_type}")
async def get_type_details(infographic_type: str):
    """
    Get detailed constraints for a specific infographic type.

    Args:
        infographic_type: The type to get details for

    Returns:
        Detailed constraint information
    """
    if infographic_type not in INFOGRAPHIC_TYPE_CONSTRAINTS:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "TYPE_NOT_FOUND",
                "message": f"Unknown infographic type: {infographic_type}",
                "available_types": list(INFOGRAPHIC_TYPE_CONSTRAINTS.keys())
            }
        )

    constraint = INFOGRAPHIC_TYPE_CONSTRAINTS[infographic_type]

    return {
        "type": infographic_type,
        "description": constraint.description,
        "grid_constraints": {
            "min_width": constraint.min_grid_width,
            "min_height": constraint.min_grid_height,
            "max_width": constraint.max_grid_width,
            "max_height": constraint.max_grid_height,
            "min_pixels": {
                "width": constraint.min_grid_width * GRID_UNIT_PIXELS,
                "height": constraint.min_grid_height * GRID_UNIT_PIXELS
            },
            "max_pixels": {
                "width": constraint.max_grid_width * GRID_UNIT_PIXELS,
                "height": constraint.max_grid_height * GRID_UNIT_PIXELS
            }
        },
        "aspect_ratio": {
            "type": constraint.aspect_ratio_type.value,
            "value": f"{constraint.aspect_ratio_value[0]}:{constraint.aspect_ratio_value[1]}" if constraint.aspect_ratio_value else "flexible"
        },
        "output_mode": constraint.output_mode.value,
        "item_limits": {
            "min": constraint.min_items,
            "max": constraint.max_items,
            "default": constraint.default_items
        }
    }


@router.get("/health")
async def health_check():
    """
    Health check for the Layout Service integration endpoint.
    """
    return {
        "status": "healthy",
        "endpoint": "/api/ai/illustrator/generate",
        "supported_types": len(INFOGRAPHIC_TYPE_CONSTRAINTS),
        "template_types": len(get_template_types()),
        "svg_types": len(get_svg_types())
    }
