"""
Infographic Type Constraints

Defines grid constraints, aspect ratios, and item limits for all infographic types.
Used by the Layout Service integration endpoint to validate requests and
determine generation strategy.
"""

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class OutputMode(str, Enum):
    """Output generation mode."""
    HTML = "html"      # Template-based HTML generation
    SVG = "svg"        # Dynamic SVG generation via Gemini 2.5 Pro


class AspectRatioType(str, Enum):
    """Aspect ratio constraint types."""
    FIXED = "fixed"       # Locked aspect ratio
    FLEXIBLE = "flexible" # Any aspect ratio allowed
    WIDE = "wide"         # Wide landscape (>2:1)
    PORTRAIT = "portrait" # Tall portrait (<1:1)
    SQUARE = "square"     # Square-ish (1:1)


@dataclass
class TypeConstraint:
    """Constraints for a single infographic type."""
    min_grid_width: int
    min_grid_height: int
    max_grid_width: int
    max_grid_height: int
    aspect_ratio_type: AspectRatioType
    aspect_ratio_value: Optional[Tuple[int, int]]  # (width, height) e.g., (3, 2)
    output_mode: OutputMode
    min_items: int
    max_items: int
    default_items: int
    description: str


# Grid unit to pixel conversion for 32x18 grid on 1920x1080 canvas
# 1920 / 32 = 60 pixels, 1080 / 18 = 60 pixels
GRID_UNIT_PIXELS = 60


# ============================================================================
# INFOGRAPHIC TYPE CONSTRAINTS
# ============================================================================

INFOGRAPHIC_TYPE_CONSTRAINTS: Dict[str, TypeConstraint] = {
    # ========================================================================
    # TEMPLATE-BASED TYPES (HTML Output)
    # ========================================================================

    "pyramid": TypeConstraint(
        min_grid_width=6,
        min_grid_height=4,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.FIXED,
        aspect_ratio_value=(3, 2),
        output_mode=OutputMode.HTML,
        min_items=3,
        max_items=6,
        default_items=4,
        description="Hierarchical pyramid with 3-6 levels"
    ),

    "funnel": TypeConstraint(
        min_grid_width=6,
        min_grid_height=4,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.FIXED,
        aspect_ratio_value=(3, 2),
        output_mode=OutputMode.HTML,
        min_items=3,
        max_items=5,
        default_items=4,
        description="Sales/conversion funnel with 3-5 stages"
    ),

    "concentric_circles": TypeConstraint(
        min_grid_width=6,
        min_grid_height=6,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.SQUARE,
        aspect_ratio_value=(1, 1),
        output_mode=OutputMode.HTML,
        min_items=3,
        max_items=5,
        default_items=4,
        description="Nested concentric circles with 3-5 rings"
    ),

    "concept_spread": TypeConstraint(
        min_grid_width=8,
        min_grid_height=4,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.WIDE,
        aspect_ratio_value=(2, 1),
        output_mode=OutputMode.HTML,
        min_items=6,
        max_items=6,
        default_items=6,
        description="Hexagon grid with 6 concepts"
    ),

    "venn": TypeConstraint(
        min_grid_width=6,
        min_grid_height=4,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.FIXED,
        aspect_ratio_value=(4, 3),
        output_mode=OutputMode.HTML,
        min_items=2,
        max_items=4,
        default_items=3,
        description="Overlapping Venn diagram with 2-4 circles"
    ),

    "comparison": TypeConstraint(
        min_grid_width=8,
        min_grid_height=4,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.WIDE,
        aspect_ratio_value=(2, 1),
        output_mode=OutputMode.HTML,
        min_items=2,
        max_items=4,
        default_items=2,
        description="Side-by-side comparison with 2-4 columns"
    ),

    # ========================================================================
    # DYNAMIC SVG TYPES (Gemini 2.5 Pro)
    # ========================================================================

    "timeline": TypeConstraint(
        min_grid_width=8,
        min_grid_height=3,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.WIDE,
        aspect_ratio_value=(3, 1),
        output_mode=OutputMode.SVG,
        min_items=3,
        max_items=10,
        default_items=5,
        description="Horizontal/vertical timeline with milestones"
    ),

    "process": TypeConstraint(
        min_grid_width=6,
        min_grid_height=3,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.FLEXIBLE,
        aspect_ratio_value=None,
        output_mode=OutputMode.SVG,
        min_items=3,
        max_items=8,
        default_items=5,
        description="Step-by-step process flow"
    ),

    "statistics": TypeConstraint(
        min_grid_width=4,
        min_grid_height=3,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.FLEXIBLE,
        aspect_ratio_value=None,
        output_mode=OutputMode.SVG,
        min_items=2,
        max_items=8,
        default_items=4,
        description="Numbers, percentages, and data visualization"
    ),

    "hierarchy": TypeConstraint(
        min_grid_width=6,
        min_grid_height=4,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.FLEXIBLE,
        aspect_ratio_value=None,
        output_mode=OutputMode.SVG,
        min_items=3,
        max_items=20,
        default_items=7,
        description="Org chart or tree structure"
    ),

    "list": TypeConstraint(
        min_grid_width=4,
        min_grid_height=4,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.PORTRAIT,
        aspect_ratio_value=(2, 3),
        output_mode=OutputMode.SVG,
        min_items=3,
        max_items=10,
        default_items=5,
        description="Visual numbered or icon list"
    ),

    "cycle": TypeConstraint(
        min_grid_width=6,
        min_grid_height=6,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.SQUARE,
        aspect_ratio_value=(1, 1),
        output_mode=OutputMode.SVG,
        min_items=3,
        max_items=8,
        default_items=5,
        description="Circular process/cycle diagram"
    ),

    "matrix": TypeConstraint(
        min_grid_width=6,
        min_grid_height=6,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.SQUARE,
        aspect_ratio_value=(1, 1),
        output_mode=OutputMode.SVG,
        min_items=4,
        max_items=16,
        default_items=9,
        description="2x2 or larger grid matrix"
    ),

    "roadmap": TypeConstraint(
        min_grid_width=8,
        min_grid_height=4,
        max_grid_width=32,
        max_grid_height=18,
        aspect_ratio_type=AspectRatioType.WIDE,
        aspect_ratio_value=(2, 1),
        output_mode=OutputMode.SVG,
        min_items=3,
        max_items=8,
        default_items=4,
        description="Project/product roadmap with phases"
    ),
}


