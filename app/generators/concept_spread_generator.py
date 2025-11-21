"""
Concept Spread Generator

Orchestrates concept-spread illustration generation:
1. Load template and constraints
2. Generate content with LLM
3. Validate constraints (with retry logic)
4. Fill template with generated content
5. Return complete HTML
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

from app.llm_services.concept_spread_service import ConceptSpreadService
from app.validators.constraint_validator import ConstraintValidator

logger = logging.getLogger(__name__)


class ConceptSpreadGenerator:
    """Generator for concept-spread illustrations"""

    def __init__(self):
        """Initialize generator with LLM service and validator"""
        self.llm_service = ConceptSpreadService()
        self.validator = ConstraintValidator()

        # Load templates
        self.templates_dir = Path(__file__).parent.parent.parent / "templates" / "concept_spread"
        self.templates = self._load_templates()

        # Load constraints
        self.constraints_path = Path(__file__).parent.parent / "variant_specs" / "concept_spread_constraints.json"
        self.constraints = self._load_constraints()

        logger.info("Initialized ConceptSpreadGenerator")

    def _load_templates(self) -> Dict[str, str]:
        """Load all concept-spread templates"""
        templates = {}
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*.html"):
                variant_name = template_file.stem  # e.g., "6"
                templates[variant_name] = template_file.read_text()
                logger.info(f"Loaded concept-spread template: {variant_name}")
        return templates

    def _load_constraints(self) -> Dict[str, Any]:
        """Load constraints JSON"""
        if self.constraints_path.exists():
            with open(self.constraints_path, 'r') as f:
                constraints = json.load(f)
                logger.info(f"Loaded concept-spread constraints: {list(constraints.keys())}")
                return constraints
        return {}

    async def generate(
        self,
        topic: str,
        num_hexagons: int = 6,
        context: Optional[Dict[str, Any]] = None,
        validate_constraints: bool = True
    ) -> Dict[str, Any]:
        """
        Generate concept-spread illustration

        Args:
            topic: Main topic for concept spread
            num_hexagons: Number of hexagons (default: 6, only 6 supported currently)
            context: Optional context (previous slides, etc.)
            validate_constraints: Whether to validate character constraints

        Returns:
            {
                "success": bool,
                "html": str (complete rendered HTML),
                "generated_content": dict,
                "character_counts": dict,
                "validation": {
                    "valid": bool,
                    "violations": list
                },
                "metadata": {
                    "model": str,
                    "generation_time_ms": int,
                    "attempts": int
                }
            }
        """
        start_time = time.time()

        try:
            # Validate inputs
            if num_hexagons != 6:
                return {
                    "success": False,
                    "error": "Only 6-hexagon variant supported currently"
                }

            # Get template and constraints
            variant_key = f"concept_spread_{num_hexagons}"
            template_html = self.templates.get(str(num_hexagons))

            if not template_html:
                return {
                    "success": False,
                    "error": f"Template not found for {num_hexagons} hexagons"
                }

            constraints = self.constraints.get(variant_key, {})

            # Generate content with retry logic
            max_retries = 2
            is_valid = False
            violations = []

            for attempt in range(max_retries + 1):
                logger.info(f"Generation attempt {attempt + 1}/{max_retries + 1}")

                # Generate content with LLM
                result = await self.llm_service.generate_concept_spread_content(
                    topic=topic,
                    constraints=constraints,
                    context=context
                )

                if not result["success"]:
                    return result  # LLM error, abort

                generated_content = result["content"]

                # Validate constraints (if enabled)
                if validate_constraints:
                    is_valid, violations = self.validator.validate_concept_spread_content(
                        generated_content=generated_content,
                        constraints=constraints
                    )

                    if is_valid:
                        logger.info(f"Content validated successfully on attempt {attempt + 1}")
                        break
                    else:
                        logger.warning(f"Attempt {attempt + 1} failed validation: {len(violations)} violations")
                        if attempt < max_retries:
                            continue  # Retry
                else:
                    is_valid = True
                    violations = []
                    break

            # Fill template with generated content
            filled_html = self._fill_template(template_html, generated_content)

            # Calculate character counts
            character_counts = self.validator.calculate_character_counts(generated_content)

            # Calculate generation time
            generation_time_ms = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "html": filled_html,
                "generated_content": generated_content,
                "character_counts": character_counts,
                "validation": {
                    "valid": is_valid,
                    "violations": violations
                },
                "metadata": {
                    "model": result.get("model"),
                    "usage_metadata": result.get("usage_metadata", {}),
                    "generation_time_ms": generation_time_ms,
                    "attempts": attempt + 1
                }
            }

        except Exception as e:
            logger.error(f"Error in concept-spread generation: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _fill_template(self, template_html: str, generated_content: Dict[str, str]) -> str:
        """
        Fill template placeholders with generated content

        Args:
            template_html: HTML template with {placeholder} syntax
            generated_content: Dict of field_name: value

        Returns:
            HTML with all placeholders replaced
        """
        filled_html = template_html

        # Replace all placeholders
        for field_name, value in generated_content.items():
            placeholder = f"{{{field_name}}}"
            filled_html = filled_html.replace(placeholder, value)

        # Clean up any remaining unfilled placeholders
        import re
        filled_html = re.sub(r'\{[^}]+\}', '', filled_html)

        return filled_html
