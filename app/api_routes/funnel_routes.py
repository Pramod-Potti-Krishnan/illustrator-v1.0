"""
Funnel Generation API Routes

Endpoint for LLM-powered funnel content generation.
Follows the same pattern as pyramid_routes.py.
"""

import logging
import time
import re
from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.models import FunnelGenerationRequest, FunnelGenerationResponse
from app.llm_services.funnel_generator import get_funnel_generator
from app.core.text_utils import to_title_case

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/v1.0/funnel/generate", response_model=FunnelGenerationResponse)
async def generate_funnel_with_llm(request: FunnelGenerationRequest):
    """
    Generate funnel illustration using LLM for content generation.

    Workflow:
    1. Validate funnel stage count (3-5)
    2. Call Gemini to generate stage content with character constraints
    3. Validate character counts
    4. Fill funnel HTML template with generated content
    5. Apply theme and size
    6. Return complete funnel HTML

    Args:
        request: FunnelGenerationRequest with topic, context, and preferences

    Returns:
        FunnelGenerationResponse with complete funnel HTML and metadata
    """
    start_time = time.time()

    try:
        logger.info(
            f"Generating {request.num_stages}-stage funnel: '{request.topic}'"
        )

        # Get generator
        generator = get_funnel_generator()

        # Generate funnel content with LLM
        gen_result = await generator.generate_funnel_data(
            num_stages=request.num_stages,
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

        # Apply title case to stage names (convert from ALL CAPS to Title Case)
        for stage in range(1, request.num_stages + 1):
            name_key = f"stage_{stage}_name"
            if name_key in generated_content:
                generated_content[name_key] = to_title_case(generated_content[name_key])

        # Determine template file
        template_file = f"{request.num_stages}.html"

        # Load template directly (not using TemplateService)
        template_path = Path(__file__).parent.parent.parent / "templates" / "funnel" / template_file

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
        # In case any stage placeholders weren't filled
        for stage_num in range(1, 6):
            filled_html = re.sub(rf'\{{stage_{stage_num}_name\}}', '', filled_html)
            for bullet_num in range(1, 4):
                filled_html = re.sub(rf'\{{stage_{stage_num}_bullet_{bullet_num}\}}', '', filled_html)

        # Calculate total generation time
        total_time = int((time.time() - start_time) * 1000)

        # Build response
        response = FunnelGenerationResponse(
            success=True,
            html=filled_html,
            infographic_html=filled_html,  # Layout Service compatibility alias
            metadata={
                "num_stages": request.num_stages,
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
            f"✅ Successfully generated {request.num_stages}-stage funnel "
            f"in {total_time}ms"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating funnel: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
