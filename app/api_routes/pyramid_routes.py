"""
Pyramid Generation API Routes

Endpoint for LLM-powered pyramid content generation.
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.models import PyramidGenerationRequest, PyramidGenerationResponse
from app.llm_services.pyramid_generator import get_generator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/v1.0/pyramid/generate", response_model=PyramidGenerationResponse)
async def generate_pyramid_with_llm(request: PyramidGenerationRequest):
    """
    Generate pyramid illustration using LLM for content generation.

    Workflow:
    1. Validate pyramid level count (3-6)
    2. Call Gemini to generate level content with character constraints
    3. Validate character counts
    4. Fill pyramid HTML template with generated content
    5. Apply theme and size
    6. Return complete pyramid HTML

    Args:
        request: PyramidGenerationRequest with topic, context, and preferences

    Returns:
        PyramidGenerationResponse with complete pyramid HTML and metadata
    """
    start_time = time.time()

    try:
        logger.info(
            f"Generating {request.num_levels}-level pyramid: '{request.topic}'"
        )

        # Get generator
        generator = get_generator()

        # ALWAYS generate overview for 3 and 4 level pyramids
        generate_overview = request.num_levels in [3, 4]

        # Generate pyramid content with LLM
        gen_result = await generator.generate_pyramid_data(
            num_levels=request.num_levels,
            topic=request.topic,
            context=request.context,
            target_points=request.target_points,
            tone=request.tone,
            audience=request.audience,
            validate_constraints=request.validate_constraints,
            generate_overview=generate_overview  # Auto-set based on num_levels
        )

        if not gen_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {gen_result.get('error')}"
            )

        generated_content = gen_result["content"]

        # Determine template file
        template_file = f"{request.num_levels}.html"

        # Load template directly (not using TemplateService)
        template_path = Path(__file__).parent.parent.parent / "templates" / "pyramid" / template_file

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

        # LOG: Debug what we're filling (v1.0.1 - bullet-based)
        logger.info(f"Filling template with {len(generated_content)} fields")
        logger.info(f"Generated content keys: {sorted(generated_content.keys())}")

        for key, value in generated_content.items():
            placeholder = f"{{{key}}}"
            # Count how many times this placeholder appears
            count = template_html.count(placeholder)
            if count > 0:
                logger.info(f"Replacing {placeholder} ({count} occurrences) with: {value[:50]}...")
            filled_html = filled_html.replace(placeholder, value)

        # Remove any remaining placeholders (e.g., overview fields when not requested)
        import re
        filled_html = re.sub(r'\{overview_heading\}', '', filled_html)
        filled_html = re.sub(r'\{overview_text\}', '', filled_html)

        # LOG: Check for any remaining placeholders
        remaining = re.findall(r'\{[^}]+\}', filled_html)
        if remaining:
            logger.warning(f"Remaining unfilled placeholders: {remaining[:10]}")

        # Calculate total generation time
        total_time = int((time.time() - start_time) * 1000)

        # Build response
        response = PyramidGenerationResponse(
            success=True,
            html=filled_html,
            metadata={
                "num_levels": request.num_levels,
                "template_file": template_file,
                "theme": request.theme,
                "size": request.size,
                "topic": request.topic,
                "code_version": "v1.0.1-bullets",  # Version marker to confirm new code
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
            f"✅ Successfully generated {request.num_levels}-level pyramid "
            f"in {total_time}ms"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating pyramid: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
