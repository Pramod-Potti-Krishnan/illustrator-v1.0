"""
Template Generator

Generates infographics using pre-built HTML templates.
Adapts existing generators (pyramid, funnel, concentric_circles, concept_spread)
to the unified Layout Service interface.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.models.layout_service_request import InfographicGenerateRequest
from app.models.layout_service_response import InfographicItem
from app.generators.base_generator import BaseGenerator, GenerationResult

logger = logging.getLogger(__name__)


class TemplateGenerator(BaseGenerator):
    """
    Generates infographics using pre-built HTML templates.

    Supports: pyramid, funnel, concentric_circles, concept_spread, venn, comparison

    Adapts the existing generation pipelines to the unified response format.
    """

    # Map type to existing generator module
    GENERATOR_MAP = {
        "pyramid": "pyramid_generator",
        "funnel": "funnel_generator",
        "concentric_circles": "concentric_circles_generator",
        "concept_spread": "concept_spread_generator",
        # venn and comparison will use template-only generation (no LLM yet)
    }

    def __init__(self, infographic_type: str):
        """
        Initialize template generator.

        Args:
            infographic_type: Type of infographic to generate
        """
        super().__init__(infographic_type)
        self.templates_dir = Path(__file__).parent.parent.parent / "templates"
        self._generator_instance = None

    def get_output_mode(self) -> str:
        """Return 'html' for template-based generation."""
        return "html"

    async def generate(self, request: InfographicGenerateRequest) -> GenerationResult:
        """
        Generate infographic using HTML template.

        Routes to existing generators for types that have them,
        or generates directly from template for simpler types.

        Args:
            request: The generation request

        Returns:
            GenerationResult with HTML and SVG-wrapped output
        """
        try:
            # Calculate dimensions
            width_px, height_px = self.calculate_dimensions(
                request.constraints.gridWidth,
                request.constraints.gridHeight
            )

            # Resolve colors
            color_scheme = self.resolve_color_scheme(request)
            colors = self.extract_colors_from_palette(color_scheme)

            # Determine item count
            item_count = self.determine_item_count(request)

            # Route to appropriate generator
            if self.infographic_type in self.GENERATOR_MAP:
                result = await self._generate_with_existing_generator(
                    request, item_count, color_scheme
                )
            else:
                # For types without existing generators (venn, comparison)
                result = await self._generate_from_template_only(
                    request, item_count, color_scheme
                )

            if not result.success:
                return result

            # Wrap HTML in SVG for consistent output
            svg_content = self.wrap_html_in_svg(result.html, width_px, height_px)

            return GenerationResult(
                success=True,
                svg=svg_content,
                html=result.html,
                items=result.items,
                metadata={
                    "type": self.infographic_type,
                    "width_px": width_px,
                    "height_px": height_px,
                    "colors": colors,
                    "item_count": len(result.items) if result.items else item_count,
                    "generation_method": "template"
                }
            )

        except Exception as e:
            logger.error(f"Template generation error: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                error=str(e),
                error_code="GENERATION_FAILED",
                retryable=True
            )

    async def _generate_with_existing_generator(
        self,
        request: InfographicGenerateRequest,
        item_count: int,
        color_scheme: Dict[str, Any]
    ) -> GenerationResult:
        """
        Generate using existing specialized generator.

        Args:
            request: The generation request
            item_count: Number of items to generate
            color_scheme: Resolved color scheme

        Returns:
            GenerationResult
        """
        try:
            if self.infographic_type == "pyramid":
                return await self._generate_pyramid(request, item_count, color_scheme)
            elif self.infographic_type == "funnel":
                return await self._generate_funnel(request, item_count, color_scheme)
            elif self.infographic_type == "concentric_circles":
                return await self._generate_concentric_circles(request, item_count, color_scheme)
            elif self.infographic_type == "concept_spread":
                return await self._generate_concept_spread(request, color_scheme)
            else:
                return GenerationResult(
                    success=False,
                    error=f"No generator for type: {self.infographic_type}",
                    error_code="INVALID_TYPE"
                )
        except Exception as e:
            logger.error(f"Existing generator error: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                error=str(e),
                error_code="GENERATION_FAILED",
                retryable=True
            )

    async def _generate_pyramid(
        self,
        request: InfographicGenerateRequest,
        item_count: int,
        color_scheme: Dict[str, Any]
    ) -> GenerationResult:
        """Generate pyramid using existing generator."""
        from app.llm_services.pyramid_generator import get_generator

        generator = get_generator()

        # Build context
        context = {
            "presentation_title": request.context.presentationTitle,
            "slide_purpose": request.context.slideTitle,
            "industry": request.context.industry,
        }

        result = await generator.generate_pyramid_data(
            num_levels=item_count,
            topic=request.prompt,
            context=context,
            tone=request.context.tone or "professional",
            audience=request.context.audience or "general",
            validate_constraints=True
        )

        if not result.get("success"):
            return GenerationResult(
                success=False,
                error=result.get("error", "Pyramid generation failed"),
                error_code="GENERATION_FAILED",
                retryable=True
            )

        # Load and fill template
        template_path = self.templates_dir / "pyramid" / f"{item_count}.html"
        if not template_path.exists():
            return GenerationResult(
                success=False,
                error=f"Pyramid template not found: {item_count}.html",
                error_code="TEMPLATE_NOT_FOUND"
            )

        template_html = template_path.read_text()
        filled_html = self._fill_template(template_html, result["content"])

        # Build items
        items = self._extract_pyramid_items(result["content"], item_count)

        return GenerationResult(
            success=True,
            html=filled_html,
            items=items,
            metadata=result.get("metadata", {})
        )

    async def _generate_funnel(
        self,
        request: InfographicGenerateRequest,
        item_count: int,
        color_scheme: Dict[str, Any]
    ) -> GenerationResult:
        """Generate funnel using existing generator."""
        from app.llm_services.funnel_generator import get_funnel_generator

        generator = get_funnel_generator()

        context = {
            "presentation_title": request.context.presentationTitle,
            "slide_purpose": request.context.slideTitle,
            "industry": request.context.industry,
        }

        result = await generator.generate_funnel_data(
            num_stages=item_count,
            topic=request.prompt,
            context=context,
            tone=request.context.tone or "professional",
            audience=request.context.audience or "general",
            validate_constraints=True
        )

        if not result.get("success"):
            return GenerationResult(
                success=False,
                error=result.get("error", "Funnel generation failed"),
                error_code="GENERATION_FAILED",
                retryable=True
            )

        # Load and fill template
        template_path = self.templates_dir / "funnel" / f"{item_count}.html"
        if not template_path.exists():
            return GenerationResult(
                success=False,
                error=f"Funnel template not found: {item_count}.html",
                error_code="TEMPLATE_NOT_FOUND"
            )

        template_html = template_path.read_text()
        filled_html = self._fill_template(template_html, result["content"])

        # Build items
        items = self._extract_funnel_items(result["content"], item_count)

        return GenerationResult(
            success=True,
            html=filled_html,
            items=items,
            metadata=result.get("metadata", {})
        )

    async def _generate_concentric_circles(
        self,
        request: InfographicGenerateRequest,
        item_count: int,
        color_scheme: Dict[str, Any]
    ) -> GenerationResult:
        """Generate concentric circles using existing generator."""
        from app.llm_services.concentric_circles_generator import get_concentric_circles_generator

        generator = get_concentric_circles_generator()

        context = {
            "presentation_title": request.context.presentationTitle,
            "slide_title": request.context.slideTitle,
            "industry": request.context.industry,
        }

        result = await generator.generate_concentric_circles_data(
            num_circles=item_count,
            topic=request.prompt,
            context=context,
            tone=request.context.tone or "professional",
            audience=request.context.audience or "general",
            validate_constraints=True
        )

        if not result.get("success"):
            return GenerationResult(
                success=False,
                error=result.get("error", "Concentric circles generation failed"),
                error_code="GENERATION_FAILED",
                retryable=True
            )

        # Load and fill template
        template_path = self.templates_dir / "concentric_circles" / f"{item_count}.html"
        if not template_path.exists():
            return GenerationResult(
                success=False,
                error=f"Concentric circles template not found: {item_count}.html",
                error_code="TEMPLATE_NOT_FOUND"
            )

        template_html = template_path.read_text()
        filled_html = self._fill_template(template_html, result["content"])

        # Build items
        items = self._extract_concentric_circles_items(result["content"], item_count)

        return GenerationResult(
            success=True,
            html=filled_html,
            items=items,
            metadata=result.get("metadata", {})
        )

    async def _generate_concept_spread(
        self,
        request: InfographicGenerateRequest,
        color_scheme: Dict[str, Any]
    ) -> GenerationResult:
        """Generate concept spread using existing generator."""
        from app.generators.concept_spread_generator import ConceptSpreadGenerator

        generator = ConceptSpreadGenerator()

        context = {
            "presentation_title": request.context.presentationTitle,
            "slide_title": request.context.slideTitle,
            "industry": request.context.industry,
        }

        result = await generator.generate(
            topic=request.prompt,
            num_hexagons=6,  # Currently only 6 is supported
            context=context,
            validate_constraints=True
        )

        if not result.get("success"):
            return GenerationResult(
                success=False,
                error=result.get("error", "Concept spread generation failed"),
                error_code="GENERATION_FAILED",
                retryable=True
            )

        # Build items
        items = self._extract_concept_spread_items(result["generated_content"])

        return GenerationResult(
            success=True,
            html=result["html"],
            items=items,
            metadata=result.get("metadata", {})
        )

    async def _generate_from_template_only(
        self,
        request: InfographicGenerateRequest,
        item_count: int,
        color_scheme: Dict[str, Any]
    ) -> GenerationResult:
        """
        Generate from template without LLM.

        For types that don't have full LLM support yet (venn, comparison).
        Returns a placeholder implementation.

        Args:
            request: The generation request
            item_count: Number of items
            color_scheme: Color scheme

        Returns:
            GenerationResult
        """
        # Check if template exists
        template_dir = self.templates_dir / self.infographic_type
        if not template_dir.exists():
            return GenerationResult(
                success=False,
                error=f"Templates not found for type: {self.infographic_type}",
                error_code="TEMPLATE_NOT_FOUND"
            )

        # For now, return an error for unsupported types
        # These will be implemented with SVG generator or new templates
        return GenerationResult(
            success=False,
            error=f"Type '{self.infographic_type}' not fully implemented. Use SVG types instead.",
            error_code="NOT_IMPLEMENTED",
            retryable=False
        )

    def _fill_template(self, template_html: str, content: Dict[str, str]) -> str:
        """
        Fill template placeholders with content.

        Args:
            template_html: HTML template with {placeholder} syntax
            content: Dict of placeholder_name -> value

        Returns:
            Filled HTML string
        """
        filled_html = template_html

        for field_name, value in content.items():
            placeholder = f"{{{field_name}}}"
            filled_html = filled_html.replace(placeholder, str(value))

        # Clean up remaining unfilled placeholders
        filled_html = re.sub(r'\{[^}]+\}', '', filled_html)

        return filled_html

    def _extract_pyramid_items(self, content: Dict[str, str], num_levels: int) -> List[InfographicItem]:
        """Extract items from pyramid content."""
        items = []
        for level in range(num_levels, 0, -1):
            label_key = f"level_{level}_label"
            label = content.get(label_key, f"Level {level}")

            # Collect bullets
            bullets = []
            for bullet_num in range(1, 6):
                bullet_key = f"level_{level}_bullet_{bullet_num}"
                if bullet_key in content:
                    bullets.append(content[bullet_key])

            items.append(InfographicItem(
                id=self.generate_item_id(level),
                title=label,
                description="; ".join(bullets) if bullets else None,
                position=num_levels - level,
                metadata={"level": level}
            ))

        return items

    def _extract_funnel_items(self, content: Dict[str, str], num_stages: int) -> List[InfographicItem]:
        """Extract items from funnel content."""
        items = []
        for stage in range(1, num_stages + 1):
            name_key = f"stage_{stage}_name"
            name = content.get(name_key, f"Stage {stage}")

            # Collect bullets
            bullets = []
            for bullet_num in range(1, 6):
                bullet_key = f"stage_{stage}_bullet_{bullet_num}"
                if bullet_key in content:
                    bullets.append(content[bullet_key])

            items.append(InfographicItem(
                id=self.generate_item_id(stage),
                title=name,
                description="; ".join(bullets) if bullets else None,
                position=stage - 1,
                metadata={"stage": stage}
            ))

        return items

    def _extract_concentric_circles_items(self, content: Dict[str, str], num_circles: int) -> List[InfographicItem]:
        """Extract items from concentric circles content."""
        items = []
        for circle in range(1, num_circles + 1):
            label_key = f"circle_{circle}_label"
            label = content.get(label_key, f"Circle {circle}")

            # Collect legend bullets
            bullets = []
            for bullet_num in range(1, 6):
                bullet_key = f"legend_{circle}_bullet_{bullet_num}"
                if bullet_key in content:
                    bullets.append(content[bullet_key])

            items.append(InfographicItem(
                id=self.generate_item_id(circle),
                title=label,
                description="; ".join(bullets) if bullets else None,
                position=circle - 1,
                metadata={"circle": circle}
            ))

        return items

    def _extract_concept_spread_items(self, content: Dict[str, str]) -> List[InfographicItem]:
        """Extract items from concept spread content."""
        items = []
        for box in range(1, 7):
            title_key = f"box_{box}_title"
            title = content.get(title_key, f"Concept {box}")

            # Collect bullets
            bullets = []
            for bullet_num in range(1, 4):
                bullet_key = f"box_{box}_bullet_{bullet_num}"
                if bullet_key in content:
                    bullets.append(content[bullet_key])

            items.append(InfographicItem(
                id=self.generate_item_id(box),
                title=title,
                description="; ".join(bullets) if bullets else None,
                icon=content.get(f"box_{box}_emoji"),
                position=box - 1,
                metadata={"box": box}
            ))

        return items
