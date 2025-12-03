"""
SVG Generator

Generates infographics dynamically using Gemini 2.5 Pro.
Supports: timeline, process, statistics, hierarchy, list, cycle, matrix, roadmap
"""

import logging
from typing import Dict, Any, List, Optional

from app.models.layout_service_request import InfographicGenerateRequest
from app.models.layout_service_response import InfographicItem
from app.generators.base_generator import BaseGenerator, GenerationResult
from app.llm_services.svg_generation_service import get_svg_generation_service

logger = logging.getLogger(__name__)


class SVGGenerator(BaseGenerator):
    """
    Generates infographics using dynamic SVG via Gemini 2.5 Pro.

    Supports: timeline, process, statistics, hierarchy, list, cycle, matrix, roadmap
    """

    def __init__(self, infographic_type: str):
        """
        Initialize SVG generator.

        Args:
            infographic_type: Type of infographic to generate
        """
        super().__init__(infographic_type)
        self._svg_service = None

    @property
    def svg_service(self):
        """Lazy-load SVG generation service."""
        if self._svg_service is None:
            self._svg_service = get_svg_generation_service()
        return self._svg_service

    def get_output_mode(self) -> str:
        """Return 'svg' for dynamic SVG generation."""
        return "svg"

    async def generate(self, request: InfographicGenerateRequest) -> GenerationResult:
        """
        Generate infographic using dynamic SVG via Gemini 2.5 Pro.

        Args:
            request: The generation request

        Returns:
            GenerationResult with SVG and HTML-wrapped output
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

            # Get context summary
            context_summary = self.get_context_summary(request)

            # Determine orientation
            orientation = request.style.orientation.value if request.style else "auto"
            if orientation == "auto":
                # Auto-detect based on aspect ratio
                aspect = width_px / height_px
                if aspect > 1.5:
                    orientation = "horizontal"
                elif aspect < 0.75:
                    orientation = "vertical"
                else:
                    orientation = "horizontal"  # Default

            # Get icon style
            icon_style = request.style.iconStyle.value if request.style else "emoji"

            # Get density
            density = request.style.density.value if request.style else "balanced"

            logger.info(
                f"Generating {self.infographic_type} SVG: "
                f"{width_px}x{height_px}, {item_count} items, {orientation}"
            )

            # Generate SVG using Gemini 2.5 Pro
            result = await self.svg_service.generate_svg(
                infographic_type=self.infographic_type,
                prompt=request.prompt,
                width=width_px,
                height=height_px,
                color_scheme=color_scheme,
                item_count=item_count,
                context_summary=context_summary,
                icon_style=icon_style,
                density=density,
                orientation=orientation
            )

            if not result.get("success"):
                return GenerationResult(
                    success=False,
                    error=result.get("error", "SVG generation failed"),
                    error_code="GENERATION_FAILED",
                    retryable=True
                )

            svg_content = result["svg"]
            structured_data = result.get("structured_data", {})

            # Wrap SVG in HTML container
            html_content = self.wrap_svg_in_html(svg_content, width_px, height_px)

            # Extract items from structured data
            items = self._extract_items_from_structured_data(structured_data)

            return GenerationResult(
                success=True,
                svg=svg_content,
                html=html_content,
                items=items,
                metadata={
                    "type": self.infographic_type,
                    "width_px": width_px,
                    "height_px": height_px,
                    "colors": colors,
                    "item_count": len(items),
                    "orientation": orientation,
                    "generation_method": "dynamic_svg",
                    "model": result.get("model")
                }
            )

        except Exception as e:
            logger.error(f"SVG generation error: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                error=str(e),
                error_code="GENERATION_FAILED",
                retryable=True
            )

    def _extract_items_from_structured_data(self, structured_data: Dict[str, Any]) -> List[InfographicItem]:
        """
        Extract InfographicItem objects from structured data.

        Args:
            structured_data: Structured data from LLM response

        Returns:
            List of InfographicItem objects
        """
        items = []
        raw_items = structured_data.get("items", [])

        for idx, raw_item in enumerate(raw_items):
            if isinstance(raw_item, dict):
                items.append(InfographicItem(
                    id=raw_item.get("id", self.generate_item_id(idx)),
                    title=raw_item.get("title", f"Item {idx + 1}"),
                    description=raw_item.get("description"),
                    icon=raw_item.get("icon"),
                    value=raw_item.get("value"),
                    color=raw_item.get("color"),
                    position=idx,
                    metadata=raw_item.get("metadata")
                ))
            else:
                # Handle simple string items
                items.append(InfographicItem(
                    id=self.generate_item_id(idx),
                    title=str(raw_item),
                    position=idx
                ))

        return items


# Factory function
def create_svg_generator(infographic_type: str) -> SVGGenerator:
    """Create an SVG generator for the specified type."""
    return SVGGenerator(infographic_type)
