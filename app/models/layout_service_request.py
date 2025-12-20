"""
Request Models for Layout Service Integration

Defines the request schema for the unified infographic generation endpoint.
Aligns with the Layout Service API specification.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class InfographicType(str, Enum):
    """
    Supported infographic types.

    Template-based (HTML output):
    - pyramid, funnel, concentric_circles, concept_spread, venn, comparison

    Dynamic SVG (Gemini 2.5 Pro):
    - timeline, process, statistics, hierarchy, list, cycle, matrix, roadmap
    """
    # Template-based types (HTML output)
    PYRAMID = "pyramid"
    FUNNEL = "funnel"
    CONCENTRIC_CIRCLES = "concentric_circles"
    CONCEPT_SPREAD = "concept_spread"
    VENN = "venn"
    COMPARISON = "comparison"

    # Dynamic SVG types (Gemini 2.5 Pro)
    TIMELINE = "timeline"
    PROCESS = "process"
    STATISTICS = "statistics"
    HIERARCHY = "hierarchy"
    LIST = "list"
    CYCLE = "cycle"
    MATRIX = "matrix"
    ROADMAP = "roadmap"


class ColorScheme(str, Enum):
    """Color scheme options for infographics."""
    BRAND = "brand"              # Use brand colors from context
    PROFESSIONAL = "professional"  # Blues and grays
    VIBRANT = "vibrant"          # Bold, saturated colors
    PASTEL = "pastel"            # Soft, muted colors
    MONOCHROME = "monochrome"    # Single color variations
    GRADIENT = "gradient"        # Gradient transitions
    CUSTOM = "custom"            # Custom colors provided


class IconStyle(str, Enum):
    """Icon style options for infographics."""
    OUTLINED = "outlined"        # Line icons
    FILLED = "filled"            # Solid icons
    DUOTONE = "duotone"          # Two-tone icons
    MINIMAL = "minimal"          # Simple geometric
    ILLUSTRATED = "illustrated"  # Detailed illustrations
    EMOJI = "emoji"              # Emoji-based
    NONE = "none"                # No icons


class Density(str, Enum):
    """Content density options."""
    COMPACT = "compact"
    BALANCED = "balanced"
    SPACIOUS = "spacious"


class Orientation(str, Enum):
    """Layout orientation options."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    AUTO = "auto"


class GridConstraints(BaseModel):
    """
    Grid size constraints from the Layout Service.

    The presentation canvas is a 32x18 grid (1920x1080 at 60px per unit).
    Each grid unit represents a portion of the slide.
    Elements can occupy any subsection of this grid.
    """
    gridWidth: int = Field(
        ...,
        ge=1,
        le=32,
        description="Element width in grid units (1-32)"
    )
    gridHeight: int = Field(
        ...,
        ge=1,
        le=18,
        description="Element height in grid units (1-18)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "gridWidth": 24,
                "gridHeight": 12
            }
        }


class StyleOptions(BaseModel):
    """Visual style options for the infographic."""
    colorScheme: ColorScheme = Field(
        default=ColorScheme.PROFESSIONAL,
        description="Color scheme to use"
    )
    iconStyle: IconStyle = Field(
        default=IconStyle.EMOJI,
        description="Icon style: emoji, outlined, filled, etc."
    )
    density: Density = Field(
        default=Density.BALANCED,
        description="Content density: compact, balanced, spacious"
    )
    orientation: Orientation = Field(
        default=Orientation.AUTO,
        description="Layout orientation: horizontal, vertical, auto"
    )
    customColors: Optional[List[str]] = Field(
        default=None,
        description="Custom color palette (hex values) when colorScheme is 'custom'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "colorScheme": "professional",
                "iconStyle": "emoji",
                "density": "balanced",
                "orientation": "horizontal"
            }
        }


class ContentOptions(BaseModel):
    """Options controlling content generation."""
    itemCount: Optional[int] = Field(
        default=None,
        ge=2,
        le=20,
        description="Number of items to generate (auto-detected if not set)"
    )
    includeIcons: bool = Field(
        default=True,
        description="Include icons/emojis in the infographic"
    )
    includeDescriptions: bool = Field(
        default=True,
        description="Include description text for items"
    )
    includeNumbers: bool = Field(
        default=False,
        description="Include numbering for items"
    )
    maxTextLength: Optional[int] = Field(
        default=None,
        ge=10,
        le=500,
        description="Maximum characters per text element"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "itemCount": 5,
                "includeIcons": True,
                "includeDescriptions": True,
                "includeNumbers": False
            }
        }


class PresentationContext(BaseModel):
    """Context from the presentation for narrative continuity."""
    presentationTitle: Optional[str] = Field(
        default=None,
        description="Title of the presentation"
    )
    presentationTheme: Optional[str] = Field(
        default=None,
        description="Theme/template name of the presentation"
    )
    slideTitle: Optional[str] = Field(
        default=None,
        description="Title of the current slide"
    )
    slideIndex: Optional[int] = Field(
        default=None,
        ge=0,
        description="Index of the current slide (0-based)"
    )
    brandColors: Optional[List[str]] = Field(
        default=None,
        description="Brand color palette (hex values)"
    )
    industry: Optional[str] = Field(
        default=None,
        description="Industry context for content generation"
    )
    audience: Optional[str] = Field(
        default=None,
        description="Target audience for the presentation"
    )
    tone: Optional[str] = Field(
        default="professional",
        description="Writing tone: professional, casual, technical, etc."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentationTitle": "Q4 Business Strategy",
                "slideTitle": "Our Journey",
                "slideIndex": 5,
                "brandColors": ["#1E40AF", "#3B82F6", "#60A5FA"],
                "industry": "Technology",
                "audience": "executives",
                "tone": "professional"
            }
        }


class InfographicGenerateRequest(BaseModel):
    """
    Request model for the unified infographic generation endpoint.

    Called by the Layout Service to generate infographic SVG/HTML content.
    """
    # Required fields
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Description of infographic content (e.g., 'Show our company's 5-year journey')"
    )
    type: InfographicType = Field(
        ...,
        description="Infographic type (timeline, pyramid, funnel, etc.)"
    )

    # Identifiers from Layout Service
    presentationId: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the presentation"
    )
    slideId: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the slide"
    )
    elementId: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the element in the layout"
    )

    # Context
    context: PresentationContext = Field(
        default_factory=PresentationContext,
        description="Presentation context for narrative continuity"
    )

    # Constraints
    constraints: GridConstraints = Field(
        ...,
        description="Grid size constraints from the canvas"
    )

    # Style options
    style: StyleOptions = Field(
        default_factory=StyleOptions,
        description="Visual style options"
    )

    # Content options
    contentOptions: ContentOptions = Field(
        default_factory=ContentOptions,
        description="Content generation options"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Show our company's 5-year growth journey with key milestones",
                "type": "timeline",
                "presentationId": "pres_abc123",
                "slideId": "slide_xyz789",
                "elementId": "elem_001",
                "context": {
                    "presentationTitle": "Annual Review 2024",
                    "slideTitle": "Our Journey",
                    "slideIndex": 3,
                    "brandColors": ["#1E40AF", "#10B981"],
                    "industry": "Technology",
                    "tone": "professional"
                },
                "constraints": {
                    "gridWidth": 24,
                    "gridHeight": 10
                },
                "style": {
                    "colorScheme": "brand",
                    "iconStyle": "emoji",
                    "density": "balanced",
                    "orientation": "horizontal"
                },
                "contentOptions": {
                    "itemCount": 5,
                    "includeIcons": True,
                    "includeDescriptions": True
                }
            }
        }
