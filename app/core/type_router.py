"""
Type Router

Routes infographic generation requests to the appropriate generator
based on the infographic type.
"""

import logging
from typing import Tuple, Optional

from app.models.layout_service_request import InfographicGenerateRequest, InfographicType
from app.generators.base_generator import BaseGenerator
from app.core.type_constraints import (
    INFOGRAPHIC_TYPE_CONSTRAINTS,
    OutputMode,
    validate_grid_constraints,
    get_output_mode,
)

logger = logging.getLogger(__name__)


class TypeRouter:
    """
    Routes infographic types to appropriate generators.

    Template-based types go to TemplateGenerator.
    SVG-based types go to SVGGenerator.
    """

    # Types that use HTML templates
    TEMPLATE_TYPES = {
        InfographicType.PYRAMID,
        InfographicType.FUNNEL,
        InfographicType.CONCENTRIC_CIRCLES,
        InfographicType.CONCEPT_SPREAD,
        InfographicType.VENN,
        InfographicType.COMPARISON,
    }

    # Types that use dynamic SVG generation
    SVG_TYPES = {
        InfographicType.TIMELINE,
        InfographicType.PROCESS,
        InfographicType.STATISTICS,
        InfographicType.HIERARCHY,
        InfographicType.LIST,
        InfographicType.CYCLE,
        InfographicType.MATRIX,
        InfographicType.ROADMAP,
    }

    def __init__(self):
        """Initialize the type router."""
        self._template_generators = {}
        self._svg_generators = {}

    def get_generator(self, infographic_type: InfographicType) -> BaseGenerator:
        """
        Get the appropriate generator for an infographic type.

        Args:
            infographic_type: The type of infographic

        Returns:
            BaseGenerator instance

        Raises:
            ValueError: If type is unknown
        """
        type_value = infographic_type.value

        # Check if it's a template type
        if infographic_type in self.TEMPLATE_TYPES:
            return self._get_template_generator(type_value)

        # Check if it's an SVG type
        if infographic_type in self.SVG_TYPES:
            return self._get_svg_generator(type_value)

        raise ValueError(f"Unknown infographic type: {type_value}")

    def _get_template_generator(self, type_value: str) -> BaseGenerator:
        """Get or create a template generator."""
        if type_value not in self._template_generators:
            from app.generators.template_generator import TemplateGenerator
            self._template_generators[type_value] = TemplateGenerator(type_value)
            logger.info(f"Created TemplateGenerator for: {type_value}")

        return self._template_generators[type_value]

    def _get_svg_generator(self, type_value: str) -> BaseGenerator:
        """Get or create an SVG generator."""
        if type_value not in self._svg_generators:
            from app.generators.svg_generator import SVGGenerator
            self._svg_generators[type_value] = SVGGenerator(type_value)
            logger.info(f"Created SVGGenerator for: {type_value}")

        return self._svg_generators[type_value]

    def validate_request(self, request: InfographicGenerateRequest) -> Tuple[bool, Optional[str]]:
        """
        Validate a generation request.

        Args:
            request: The generation request

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate type is known
        type_value = request.type.value
        if type_value not in INFOGRAPHIC_TYPE_CONSTRAINTS:
            return False, f"Unknown infographic type: {type_value}"

        # Validate grid constraints
        is_valid, error = validate_grid_constraints(
            type_value,
            request.constraints.gridWidth,
            request.constraints.gridHeight
        )
        if not is_valid:
            return False, error

        return True, None

    def get_output_mode_for_type(self, infographic_type: InfographicType) -> OutputMode:
        """
        Get the output mode for an infographic type.

        Args:
            infographic_type: The type of infographic

        Returns:
            OutputMode (HTML or SVG)
        """
        return get_output_mode(infographic_type.value)

    def is_template_type(self, infographic_type: InfographicType) -> bool:
        """Check if a type uses HTML templates."""
        return infographic_type in self.TEMPLATE_TYPES

    def is_svg_type(self, infographic_type: InfographicType) -> bool:
        """Check if a type uses dynamic SVG generation."""
        return infographic_type in self.SVG_TYPES


# Global router instance
_router: Optional[TypeRouter] = None


def get_router() -> TypeRouter:
    """Get the global type router instance."""
    global _router
    if _router is None:
        _router = TypeRouter()
    return _router
