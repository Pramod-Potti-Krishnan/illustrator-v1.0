"""
Funnel Content Generator

Orchestrates LLM content generation and template assembly for funnels.
Follows the same pattern as pyramid_generator.py.
"""

import logging
import time
from typing import Dict, Any, Optional
from app.llm_services.llm_service import get_funnel_service
from app.core.funnel_validator import get_funnel_validator

logger = logging.getLogger(__name__)


class FunnelGenerator:
    """Generates funnel content using LLM and validates constraints"""

    def __init__(self):
        self.llm_service = get_funnel_service()  # Uses LLM_FUNNEL env variable
        self.validator = get_funnel_validator()

    async def generate_funnel_data(
        self,
        num_stages: int,
        topic: str,
        context: Dict[str, Any],
        target_points: Optional[list] = None,
        tone: str = "professional",
        audience: str = "general",
        validate_constraints: bool = True,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Generate funnel content data with LLM.

        Args:
            num_stages: Number of funnel stages (3-5)
            topic: Main funnel topic
            context: Additional context
            target_points: Key stage labels to include
            tone: Writing tone
            audience: Target audience
            validate_constraints: Whether to enforce character limits
            max_retries: Max retry attempts on validation failure

        Returns:
            Dict with generated content and metadata
        """
        start_time = time.time()

        # Get constraints
        constraints = self.validator.get_constraints_for_funnel(num_stages)

        # Generate content with retries
        for attempt in range(max_retries + 1):
            logger.info(f"Generating funnel content (attempt {attempt + 1}/{max_retries + 1})")

            # Call LLM
            result = await self.llm_service.generate_funnel_content(
                topic=topic,
                num_stages=num_stages,
                context=context,
                constraints=constraints,
                target_points=target_points,
                tone=tone,
                audience=audience
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
                    num_stages=num_stages
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
            num_stages=num_stages
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
_generator: FunnelGenerator = None


def get_funnel_generator() -> FunnelGenerator:
    """Get or create the global funnel generator instance"""
    global _generator

    if _generator is None:
        _generator = FunnelGenerator()

    return _generator
