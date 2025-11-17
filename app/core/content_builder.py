"""
Content Builder for Illustrator Service v1.0
============================================

Builds layout-specific response structures that match Layout Builder's
field expectations. Follows Text Service v1.2 pattern for format ownership.

Format Ownership (from SERVICE_INTEGRATION_OVERVIEW.md):
- Layout Builder: Owns slide_title, subtitle (via element_1)
- Illustrator Service: Owns content HTML (rich_content, element_4, element_3, element_2)
"""

from typing import Dict, Optional


class ContentBuilder:
    """
    Builds layout-specific response content dictionaries.

    Each layout has different field requirements:
    - L25: slide_title + subtitle + rich_content
    - L01: slide_title + element_1 + element_4 + element_3
    - L02: slide_title + element_1 + element_3 + element_2
    """

    @staticmethod
    def build_l25_response(
        html: str,
        title: str,
        subtitle: str = ""
    ) -> Dict[str, str]:
        """
        Build L25 layout response structure.

        L25 Format:
        - slide_title: Main slide title
        - subtitle: Optional subtitle
        - rich_content: Full HTML content (1800×720px)

        Args:
            html: Generated illustration HTML
            title: Slide title
            subtitle: Optional subtitle

        Returns:
            Dictionary with L25 fields
        """
        return {
            "slide_title": title,
            "subtitle": subtitle,
            "rich_content": html
        }

    @staticmethod
    def build_l01_response(
        diagram_html: str,
        title: str,
        subtitle: str = "",
        body_text: str = ""
    ) -> Dict[str, str]:
        """
        Build L01 layout response structure.

        L01 Format:
        - slide_title: Main slide title
        - element_1: Subtitle text
        - element_4: Diagram HTML (1800×600px, centered)
        - element_3: Body text below diagram

        Args:
            diagram_html: Generated diagram HTML
            title: Slide title
            subtitle: Optional subtitle for element_1
            body_text: Optional explanatory text for element_3

        Returns:
            Dictionary with L01 fields
        """
        return {
            "slide_title": title,
            "element_1": subtitle,
            "element_4": diagram_html,  # Primary diagram area
            "element_3": body_text
        }

    @staticmethod
    def build_l02_response(
        diagram_html: str,
        text_html: str,
        title: str,
        subtitle: str = ""
    ) -> Dict[str, str]:
        """
        Build L02 layout response structure.

        L02 Format:
        - slide_title: Main slide title
        - element_1: Subtitle text
        - element_3: Diagram HTML (1260×720px, left side)
        - element_2: Explanatory text HTML (480px width, right side)

        Args:
            diagram_html: Generated diagram HTML
            text_html: Explanatory text HTML
            title: Slide title
            subtitle: Optional subtitle for element_1

        Returns:
            Dictionary with L02 fields
        """
        return {
            "slide_title": title,
            "element_1": subtitle,
            "element_3": diagram_html,  # Diagram left (1260×720px)
            "element_2": text_html      # Text right (480px wide)
        }

    @staticmethod
    def build_response(
        layout_id: str,
        title: str,
        **kwargs
    ) -> Dict[str, str]:
        """
        Build response for any layout type (convenience method).

        Args:
            layout_id: Layout identifier (L25, L01, L02)
            title: Slide title
            **kwargs: Layout-specific arguments
                L25: html, subtitle
                L01: diagram_html, subtitle, body_text
                L02: diagram_html, text_html, subtitle

        Returns:
            Dictionary with layout-specific fields

        Raises:
            ValueError: If layout_id is unsupported
        """
        if layout_id == "L25":
            return ContentBuilder.build_l25_response(
                html=kwargs.get("html", ""),
                title=title,
                subtitle=kwargs.get("subtitle", "")
            )
        elif layout_id == "L01":
            return ContentBuilder.build_l01_response(
                diagram_html=kwargs.get("diagram_html", ""),
                title=title,
                subtitle=kwargs.get("subtitle", ""),
                body_text=kwargs.get("body_text", "")
            )
        elif layout_id == "L02":
            return ContentBuilder.build_l02_response(
                diagram_html=kwargs.get("diagram_html", ""),
                text_html=kwargs.get("text_html", ""),
                title=title,
                subtitle=kwargs.get("subtitle", "")
            )
        else:
            raise ValueError(f"Unsupported layout_id: {layout_id}")

    @staticmethod
    def wrap_for_layout(
        html: str,
        layout_id: str,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ) -> str:
        """
        Wrap HTML with layout-specific container constraints.

        Ensures generated HTML fits within layout dimensions using
        percentage-based sizing with max constraints.

        Args:
            html: Generated HTML content
            layout_id: Layout identifier (L25, L01, L02)
            max_width: Optional max width override
            max_height: Optional max height override

        Returns:
            HTML wrapped in layout-appropriate container
        """
        # Get default dimensions for layout
        dimensions = {
            "L25": (1800, 720),
            "L01": (1800, 600),
            "L02": (1260, 720)  # Diagram area
        }

        default_width, default_height = dimensions.get(layout_id, (1800, 720))
        max_w = max_width or default_width
        max_h = max_height or default_height

        wrapper = f"""<div style="width: 100%; height: 100%; max-width: {max_w}px; max-height: {max_h}px; margin: 0; padding: 0; box-sizing: border-box;">
{html}
</div>"""

        return wrapper
