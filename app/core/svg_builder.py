"""
SVG Builder Utilities

Helper functions for building and manipulating SVG content.
"""

from typing import Dict, Any, List, Optional, Tuple
import re


def create_svg_wrapper(
    content: str,
    width: int,
    height: int,
    background_color: Optional[str] = None
) -> str:
    """
    Create a complete SVG wrapper with proper attributes.

    Args:
        content: Inner SVG elements
        width: Width in pixels
        height: Height in pixels
        background_color: Optional background color

    Returns:
        Complete SVG string
    """
    background = ""
    if background_color:
        background = f'<rect width="{width}" height="{height}" fill="{background_color}"/>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  {background}
  {content}
</svg>"""


def create_text_element(
    text: str,
    x: int,
    y: int,
    font_size: int = 14,
    font_weight: str = "400",
    fill: str = "#1E293B",
    text_anchor: str = "start",
    dominant_baseline: str = "auto"
) -> str:
    """
    Create an SVG text element.

    Args:
        text: Text content
        x: X position
        y: Y position
        font_size: Font size in pixels
        font_weight: Font weight (400, 600, 700)
        fill: Text color
        text_anchor: Alignment (start, middle, end)
        dominant_baseline: Vertical alignment

    Returns:
        SVG text element string
    """
    return (
        f'<text x="{x}" y="{y}" '
        f'font-family="Inter, system-ui, sans-serif" '
        f'font-size="{font_size}" '
        f'font-weight="{font_weight}" '
        f'fill="{fill}" '
        f'text-anchor="{text_anchor}" '
        f'dominant-baseline="{dominant_baseline}">'
        f'{escape_xml(text)}'
        f'</text>'
    )


def create_rect(
    x: int,
    y: int,
    width: int,
    height: int,
    fill: str = "#FFFFFF",
    stroke: Optional[str] = None,
    stroke_width: int = 1,
    rx: int = 0
) -> str:
    """
    Create an SVG rectangle element.

    Args:
        x: X position
        y: Y position
        width: Width
        height: Height
        fill: Fill color
        stroke: Stroke color (optional)
        stroke_width: Stroke width
        rx: Corner radius

    Returns:
        SVG rect element string
    """
    stroke_attr = f'stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ""
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'fill="{fill}" rx="{rx}" {stroke_attr}/>'
    )


def create_circle(
    cx: int,
    cy: int,
    r: int,
    fill: str = "#FFFFFF",
    stroke: Optional[str] = None,
    stroke_width: int = 1
) -> str:
    """
    Create an SVG circle element.

    Args:
        cx: Center X
        cy: Center Y
        r: Radius
        fill: Fill color
        stroke: Stroke color (optional)
        stroke_width: Stroke width

    Returns:
        SVG circle element string
    """
    stroke_attr = f'stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" {stroke_attr}/>'


def create_line(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    stroke: str = "#CBD5E1",
    stroke_width: int = 2,
    stroke_dasharray: Optional[str] = None
) -> str:
    """
    Create an SVG line element.

    Args:
        x1: Start X
        y1: Start Y
        x2: End X
        y2: End Y
        stroke: Stroke color
        stroke_width: Stroke width
        stroke_dasharray: Dash pattern (e.g., "5,5")

    Returns:
        SVG line element string
    """
    dash_attr = f'stroke-dasharray="{stroke_dasharray}"' if stroke_dasharray else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{stroke_width}" {dash_attr}/>'
    )


def create_path(
    d: str,
    fill: str = "none",
    stroke: str = "#CBD5E1",
    stroke_width: int = 2
) -> str:
    """
    Create an SVG path element.

    Args:
        d: Path data
        fill: Fill color
        stroke: Stroke color
        stroke_width: Stroke width

    Returns:
        SVG path element string
    """
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


def create_arrow_marker(
    marker_id: str = "arrow",
    color: str = "#CBD5E1"
) -> str:
    """
    Create an SVG arrow marker definition.

    Args:
        marker_id: Marker ID for referencing
        color: Arrow color

    Returns:
        SVG defs string with marker
    """
    return f"""<defs>
  <marker id="{marker_id}" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
    <path d="M0,0 L0,6 L9,3 z" fill="{color}"/>
  </marker>
</defs>"""


def create_gradient(
    gradient_id: str,
    start_color: str,
    end_color: str,
    direction: str = "vertical"
) -> str:
    """
    Create an SVG linear gradient definition.

    Args:
        gradient_id: Gradient ID for referencing
        start_color: Start color
        end_color: End color
        direction: "vertical" or "horizontal"

    Returns:
        SVG defs string with gradient
    """
    if direction == "horizontal":
        x1, y1, x2, y2 = "0%", "0%", "100%", "0%"
    else:
        x1, y1, x2, y2 = "0%", "0%", "0%", "100%"

    return f"""<defs>
  <linearGradient id="{gradient_id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">
    <stop offset="0%" style="stop-color:{start_color};stop-opacity:1"/>
    <stop offset="100%" style="stop-color:{end_color};stop-opacity:1"/>
  </linearGradient>
