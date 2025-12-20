"""
Concept Spread API Routes

FastAPI endpoints for concept-spread illustration generation.
Provides stateless API for generating hexagon-based concept spreads.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.generators.concept_spread_generator import ConceptSpreadGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/concept-spread", tags=["concept-spread"])

# Initialize generator (singleton)
generator = ConceptSpreadGenerator()


# Request/Response Models
class ConceptSpreadGenerationRequest(BaseModel):
    """Request model for concept-spread generation"""

    # REQUIRED: Core functionality
    topic: str = Field(..., min_length=1, description="Main topic for concept spread")
    num_hexagons: int = Field(6, ge=6, le=6, description="Number of hexagons (currently only 6 supported)")

    # OPTIONAL: Context & customization
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context (previous slides, etc.)")
    tone: str = Field("professional", description="Writing tone")
    audience: str = Field("general", description="Target audience")

    # OPTIONAL: Session management (for Director integration)
    presentation_id: Optional[str] = Field(None, description="Presentation identifier")
    slide_id: Optional[str] = Field(None, description="Slide identifier")
    slide_number: Optional[int] = Field(None, description="Slide position in deck")

    # OPTIONAL: Configuration
    validate_constraints: bool = Field(True, description="Enforce character limits")


class ConceptSpreadGenerationResponse(BaseModel):
    """Response model for concept-spread generation"""

    success: bool
    html: Optional[str] = None  # Complete rendered illustration
    infographic_html: Optional[str] = None  # Layout Service compatibility alias
    error: Optional[str] = None

    # Generated content (for debugging)
    generated_content: Optional[Dict[str, str]] = None

    # Validation results
    character_counts: Optional[Dict[str, Dict[str, int]]] = None
    validation: Optional[Dict[str, Any]] = None

    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    generation_time_ms: Optional[int] = None

    # Session fields (echoed from request)
    presentation_id: Optional[str] = None
    slide_id: Optional[str] = None
    slide_number: Optional[int] = None


@router.post("/generate", response_model=ConceptSpreadGenerationResponse)
async def generate_concept_spread(request: ConceptSpreadGenerationRequest):
    """
    Generate concept-spread illustration

    **Workflow**:
    1. Receive topic and configuration
    2. Generate hexagon labels, icons, and description bullets with LLM
    3. Validate against character constraints (with retry)
    4. Fill template with generated content
    5. Return complete HTML fragment

    **Example Request**:
    ```json
    {
        "topic": "Digital Transformation Strategy",
        "num_hexagons": 6,
        "presentation_id": "pres-001",
        "slide_number": 5
    }
    ```

    **Example Response**:
    ```json
    {
        "success": true,
        "html": "<div class='concept-spread-container'>...</div>",
        "generated_content": {
            "hex_1_label": "INNOVATION",
            "hex_1_icon": "💡",
            "box_1_bullet_1": "...",
            ...
        },
        "validation": {
            "valid": true,
            "violations": []
        },
        "metadata": {
            "model": "gemini-1.5-flash-002",
            "generation_time_ms": 1234,
            "attempts": 1
        },
        "presentation_id": "pres-001",
        "slide_number": 5
    }
    ```
    """
    start_time = time.time()

    try:
        logger.info(f"Received concept-spread generation request: topic='{request.topic}', num_hexagons={request.num_hexagons}")

        # Generate concept-spread
        result = await generator.generate(
            topic=request.topic,
            num_hexagons=request.num_hexagons,
            context=request.context,
            validate_constraints=request.validate_constraints
        )

        # Check for errors
        if not result["success"]:
            logger.error(f"Generation failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error"))

        # Calculate total generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = ConceptSpreadGenerationResponse(
            success=True,
            html=result["html"],
            infographic_html=result["html"],  # Layout Service compatibility alias
            generated_content=result["generated_content"],
            character_counts=result.get("character_counts"),
            validation=result.get("validation"),
            metadata=result.get("metadata"),
            generation_time_ms=generation_time_ms,
            # Echo session fields
            presentation_id=request.presentation_id,
            slide_id=request.slide_id,
            slide_number=request.slide_number
        )

        logger.info(f"Successfully generated concept-spread in {generation_time_ms}ms")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in concept-spread generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "concept-spread",
        "supported_variants": [6]
    }
