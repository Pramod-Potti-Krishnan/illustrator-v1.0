"""
SVG Generation Service

Uses Gemini 2.5 Pro to generate complete SVG infographics dynamically.
Supports: timeline, process, statistics, hierarchy, list, cycle, matrix, roadmap
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from xml.etree import ElementTree

from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationConfig

from app.core.type_constraints import get_color_scheme

logger = logging.getLogger(__name__)


class SVGGenerationService:
    """
    Service for generating SVG infographics using Gemini 2.5 Pro.

    Generates complete, valid SVG code based on:
    - Infographic type
    - User prompt
    - Dimensions and color scheme
    - Type-specific design guidelines
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize SVG generation service.

        Args:
            project_id: GCP project ID (from env if not provided)
            location: GCP region (from env if not provided)
            model_name: Model to use (from env if not provided)
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location or os.getenv("GEMINI_LOCATION", "us-central1")
        self.model_name = model_name or os.getenv("LLM_SVG_GENERATOR", "gemini-2.5-pro-preview-05-06")

        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID environment variable must be set")

        # Initialize Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)

        # Create generative model
        self.model = GenerativeModel(self.model_name)

        logger.info(
            f"Initialized SVGGenerationService: "
            f"project={self.project_id}, location={self.location}, model={self.model_name}"
        )

    async def generate_svg(
        self,
        infographic_type: str,
        prompt: str,
        width: int,
        height: int,
        color_scheme: Dict[str, Any],
        item_count: int,
        context_summary: str,
        icon_style: str = "emoji",
        density: str = "balanced",
        orientation: str = "auto"
    ) -> Dict[str, Any]:
        """
        Generate a complete SVG infographic.

        Args:
            infographic_type: Type (timeline, process, etc.)
            prompt: User's content prompt
            width: Width in pixels
            height: Height in pixels
            color_scheme: Color palette to use
            item_count: Number of items to generate
            context_summary: Context from presentation
            icon_style: Icon style (emoji, outlined, etc.)
            density: Content density
            orientation: Layout orientation

        Returns:
            Dict with:
                - success: bool
                - svg: str (SVG content)
                - structured_data: dict (items, metadata)
                - error: str (if failed)
        """
        try:
            # Build the prompt
            full_prompt = self._build_generation_prompt(
                infographic_type=infographic_type,
                prompt=prompt,
                width=width,
                height=height,
                color_scheme=color_scheme,
                item_count=item_count,
                context_summary=context_summary,
                icon_style=icon_style,
                density=density,
                orientation=orientation
            )

            # Generate with Gemini
            generation_config = GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192,  # SVGs can be long
                response_mime_type="application/json"
            )

            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            # Parse response
            response_text = response.text.strip()

            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text[:500]}")
                return {
                    "success": False,
                    "error": "Invalid JSON response from LLM",
                    "raw_response": response_text
                }

            # Validate SVG
            svg_content = result.get("svg", "")
            is_valid, error = self._validate_svg(svg_content)

            if not is_valid:
                logger.warning(f"SVG validation failed: {error}")
                # Try to fix common issues
                svg_content = self._fix_svg_issues(svg_content, width, height)
                is_valid, error = self._validate_svg(svg_content)

                if not is_valid:
                    return {
                        "success": False,
                        "error": f"Generated SVG is invalid: {error}",
                        "svg": svg_content
                    }

            return {
                "success": True,
                "svg": svg_content,
                "structured_data": result.get("structured_data", {}),
                "model": self.model_name
            }

        except Exception as e:
            logger.error(f"SVG generation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _build_generation_prompt(
        self,
        infographic_type: str,
        prompt: str,
        width: int,
        height: int,
        color_scheme: Dict[str, Any],
        item_count: int,
        context_summary: str,
        icon_style: str,
        density: str,
        orientation: str
    ) -> str:
        """Build the complete prompt for SVG generation."""

        # Get type-specific guidelines
        type_guidelines = self._get_type_guidelines(infographic_type)

        # Format colors
        primary_color = color_scheme.get("primary", "#1E40AF")
        secondary_colors = color_scheme.get("secondary", ["#3B82F6"])
        if isinstance(secondary_colors, list):
            secondary_colors_str = ", ".join(secondary_colors)
        else:
            secondary_colors_str = secondary_colors
        accent_color = color_scheme.get("accent", "#0D9488")
        text_color = color_scheme.get("text", "#1E293B")
        background_color = color_scheme.get("background", "#F8FAFC")

        # Determine icon format
        icon_instructions = ""
        if icon_style == "emoji":
            icon_instructions = """
- Use emoji characters for icons (e.g., rocket, chart, target, star, check, arrow)
- Place emojis as <text> elements with appropriate font-size
- Examples: Use text elements with emojis like: <text font-size="24">🚀</text>"""
        elif icon_style == "none":
            icon_instructions = "- Do NOT include any icons"
        else:
            icon_instructions = f"""
- Create simple geometric icons in {icon_style} style
- Use basic shapes (circles, rectangles, paths) for icons
- Keep icons simple and recognizable"""

        prompt_template = f"""You are an expert SVG infographic designer. Generate a complete, valid SVG infographic.

INFOGRAPHIC TYPE: {infographic_type}
USER REQUEST: {prompt}

DIMENSIONS:
- Width: {width}px
- Height: {height}px
- ViewBox: 0 0 {width} {height}

COLORS:
- Primary: {primary_color}
- Secondary: {secondary_colors_str}
- Accent: {accent_color}
- Text: {text_color}
- Background: {background_color}

CONTENT:
- Generate exactly {item_count} items
- Density: {density}
- Orientation: {orientation}
- Context: {context_summary}

ICON STYLE:
{icon_instructions}

TYPE-SPECIFIC GUIDELINES FOR {infographic_type.upper()}:
{type_guidelines}

SVG REQUIREMENTS:
1. Start with: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
2. Include all visual elements inline (no external references)
3. Use the specified color palette
4. Ensure text is readable (minimum 14px font-size)
5. Include proper spacing and alignment
6. Make it visually professional and polished
7. Use rounded corners (rx="8") for modern look
8. Add subtle shadows or gradients where appropriate
9. Ensure all text fits within its containers
10. End with: </svg>

TYPOGRAPHY:
- Titles: font-weight="700", font-size="18-24px"
- Labels: font-weight="600", font-size="14-16px"
- Body text: font-weight="400", font-size="12-14px"
- Font family: Inter, system-ui, sans-serif

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
  "svg": "<svg xmlns=\\"http://www.w3.org/2000/svg\\" ...complete SVG code...</svg>",
  "structured_data": {{
    "items": [
      {{"id": "item_1", "title": "Title 1", "description": "Description 1", "icon": "emoji or null"}},
      ...
    ],
    "metadata": {{
      "orientation": "horizontal or vertical",
      "layout": "specific layout used"
    }}
  }}
}}

IMPORTANT:
- The SVG must be complete and render correctly
- All quotes inside the SVG must be escaped as \\"
- No comments or extra text outside the JSON
- Validate that the SVG is well-formed XML"""

        return prompt_template

    def _get_type_guidelines(self, infographic_type: str) -> str:
        """Get type-specific design guidelines."""

        guidelines = {
            "timeline": """
TIMELINE DESIGN:
- Horizontal layout: Events flow left-to-right on a central line
- Vertical layout: Events flow top-to-bottom
- Central connector: A line/path connecting all events (stroke-width: 3-4px)
- Event markers: Circles (r=12-16) at each event point on the line
- Date labels: Positioned above/below (horizontal) or left (vertical) of markers
- Event titles: Clear, bold text near each marker
- Event descriptions: Smaller text below titles
- Alternating positions: Events can alternate above/below the line for better spacing
- Arrow at end: Optional directional arrow showing progression
- Current marker: Optionally highlight "current" or "now" with different color/size""",

            "process": """
PROCESS FLOW DESIGN:
- Step boxes: Rectangles (width: 150-200px, height: 80-120px) with rounded corners
- Connecting arrows: Clear directional arrows between steps (stroke-width: 2-3px)
- Step numbers: Circle badges (1, 2, 3...) in the corner of each box or before the title
- Step titles: Bold, centered in boxes
- Step descriptions: Smaller text below titles
- Layouts:
  - Linear: All steps in a row with arrows
  - Zigzag: Steps arranged in two rows, alternating
  - Vertical: Steps stacked vertically with downward arrows
- Color progression: Steps can get progressively lighter or use accent for important steps
- Icon area: Space for icon/emoji at top of each step box""",

            "statistics": """
STATISTICS DESIGN:
- Number display: Large, prominent numbers (font-size: 36-48px, font-weight: 700)
- Unit/suffix: Smaller text after number (%, k, M, etc.)
- Stat cards: Rounded rectangles containing each statistic
- Icons: Related icon/emoji above or beside each number
- Labels: Clear descriptions below each statistic
- Trend indicators: Optional up/down arrows with percentage change
- Color coding: Use colors to distinguish different stats or show positive/negative
- Grid layout: Arrange stats in 2x2, 3x2, or 4x2 grid based on count
- Comparison bars: Optional horizontal bars showing relative values""",

            "hierarchy": """
HIERARCHY/ORG CHART DESIGN:
- Node boxes: Rectangles with rounded corners for each person/item
- Connecting lines: Vertical and horizontal lines connecting parent to children
- Root node: Top center, possibly larger or different color
- Level spacing: Consistent vertical spacing between levels
- Horizontal centering: Children centered under parents
- Node content:
  - Title/name at top (bold)
  - Role/description below (smaller)
  - Optional icon/avatar area
- Line style: Solid lines, stroke-width: 2px
- Collapsed indicator: + symbol for nodes that could have children
- Level colors: Optionally different shades per level""",

            "list": """
LIST DESIGN:
- Vertical arrangement: Items stacked top-to-bottom
- Number badges: Circles with numbers (1, 2, 3...) on the left
- Or icons: Icon/emoji on the left instead of numbers
- Title text: Bold text next to number/icon
- Description: Optional smaller text below title
- Consistent spacing: Equal vertical gap between items
- Background: Optional alternating row backgrounds for readability
- Accent line: Optional vertical accent line on the left
- Checkbox variant: Square checkboxes instead of numbers for task lists
- Bullet variant: Simple circles/dots for unordered lists""",

            "cycle": """
CYCLE DIAGRAM DESIGN:
- Circular arrangement: Elements positioned around a circle
- Center element: Optional central circle with main concept/title
- Outer elements: Evenly spaced around the circle
- Connecting arrows: Curved arrows between elements showing direction
- Element boxes: Pill-shaped or rounded rectangles
- Arrow direction: Clockwise or counter-clockwise flow
- Icon placement: Icon in each element box
- Segment colors: Each segment can have a different color from the palette
- Labels: Text inside or near each element
- Ring structure: Elements can sit on a ring/circle path
- Rotation: Elements might be rotated to face outward or all upright""",

            "matrix": """
MATRIX/QUADRANT DESIGN:
- Grid structure: 2x2 (or larger) grid with clear dividing lines
- Axis labels: Labels on left (Y-axis) and bottom (X-axis)
- Quadrant labels: Title in each quadrant (e.g., "High Impact/Low Effort")
- Grid lines: Clear horizontal and vertical dividers
- Cell content: Items positioned in appropriate cells
- Cell backgrounds: Optional different background colors per quadrant
- Axis arrows: Optional arrows at ends of axes showing direction
- Data points: Circles or markers for items in their positions
- Legend: Optional legend explaining colors/symbols
- Quadrant icons: Optional icons representing each quadrant's theme""",

            "roadmap": """
ROADMAP DESIGN:
- Timeline structure: Horizontal timeline showing phases/quarters
- Phase blocks: Rounded rectangles spanning time periods
- Swimlanes: Optional horizontal lanes for different tracks/teams
- Time markers: Month, quarter, or year markers on timeline
- Milestones: Diamond shapes at key points
- Current position: Vertical line or marker showing "now"
- Status colors:
  - Completed: Green or solid color
  - In progress: Blue or accent color
  - Planned: Gray or outline
- Phase labels: Clear labels for each phase
- Dependencies: Optional dotted lines showing dependencies
- Progress bars: Optional progress indicators within phases"""
        }

        return guidelines.get(infographic_type, "Follow standard infographic design principles.")

    def _validate_svg(self, svg_content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that SVG content is well-formed.

        Args:
            svg_content: SVG string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not svg_content:
            return False, "Empty SVG content"

        if not svg_content.strip().startswith("<svg"):
            return False, "SVG does not start with <svg tag"

        if not svg_content.strip().endswith("</svg>"):
            return False, "SVG does not end with </svg> tag"

        try:
            # Parse as XML
            ElementTree.fromstring(svg_content)
            return True, None
        except ElementTree.ParseError as e:
            return False, f"XML parse error: {str(e)}"

    def _fix_svg_issues(self, svg_content: str, width: int, height: int) -> str:
        """
        Attempt to fix common SVG issues.

        Args:
            svg_content: Potentially malformed SVG
            width: Expected width
            height: Expected height

        Returns:
            Fixed SVG content
        """
        # Ensure proper namespace
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
            svg_content = svg_content.replace(
                "<svg",
                '<svg xmlns="http://www.w3.org/2000/svg"',
                1
            )

        # Ensure viewBox
        if "viewBox" not in svg_content:
            svg_content = svg_content.replace(
                "<svg",
                f'<svg viewBox="0 0 {width} {height}"',
                1
            )

        # Fix unclosed tags (simple heuristic)
        if svg_content.count("<svg") > svg_content.count("</svg>"):
            svg_content = svg_content + "</svg>"

        return svg_content


# Global service instance
_svg_service: Optional[SVGGenerationService] = None


def get_svg_generation_service() -> SVGGenerationService:
    """Get the global SVG generation service instance."""
    global _svg_service
    if _svg_service is None:
        _svg_service = SVGGenerationService()
    return _svg_service
