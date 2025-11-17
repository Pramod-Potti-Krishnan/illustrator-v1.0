"""
Layout Selector for Illustrator Service v1.0
============================================

Maps illustration types to appropriate layouts (L01, L02, L25) based on
content complexity and visual requirements.

Layout Strategy:
- L25: Full rich_content (1800×720px) - Complex integrated content
- L01: Centered diagram (1800×600px) - Simple self-explanatory visuals
- L02: Diagram left + text right (1260×720px + 480px) - Complex diagrams needing explanation
"""

from typing import Dict, Tuple, List


class LayoutSelector:
    """Maps illustration types to appropriate layouts and provides layout metadata"""

    # Primary layout mapping for 15 priority illustrations
    LAYOUT_MAP = {
        # L25: Full rich_content (1800×720px) - 5 illustrations
        # Best for: Integrated content with text + diagram in single rich HTML
        "swot_2x2": "L25",
        "ansoff_matrix": "L25",
        "kpi_dashboard": "L25",
        "bcg_matrix": "L25",
        "porters_five_forces": "L25",

        # L01: Centered diagram (1800×600px) - 6 illustrations
        # Best for: Simple diagrams that are self-explanatory
        "pros_cons": "L01",
        "process_flow_horizontal": "L01",
        "pyramid_3tier": "L01",
        "funnel_4stage": "L01",
        "venn_2circle": "L01",
        "before_after": "L01",

        # L02: Diagram left + text right (1260×720px + 480px) - 4 illustrations
        # Best for: Complex diagrams that need explanatory text
        "timeline_horizontal": "L02",
        "org_chart": "L02",
        "value_chain": "L02",
        "circular_process": "L02"
    }

    # Layout dimensions and field information
    LAYOUT_SPECS = {
        "L25": {
            "dimensions": {"width": 1800, "height": 720},
            "aspect_ratio": "5:2",
            "primary_field": "rich_content",
            "fields": ["slide_title", "subtitle", "rich_content"],
            "description": "Full rich content area for integrated text+diagram"
        },
        "L01": {
            "dimensions": {"width": 1800, "height": 600},
            "aspect_ratio": "3:1",
            "primary_field": "element_4",
            "fields": ["slide_title", "element_1", "element_4", "element_3"],
            "description": "Centered diagram with title and body text"
        },
        "L02": {
            "dimensions": {
                "diagram": {"width": 1260, "height": 720},
                "text": {"width": 480, "height": 720}
            },
            "aspect_ratio": "diagram 7:4, text 2:3",
            "primary_fields": ["element_3", "element_2"],
            "fields": ["slide_title", "element_1", "element_3", "element_2"],
            "description": "Diagram left (element_3) + explanatory text right (element_2)"
        }
    }

    @classmethod
    def get_layout(cls, illustration_type: str) -> str:
        """
        Get appropriate layout for illustration type.

        Args:
            illustration_type: Type of illustration (e.g., "swot_2x2")

        Returns:
            Layout ID (L25, L01, or L02), defaults to L25
        """
        return cls.LAYOUT_MAP.get(illustration_type, "L25")

    @classmethod
    def get_dimensions(cls, layout_id: str) -> Dict[str, int]:
        """
        Get dimensions for a layout.

        Args:
            layout_id: Layout identifier (L25, L01, L02)

        Returns:
            Dictionary with width and height in pixels
        """
        specs = cls.LAYOUT_SPECS.get(layout_id)
        if not specs:
            return {"width": 1800, "height": 720}  # Default to L25

        # Handle L02's dual dimensions
        if layout_id == "L02":
            return specs["dimensions"]["diagram"]

        return specs["dimensions"]

    @classmethod
    def get_fields(cls, layout_id: str) -> List[str]:
        """
        Get required fields for a layout.

        Args:
            layout_id: Layout identifier (L25, L01, L02)

        Returns:
            List of field names for this layout
        """
        specs = cls.LAYOUT_SPECS.get(layout_id, cls.LAYOUT_SPECS["L25"])
        return specs["fields"]

    @classmethod
    def get_primary_content_field(cls, layout_id: str) -> str:
        """
        Get the primary content field for a layout.

        Args:
            layout_id: Layout identifier (L25, L01, L02)

        Returns:
            Primary field name where main content goes
        """
        specs = cls.LAYOUT_SPECS.get(layout_id, cls.LAYOUT_SPECS["L25"])

        # L02 has two primary fields, return diagram field
        if layout_id == "L02":
            return specs["primary_fields"][0]  # element_3 (diagram)

        return specs["primary_field"]

    @classmethod
    def supports_illustration(cls, illustration_type: str) -> bool:
        """
        Check if illustration type is supported.

        Args:
            illustration_type: Type of illustration

        Returns:
            True if supported, False otherwise
        """
        return illustration_type in cls.LAYOUT_MAP

    @classmethod
    def get_all_illustrations_by_layout(cls) -> Dict[str, List[str]]:
        """
        Get all illustrations grouped by layout.

        Returns:
            Dictionary mapping layout_id to list of illustration types
        """
        result = {"L25": [], "L01": [], "L02": []}
        for illust_type, layout_id in cls.LAYOUT_MAP.items():
            result[layout_id].append(illust_type)
        return result

    @classmethod
    def get_layout_info(cls, illustration_type: str) -> Dict:
        """
        Get complete layout information for an illustration type.

        Args:
            illustration_type: Type of illustration

        Returns:
            Dictionary with layout_id, dimensions, fields, and metadata
        """
        layout_id = cls.get_layout(illustration_type)
        specs = cls.LAYOUT_SPECS.get(layout_id, cls.LAYOUT_SPECS["L25"])

        return {
            "layout_id": layout_id,
            "dimensions": cls.get_dimensions(layout_id),
            "fields": specs["fields"],
            "primary_field": cls.get_primary_content_field(layout_id),
            "description": specs["description"],
            "aspect_ratio": specs["aspect_ratio"]
        }