# ============================================================================
# ITEM LIMITS BY GRID SIZE
# ============================================================================

def get_item_limits_for_grid(infographic_type: str, grid_width: int, grid_height: int) -> Dict[str, int]:
    """
    Calculate recommended item count limits based on grid size.

    Larger grids can accommodate more items with readable text.

    Args:
        infographic_type: Type of infographic
        grid_width: Grid width in units
        grid_height: Grid height in units

    Returns:
        Dict with 'min', 'max', 'recommended' item counts
    """
    constraints = INFOGRAPHIC_TYPE_CONSTRAINTS.get(infographic_type)
    if not constraints:
        raise ValueError(f"Unknown infographic type: {infographic_type}")

    # Calculate grid area
    grid_area = grid_width * grid_height

    # Size category based on area (32x18 grid = 576 max area)
    if grid_area <= 144:      # Small (e.g., 12x12, 8x16)
        size_factor = 0.6
    elif grid_area <= 288:    # Medium (e.g., 16x16, 24x12)
        size_factor = 0.8
    else:                     # Large (e.g., 24x16, 32x18)
        size_factor = 1.0

    # Adjust max items based on size
    adjusted_max = int(constraints.max_items * size_factor)
    adjusted_max = max(adjusted_max, constraints.min_items)  # Never below min

    # Recommended is midpoint
    recommended = (constraints.min_items + adjusted_max) // 2

    return {
        "min": constraints.min_items,
        "max": adjusted_max,
        "recommended": recommended,
        "type_max": constraints.max_items
    }


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_grid_constraints(infographic_type: str, grid_width: int, grid_height: int) -> Tuple[bool, Optional[str]]:
    """
    Validate that grid dimensions meet type requirements.

    Args:
        infographic_type: Type of infographic
        grid_width: Requested grid width
        grid_height: Requested grid height

    Returns:
        Tuple of (is_valid, error_message)
    """
    constraints = INFOGRAPHIC_TYPE_CONSTRAINTS.get(infographic_type)
    if not constraints:
        return False, f"Unknown infographic type: {infographic_type}"

    # Check minimum
    if grid_width < constraints.min_grid_width:
        return False, (
            f"Grid width {grid_width} is below minimum {constraints.min_grid_width} "
            f"for {infographic_type}"
        )
    if grid_height < constraints.min_grid_height:
        return False, (
            f"Grid height {grid_height} is below minimum {constraints.min_grid_height} "
            f"for {infographic_type}"
        )

    # Check maximum
    if grid_width > constraints.max_grid_width:
        return False, (
            f"Grid width {grid_width} exceeds maximum {constraints.max_grid_width} "
            f"for {infographic_type}"
        )
    if grid_height > constraints.max_grid_height:
        return False, (
            f"Grid height {grid_height} exceeds maximum {constraints.max_grid_height} "
            f"for {infographic_type}"
        )

    return True, None


