"""
API routes for Illustrator Service v1.0
"""

import time
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException

from .models import IllustrationRequest, IllustrationResponse
from .services import TemplateService
from .themes import list_themes
from .sizes import list_sizes

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v1.0", tags=["illustrations"])

# Initialize template service
templates_dir = Path(__file__).parent.parent / "templates"
template_service = TemplateService(templates_dir=templates_dir)


@router.post("/generate", response_model=IllustrationResponse)
async def generate_illustration(request: IllustrationRequest):
    """
    Generate an illustration from a template

    This endpoint:
    1. Loads a pre-built HTML+CSS template
    2. Fills it with your data
    3. Applies theme colors
    4. Returns HTML (or converts to PNG if requested)

    Note: Only approved illustration types are supported (pyramid, funnel).
    Archived templates are not accessible via this endpoint.
    """
    start_time = time.time()

    # Define allowed illustration types (approved only)
    ALLOWED_TYPES = ["pyramid", "pyramid_3tier", "funnel", "funnel_4stage"]

    # Validate illustration type is not archived
    if request.illustration_type not in ALLOWED_TYPES:
        logger.warning(f"Attempted to generate archived type: {request.illustration_type}")
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "archived_template",
                "message": f"Illustration type '{request.illustration_type}' is archived and no longer supported",
                "suggestions": [
                    "Use GET /v1.0/illustrations to see currently supported types",
                    "Currently supported: pyramid (approved), funnel (work in progress)"
                ]
            }
        )

    try:
        # Generate HTML
        html = template_service.generate(
            illustration_type=request.illustration_type,
            variant_id=request.variant_id,
            data=request.data,
            theme_name=request.theme,
            size_name=request.size
        )

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Get size for metadata
        from .sizes import get_size
        size = get_size(request.size)

        # Prepare response
        response = IllustrationResponse(
            illustration_type=request.illustration_type,
            variant_id=request.variant_id,
            format="html",  # PNG conversion in future phase
            data=html,
            metadata={
                "width": size.width,
                "height": size.height,
                "theme": request.theme,
                "rendering_method": "html_css"  # Will be "svg" for SVG templates
            },
            generation_time_ms=generation_time_ms
        )

        logger.info(
            f"Generated {request.illustration_type}/{request.variant_id} "
            f"in {generation_time_ms}ms"
        )

        return response

    except FileNotFoundError as e:
        logger.error(f"Template not found: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "template_not_found",
                "message": str(e),
                "suggestions": [
                    f"Check that illustration_type '{request.illustration_type}' exists",
                    f"Check that variant_id '{request.variant_id}' exists",
                    "Use GET /v1.0/illustrations to see available types"
                ]
            }
        )

    except KeyError as e:
        logger.error(f"Invalid theme or size: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "validation_error",
                "message": str(e),
                "suggestions": [
                    "Use GET /v1.0/themes to see available themes",
                    "Use GET /v1.0/sizes to see available sizes"
                ]
            }
        )

    except ValueError as e:
        logger.error(f"Data validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error_type": "validation_error",
                "message": str(e),
                "suggestions": [
                    f"Check data structure for {request.illustration_type}",
                    f"Use GET /v1.0/illustration/{request.illustration_type} for schema"
                ]
            }
        )

    except Exception as e:
        logger.exception("Unexpected error during generation")
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "generation_error",
                "message": f"Unexpected error: {str(e)}"
            }
        )


@router.get("/illustrations")
async def list_illustrations():
    """
    List all available illustration types and their variants

    Returns information about which templates are currently available
    """
    templates = template_service.list_available_templates()

    return {
        "total_templates": len(templates),
        "illustrations": templates
    }


@router.get("/illustration/{illustration_type}")
async def get_illustration_details(illustration_type: str):
    """
    Get details about a specific illustration type

    Returns available variants and basic information
    """
    templates = template_service.list_available_templates()

    # Find matching template
    for template in templates:
        if template["illustration_type"] == illustration_type:
            return {
                "illustration_type": illustration_type,
                "variants": template["variants"],
                "supported_themes": list(["professional", "bold", "minimal", "playful"]),
                "supported_sizes": list(["small", "medium", "large"])
            }

    # Not found
    raise HTTPException(
        status_code=404,
        detail={
            "error_type": "not_found",
            "message": f"Illustration type '{illustration_type}' not found",
            "suggestions": [
                "Use GET /v1.0/illustrations to see available types"
            ]
        }
    )


@router.get("/themes")
async def get_themes():
    """
    List all available color themes

    Returns all 4 predefined themes with their color palettes
    """
    return {
        "total_themes": 4,
        "themes": list_themes()
    }


@router.get("/sizes")
async def get_sizes():
    """
    List all available size presets

    Returns all 3 predefined sizes
    """
    return {
        "total_sizes": 3,
        "sizes": list_sizes()
    }