</defs>"""


def create_shadow_filter(filter_id: str = "shadow") -> str:
    """
    Create an SVG drop shadow filter.

    Args:
        filter_id: Filter ID for referencing

    Returns:
        SVG defs string with filter
    """
    return f"""<defs>
  <filter id="{filter_id}" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.15"/>
  </filter>
</defs>"""


def create_group(content: str, transform: Optional[str] = None, filter: Optional[str] = None) -> str:
    """
    Create an SVG group element.

    Args:
        content: Group content
        transform: Transform attribute (e.g., "translate(10,10)")
        filter: Filter reference (e.g., "url(#shadow)")

    Returns:
        SVG group element string
    """
    attrs = []
    if transform:
        attrs.append(f'transform="{transform}"')
    if filter:
        attrs.append(f'filter="{filter}"')

    attrs_str = " ".join(attrs)
    return f"<g {attrs_str}>{content}</g>"


def escape_xml(text: str) -> str:
    """
    Escape special XML characters.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def calculate_text_width(text: str, font_size: int) -> int:
    """
    Estimate text width in pixels.

    This is an approximation since actual rendering depends on font.

    Args:
        text: Text content
        font_size: Font size in pixels

    Returns:
        Estimated width in pixels
    """
    # Average character width is roughly 0.6 of font size for sans-serif
    return int(len(text) * font_size * 0.6)


def wrap_text(text: str, max_width: int, font_size: int) -> List[str]:
    """
    Wrap text into multiple lines.

    Args:
        text: Text to wrap
        max_width: Maximum width in pixels
        font_size: Font size in pixels

    Returns:
        List of text lines
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        if calculate_text_width(test_line, font_size) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def create_multiline_text(
    lines: List[str],
    x: int,
    y: int,
    font_size: int = 14,
    line_height: float = 1.4,
    **kwargs
) -> str:
    """
    Create SVG text with multiple tspan elements for lines.

    Args:
        lines: List of text lines
        x: X position
        y: Y position (of first line)
        font_size: Font size
        line_height: Line height multiplier
        **kwargs: Additional attributes for create_text_element

    Returns:
        SVG text element with tspans
    """
    if not lines:
        return ""

    tspans = []
    for i, line in enumerate(lines):
        dy = 0 if i == 0 else int(font_size * line_height)
        tspans.append(f'<tspan x="{x}" dy="{dy}">{escape_xml(line)}</tspan>')

    font_weight = kwargs.get("font_weight", "400")
    fill = kwargs.get("fill", "#1E293B")
    text_anchor = kwargs.get("text_anchor", "start")

    return (
        f'<text x="{x}" y="{y}" '
        f'font-family="Inter, system-ui, sans-serif" '
        f'font-size="{font_size}" '
        f'font-weight="{font_weight}" '
        f'fill="{fill}" '
        f'text-anchor="{text_anchor}">'
        f'{"".join(tspans)}'
        f'</text>'
    )


def calculate_positions_circular(
    count: int,
    cx: int,
    cy: int,
    radius: int,
    start_angle: float = -90
) -> List[Tuple[int, int]]:
    """
    Calculate evenly spaced positions around a circle.

    Args:
        count: Number of positions
        cx: Center X
        cy: Center Y
        radius: Radius
        start_angle: Starting angle in degrees (-90 = top)

    Returns:
        List of (x, y) tuples
    """
    import math

    positions = []
    angle_step = 360 / count

    for i in range(count):
        angle = math.radians(start_angle + i * angle_step)
        x = cx + int(radius * math.cos(angle))
        y = cy + int(radius * math.sin(angle))
        positions.append((x, y))

    return positions


def calculate_positions_grid(
    count: int,
    x_start: int,
    y_start: int,
    item_width: int,
    item_height: int,
    columns: int,
    gap_x: int = 20,
    gap_y: int = 20
) -> List[Tuple[int, int]]:
    """
    Calculate grid positions for items.

    Args:
        count: Number of items
        x_start: Starting X
        y_start: Starting Y
        item_width: Width of each item
        item_height: Height of each item
        columns: Number of columns
        gap_x: Horizontal gap
        gap_y: Vertical gap

    Returns:
        List of (x, y) tuples
    """
    positions = []

    for i in range(count):
        col = i % columns
        row = i // columns
        x = x_start + col * (item_width + gap_x)
        y = y_start + row * (item_height + gap_y)
        positions.append((x, y))

    return positions
