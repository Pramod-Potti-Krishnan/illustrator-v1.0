"""
Pyramid Content Generator

Orchestrates LLM content generation and template assembly for pyramids.
"""

import logging
import time
from typing import Dict, Any, Optional
from app.llm_services.llm_service import get_gemini_service
from app.core.pyramid_validator import get_validator

logger = logging.getLogger(__name__)


class PyramidGenerator:
    """Generates pyramid content using LLM and validates constraints"""

    def __init__(self):
        self.llm_service = get_gemini_service()
        self.validator = get_validator()

    async def generate_pyramid_data(
        self,
        num_levels: int,
        topic: str,
        context: Dict[str, Any],
        target_points: Optional[list] = None,
        tone: str = "professional",
        audience: str = "general",
        validate_constraints: bool = True,
        generate_overview: bool = False,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Generate pyramid content data with LLM.

        Args:
            num_levels: Number of pyramid levels (3-6)
            topic: Main pyramid topic
            context: Additional context
            target_points: Key points to include
            tone: Writing tone
            audience: Target audience
            validate_constraints: Whether to enforce character limits
            generate_overview: Whether to generate overview section (3 & 4 levels only)
            max_retries: Max retry attempts on validation failure

        Returns:
            Dict with generated content and metadata
        """
        start_time = time.time()

        # Get constraints
        constraints = self.validator.get_constraints_for_pyramid(num_levels)

        # Generate content with retries
        for attempt in range(max_retries + 1):
            logger.info(f"Generating pyramid content (attempt {attempt + 1}/{max_retries + 1})")

            # Call LLM
            result = await self.llm_service.generate_pyramid_content(
                topic=topic,
                num_levels=num_levels,
                context=context,
                constraints=constraints,
                target_points=target_points,
                tone=tone,
                audience=audience,
                generate_overview=generate_overview
            )

            if not result["success"]:
                return {
                    "success": False,
                    "error": result.get("error", "LLM generation failed")
                }

            generated_content = result["content"]

            # Validate if required
            if validate_constraints:
                is_valid, violations = self.validator.validate_content(
                    content=generated_content,
                    num_levels=num_levels
                )

                if is_valid:
                    logger.info("✅ Content validation passed")
                    break
                else:
                    logger.warning(
                        f"❌ Validation failed (attempt {attempt + 1}): "
                        f"{len(violations)} violations"
                    )
                    if attempt < max_retries:
                        logger.info("Retrying generation...")
                        continue
                    else:
                        logger.error("Max retries reached, returning with violations")
            else:
                is_valid = True
                violations = []
                break

        # Get character counts
        character_counts = self.validator.get_character_counts(
            content=generated_content,
            num_levels=num_levels
        )

        generation_time = int((time.time() - start_time) * 1000)

        return {
            "success": True,
            "content": generated_content,
            "character_counts": character_counts,
            "validation": {
                "valid": is_valid,
                "violations": violations
            },
            "metadata": {
                "generation_time_ms": generation_time,
                "attempts": attempt + 1,
                "model": result.get("model"),
                "usage": result.get("usage_metadata", {})
            }
        }


# Global generator instance
_generator: PyramidGenerator = None


def get_generator() -> PyramidGenerator:
    """Get or create the global generator instance"""
    global _generator

    if _generator is None:
        _generator = PyramidGenerator()

    return _generator
