"""
Base Generator Abstract Class

Defines the interface for all infographic generators.
Both template-based (HTML) and dynamic (SVG) generators inherit from this.
"""

import uuid
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass

from app.models.layout_service_request import InfographicGenerateRequest
from app.models.layout_service_response import (
    InfographicItem,
    InfographicData,
    InfographicMetadata,
    EditableItem,
    EditInfo,
    RenderedOutput,
    ResponseData,
)
from app.core.type_constraints import (
    GRID_UNIT_PIXELS,
    get_type_constraint,
    get_item_limits_for_grid,
    get_color_scheme,
    TypeConstraint,
)

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result from a generator."""
    success: bool
    svg: Optional[str] = None
    html: Optional[str] = None
    items: Optional[List[InfographicItem]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    retryable: bool = False


class BaseGenerator(ABC):
    """
    Abstract base class for infographic generators.

    Subclasses must implement:
    - generate(): Main generation logic
    - get_output_mode(): Return 'html' or 'svg'

    Provides common utilities:
    - Dimension calculations
    - Color scheme resolution
    - Item count determination
    - Response building
    """

    def __init__(self, infographic_type: str):
        """
        Initialize generator for a specific infographic type.

        Args:
            infographic_type: Type of infographic (pyramid, timeline, etc.)
        """
        self.infographic_type = infographic_type
        self.constraints = get_type_constraint(infographic_type)
        logger.info(f"Initialized {self.__class__.__name__} for type: {infographic_type}")

    @abstractmethod
    async def generate(self, request: InfographicGenerateRequest) -> GenerationResult:
        """
        Generate the infographic.

        Args:
            request: The generation request

        Returns:
            GenerationResult with svg/html content and structured data
        """
        pass

    @abstractmethod
    def get_output_mode(self) -> str:
        """
        Return the output mode for this generator.

        Returns:
            'html' for template-based, 'svg' for dynamic generation
        """
        pass

    def calculate_dimensions(self, grid_width: int, grid_height: int) -> Tuple[int, int]:
        """
        Convert grid units to pixel dimensions.

        Args:
            grid_width: Width in grid units (1-12)
            grid_height: Height in grid units (1-8)

        Returns:
            Tuple of (width_px, height_px)
        """
        return (grid_width * GRID_UNIT_PIXELS, grid_height * GRID_UNIT_PIXELS)

    def determine_item_count(self, request: InfographicGenerateRequest) -> int:
        """
        Determine the number of items to generate.

        Uses explicit itemCount if provided, otherwise calculates based on grid size.

        Args:
            request: The generation request

        Returns:
            Number of items to generate
        """
        if request.contentOptions and request.contentOptions.itemCount:
            # Clamp to valid range
            item_count = request.contentOptions.itemCount
            return max(self.constraints.min_items,
                      min(item_count, self.constraints.max_items))

        # Calculate based on grid size
        limits = get_item_limits_for_grid(
            self.infographic_type,
            request.constraints.gridWidth,
            request.constraints.gridHeight
        )
        return limits["recommended"]

    def resolve_color_scheme(self, request: InfographicGenerateRequest) -> Dict[str, Any]:
        """
        Resolve the color scheme for the infographic.

        Args:
            request: The generation request

        Returns:
            Color palette dict with primary, secondary, accent, etc.
        """
        scheme_name = request.style.colorScheme.value if request.style else "professional"
        brand_colors = None

        if scheme_name == "brand" and request.context.brandColors:
            brand_colors = request.context.brandColors

        return get_color_scheme(scheme_name, brand_colors)

    def generate_id(self) -> str:
        """Generate a unique generation ID."""
        return f"gen_{uuid.uuid4().hex[:12]}"

    def generate_item_id(self, index: int) -> str:
        """Generate a unique item ID."""
        return f"item_{index:03d}_{uuid.uuid4().hex[:6]}"

    def build_response_data(
        self,
        generation_id: str,
        svg_content: str,
        html_content: str,
        items: List[InfographicItem],
        width_px: int,
        height_px: int,
        color_palette: List[str],
        icons_used: Optional[List[str]] = None
    ) -> ResponseData:
        """
        Build the ResponseData object from generation results.

        Args:
            generation_id: Unique generation ID
            svg_content: SVG string
            html_content: HTML string
            items: List of InfographicItem objects
            width_px: Width in pixels
            height_px: Height in pixels
            color_palette: List of colors used
            icons_used: List of icons/emojis used

        Returns:
            ResponseData object
        """
        # Build rendered output
        rendered = RenderedOutput(
            svg=svg_content,
            html=html_content,
            png=None  # PNG generation not implemented
        )

        # Build infographic data
        infographic_data = InfographicData(
            items=items,
            metadata={
                "type": self.infographic_type,
                "generationMethod": self.get_output_mode()
            }
        )

        # Build metadata
        metadata = InfographicMetadata(
            type=self.infographic_type,
            itemCount=len(items),
            dimensions={"width": width_px, "height": height_px},
            aspectRatio=round(width_px / height_px, 2) if height_px > 0 else 1.0,
            colorPalette=color_palette,
            iconsUsed=icons_used,
            generationMethod=f"{'template' if self.get_output_mode() == 'html' else 'dynamic_svg'}"
        )

        # Build edit info
        editable_items = [
            EditableItem(
                itemId=item.id,
                itemType="title",
                currentValue=item.title,
                maxLength=100,
                position=item.position
            )
            for item in items
        ]

        edit_info = EditInfo(
            editableItems=editable_items,
            reorderableItems=True,
            addableItems=len(items) < self.constraints.max_items,
            deletableItems=len(items) > self.constraints.min_items,
            maxItems=self.constraints.max_items,
            minItems=self.constraints.min_items
        )

        return ResponseData(
            generationId=generation_id,
            rendered=rendered,
            infographicData=infographic_data,
            metadata=metadata,
            editInfo=edit_info
        )

    def wrap_svg_in_html(self, svg_content: str, width_px: int, height_px: int) -> str:
        """
        Wrap SVG content in an HTML container.

        Args:
            svg_content: Raw SVG string
            width_px: Width in pixels
            height_px: Height in pixels

        Returns:
            HTML string with embedded SVG
        """
        return f"""<div class="infographic-container" style="width: {width_px}px; height: {height_px}px; overflow: hidden;">
{svg_content}
</div>"""

    def wrap_html_in_svg(self, html_content: str, width_px: int, height_px: int) -> str:
        """
        Wrap HTML content in an SVG foreignObject.

        This allows HTML templates to be used where SVG is expected.

        Args:
            html_content: Raw HTML string
            width_px: Width in pixels
            height_px: Height in pixels

        Returns:
            SVG string with embedded HTML via foreignObject
        """
        # Escape any problematic characters in HTML for XML
        escaped_html = html_content.replace("&", "&amp;")

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px} {height_px}" width="{width_px}" height="{height_px}">
  <foreignObject x="0" y="0" width="{width_px}" height="{height_px}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="width: 100%; height: 100%;">
{html_content}
    </div>
  </foreignObject>
</svg>"""

    def get_context_summary(self, request: InfographicGenerateRequest) -> str:
        """
        Build a context summary string for LLM prompts.

        Args:
            request: The generation request

        Returns:
            Context summary string
        """
        parts = []

        if request.context.presentationTitle:
            parts.append(f"Presentation: {request.context.presentationTitle}")
        if request.context.slideTitle:
            parts.append(f"Slide: {request.context.slideTitle}")
        if request.context.industry:
            parts.append(f"Industry: {request.context.industry}")
        if request.context.audience:
            parts.append(f"Audience: {request.context.audience}")
        if request.context.tone:
            parts.append(f"Tone: {request.context.tone}")

        return "\n".join(parts) if parts else "General business context"

    def extract_colors_from_palette(self, color_scheme: Dict[str, Any]) -> List[str]:
        """
        Extract a flat list of colors from a color scheme.

        Args:
            color_scheme: Color scheme dict

        Returns:
            List of hex color strings
        """
        colors = [color_scheme.get("primary", "#1E40AF")]

        secondary = color_scheme.get("secondary", [])
        if isinstance(secondary, list):
            colors.extend(secondary)
        elif secondary:
            colors.append(secondary)

        if color_scheme.get("accent"):
            colors.append(color_scheme["accent"])

        return colors