def get_output_mode(infographic_type: str) -> OutputMode:
    """
    Get the output mode for an infographic type.

    Args:
        infographic_type: Type of infographic

    Returns:
        OutputMode (HTML or SVG)
    """
    constraints = INFOGRAPHIC_TYPE_CONSTRAINTS.get(infographic_type)
    if not constraints:
        raise ValueError(f"Unknown infographic type: {infographic_type}")
    return constraints.output_mode


def calculate_pixel_dimensions(grid_width: int, grid_height: int) -> Tuple[int, int]:
    """
    Convert grid units to pixel dimensions.

    Args:
        grid_width: Width in grid units
        grid_height: Height in grid units

    Returns:
        Tuple of (width_px, height_px)
    """
    return (grid_width * GRID_UNIT_PIXELS, grid_height * GRID_UNIT_PIXELS)


def get_type_constraint(infographic_type: str) -> TypeConstraint:
    """
    Get constraints for an infographic type.

    Args:
        infographic_type: Type of infographic

    Returns:
        TypeConstraint dataclass

    Raises:
        ValueError: If type is unknown
    """
    constraints = INFOGRAPHIC_TYPE_CONSTRAINTS.get(infographic_type)
    if not constraints:
        raise ValueError(f"Unknown infographic type: {infographic_type}")
    return constraints


def list_all_types() -> Dict[str, Dict[str, Any]]:
    """
    List all infographic types with their constraints.

    Returns:
        Dict of type name -> constraint summary
    """
    result = {}
    for type_name, constraint in INFOGRAPHIC_TYPE_CONSTRAINTS.items():
        result[type_name] = {
            "min_grid": f"{constraint.min_grid_width}x{constraint.min_grid_height}",
            "max_grid": f"{constraint.max_grid_width}x{constraint.max_grid_height}",
            "aspect_ratio": constraint.aspect_ratio_type.value,
            "output_mode": constraint.output_mode.value,
            "items": f"{constraint.min_items}-{constraint.max_items}",
            "description": constraint.description
        }
    return result


def get_template_types() -> list:
    """Get list of types that use HTML templates."""
    return [
        name for name, c in INFOGRAPHIC_TYPE_CONSTRAINTS.items()
        if c.output_mode == OutputMode.HTML
    ]


def get_svg_types() -> list:
    """Get list of types that use dynamic SVG generation."""
    return [
        name for name, c in INFOGRAPHIC_TYPE_CONSTRAINTS.items()
        if c.output_mode == OutputMode.SVG
    ]


# ============================================================================
# COLOR SCHEMES
# ============================================================================

COLOR_SCHEMES = {
    "professional": {
        "primary": "#1E40AF",
        "secondary": ["#3B82F6", "#60A5FA", "#93C5FD"],
        "accent": "#0D9488",
        "background": "#F8FAFC",
        "text": "#1E293B",
        "muted": "#94A3B8"
    },
    "vibrant": {
        "primary": "#7C3AED",
        "secondary": ["#A855F7", "#C084FC", "#E879F9"],
        "accent": "#F59E0B",
        "background": "#FEFCE8",
        "text": "#18181B",
        "muted": "#71717A"
    },
    "pastel": {
        "primary": "#A5B4FC",
        "secondary": ["#C4B5FD", "#DDD6FE", "#E9D5FF"],
        "accent": "#FDBA74",
        "background": "#FFF7ED",
        "text": "#44403C",
        "muted": "#A8A29E"
    },
    "monochrome": {
        "primary": "#374151",
        "secondary": ["#4B5563", "#6B7280", "#9CA3AF"],
        "accent": "#1F2937",
        "background": "#F9FAFB",
        "text": "#111827",
        "muted": "#D1D5DB"
    },
    "gradient": {
        "primary": "#667EEA",
        "secondary": ["#764BA2", "#F093FB", "#F5576C"],
        "accent": "#4FACFE",
        "background": "#FFFFFF",
        "text": "#1A1A2E",
        "muted": "#A0AEC0"
    }
}


def get_color_scheme(scheme_name: str, brand_colors: list = None) -> Dict[str, Any]:
    """
    Get color palette for a scheme.

    Args:
        scheme_name: Name of color scheme
        brand_colors: Optional brand colors to use for 'brand' scheme

    Returns:
        Color palette dict
    """
    if scheme_name == "brand" and brand_colors:
        # Use brand colors
        return {
            "primary": brand_colors[0] if len(brand_colors) > 0 else "#1E40AF",
            "secondary": brand_colors[1:4] if len(brand_colors) > 1 else ["#3B82F6"],
            "accent": brand_colors[4] if len(brand_colors) > 4 else brand_colors[0],
            "background": "#FFFFFF",
            "text": "#1E293B",
            "muted": "#94A3B8"
        }

    return COLOR_SCHEMES.get(scheme_name, COLOR_SCHEMES["professional"])
