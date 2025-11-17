"""
Concentric Circles Generation API Routes

Endpoint for LLM-powered concentric circles content generation.
Follows the same pattern as pyramid_routes.py and funnel_routes.py.
"""

import logging
import time
import re
from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.models import ConcentricCirclesGenerationRequest, ConcentricCirclesGenerationResponse
from app.llm_services.concentric_circles_generator import get_concentric_circles_generator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/v1.0/concentric_circles/generate", response_model=ConcentricCirclesGenerationResponse)
async def generate_concentric_circles_with_llm(request: ConcentricCirclesGenerationRequest):
    """
    Generate concentric circles illustration using LLM for content generation.

    Workflow:
    1. Validate circle count (3-5)
    2. Call Gemini to generate circle labels and legend bullets with character constraints
    3. Validate character counts
    4. Fill concentric circles HTML template with generated content
    5. Apply theme and size
    6. Return complete concentric circles HTML

    Args:
        request: ConcentricCirclesGenerationRequest with topic, context, and preferences

    Returns:
        ConcentricCirclesGenerationResponse with complete concentric circles HTML and metadata
    """
    start_time = time.time()

    try:
        logger.info(
            f"Generating {request.num_circles}-circle concentric circles: '{request.topic}'"
        )

        # Get generator
        generator = get_concentric_circles_generator()

        # Generate concentric circles content with LLM
        gen_result = await generator.generate_concentric_circles_data(
            num_circles=request.num_circles,
            topic=request.topic,
            context=request.context,
            target_points=request.target_points,
            tone=request.tone,
            audience=request.audience,
            validate_constraints=request.validate_constraints
        )

        if not gen_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {gen_result.get('error')}"
            )

        generated_content = gen_result["content"]

        # Determine template file
        template_file = f"{request.num_circles}.html"

        # Load template directly (not using TemplateService)
        template_path = Path(__file__).parent.parent.parent / "templates" / "concentric_circles" / template_file

        try:
            with open(template_path, 'r') as f:
                template_html = f.read()
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Template not found: {template_path}"
            )

        # Fill template with generated content
        filled_html = template_html
        for key, value in generated_content.items():
            placeholder = f"{{{key}}}"
            filled_html = filled_html.replace(placeholder, value)

        # Remove any remaining placeholders (defensive cleanup)
        # Bullets per legend: {3: 5, 4: 4, 5: 3}
        bullets_per_legend = {3: 5, 4: 4, 5: 3}
        num_bullets = bullets_per_legend.get(request.num_circles, 3)

        for circle_num in range(1, 6):
            filled_html = re.sub(rf'\{{circle_{circle_num}_label\}}', '', filled_html)
            for legend_num in range(1, 6):
                for bullet_num in range(1, 6):
                    filled_html = re.sub(rf'\{{legend_{legend_num}_bullet_{bullet_num}\}}', '', filled_html)

        # Calculate total generation time
        total_time = int((time.time() - start_time) * 1000)

        # Build response
        response = ConcentricCirclesGenerationResponse(
            success=True,
            html=filled_html,
            metadata={
                "num_circles": request.num_circles,
                "template_file": template_file,
                "theme": request.theme,
                "size": request.size,
                "topic": request.topic,
                **gen_result.get("metadata", {})
            },
            generated_content=generated_content,
            character_counts=gen_result["character_counts"],
            validation=gen_result["validation"],
            generation_time_ms=total_time,
            # Echo session context (aligns with Text Service v1.2)
            presentation_id=request.presentation_id,
            slide_id=request.slide_id,
            slide_number=request.slide_number
        )

        logger.info(
            f"✅ Successfully generated {request.num_circles}-circle concentric circles "
            f"in {total_time}ms"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Concentric circles generation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
