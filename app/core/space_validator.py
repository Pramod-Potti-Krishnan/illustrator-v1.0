"""
Space Validator for Director Integration

Validates whether visualizations fit in the available space
provided by the layout.
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from app.models.coordination_models import AvailableSpace

logger = logging.getLogger(__name__)


@dataclass
class SpaceValidationResult:
    """Result of space validation."""
    fits_well: bool
    estimated_fill_percent: int
    required_width: int
    required_height: int
    available_width: int
    available_height: int
    reason: str


class SpaceValidator:
    """
    Validates space requirements for visual types.

    Checks if the requested visualization can fit in the
    available space provided by the layout.
    """

    # Minimum space requirements for each visual type (width, height)
    MIN_REQUIREMENTS = {
        "pyramid": {"width": 800, "height": 600},
        "funnel": {"width": 700, "height": 600},
        "concentric_circles": {"width": 700, "height": 700},
        "concept_spread": {"width": 1000, "height": 700},
    }

    # Optimal space requirements (gives best visual results)
    OPTIMAL_REQUIREMENTS = {
        "pyramid": {"width": 1200, "height": 700},
        "funnel": {"width": 1000, "height": 700},
        "concentric_circles": {"width": 900, "height": 700},
        "concept_spread": {"width": 1800, "height": 840},
    }

    # Aspect ratio preferences (width/height)
    ASPECT_RATIOS = {
        "pyramid": {"min": 1.2, "max": 2.0, "optimal": 1.7},
        "funnel": {"min": 1.0, "max": 1.8, "optimal": 1.4},
        "concentric_circles": {"min": 0.9, "max": 1.3, "optimal": 1.0},
        "concept_spread": {"min": 1.5, "max": 2.5, "optimal": 2.14},
    }

    def validate(
        self,
        visual_type: str,
        available_space: Optional[AvailableSpace],
        item_count: int = 4
    ) -> SpaceValidationResult:
        """
        Validate if visual type fits in available space.

        Args:
            visual_type: The type of visualization
            available_space: Available space from layout (optional)
            item_count: Number of items to render

        Returns:
            SpaceValidationResult with fit status and utilization
        """
        if available_space is None:
            # No space constraints provided - assume it fits
            return SpaceValidationResult(
                fits_well=True,
                estimated_fill_percent=80,
                required_width=self.OPTIMAL_REQUIREMENTS.get(
                    visual_type, {"width": 1000}
                )["width"],
                required_height=self.OPTIMAL_REQUIREMENTS.get(
                    visual_type, {"height": 700}
                )["height"],
                available_width=1800,  # Default slide width
                available_height=750,  # Default content zone height
                reason="No space constraints provided - using defaults",
            )

        # Get requirements
        min_req = self.MIN_REQUIREMENTS.get(
            visual_type,
            {"width": 700, "height": 600}
        )
        optimal_req = self.OPTIMAL_REQUIREMENTS.get(
            visual_type,
            {"width": 1000, "height": 700}
        )

        # Adjust requirements based on item count
        adjusted_min = self._adjust_for_item_count(min_req, item_count, visual_type)
        adjusted_optimal = self._adjust_for_item_count(optimal_req, item_count, visual_type)

        avail_width = available_space.width
        avail_height = available_space.height

        # Check if minimum requirements are met
        fits_minimum = (
            avail_width >= adjusted_min["width"] and
            avail_height >= adjusted_min["height"]
        )

        if not fits_minimum:
            return SpaceValidationResult(
                fits_well=False,
                estimated_fill_percent=0,
                required_width=adjusted_min["width"],
                required_height=adjusted_min["height"],
                available_width=avail_width,
                available_height=avail_height,
                reason=f"Space too small: need {adjusted_min['width']}x{adjusted_min['height']}, "
                       f"have {avail_width}x{avail_height}",
            )

        # Calculate fill percentage
        fill_percent = self._calculate_fill_percent(
            adjusted_optimal, avail_width, avail_height
        )

        # Check aspect ratio
        aspect_ok, aspect_reason = self._check_aspect_ratio(
            visual_type, avail_width, avail_height
        )

        # Determine if it fits well
        fits_well = fill_percent >= 50 and aspect_ok

        reason = self._build_reason(
            fits_well, fill_percent, aspect_ok, aspect_reason, visual_type
        )

        return SpaceValidationResult(
            fits_well=fits_well,
            estimated_fill_percent=fill_percent,
            required_width=adjusted_optimal["width"],
            required_height=adjusted_optimal["height"],
            available_width=avail_width,
            available_height=avail_height,
            reason=reason,
        )

    def _adjust_for_item_count(
        self,
        requirements: Dict[str, int],
        item_count: int,
        visual_type: str
    ) -> Dict[str, int]:
        """Adjust space requirements based on item count."""
        # Base adjustments
        width = requirements["width"]
        height = requirements["height"]

        if visual_type == "pyramid":
            # Pyramids need more height with more levels
            if item_count > 4:
                height = int(height * 1.15)
            if item_count > 5:
                height = int(height * 1.1)

        elif visual_type == "funnel":
            # Funnels need more height with more stages
            if item_count > 4:
                height = int(height * 1.2)

        elif visual_type == "concentric_circles":
            # Circles need more space with more rings
            if item_count > 4:
                width = int(width * 1.15)
                height = int(height * 1.15)

        return {"width": width, "height": height}

    def _calculate_fill_percent(
        self,
        optimal: Dict[str, int],
        avail_width: int,
        avail_height: int
    ) -> int:
        """Calculate how well the space will be utilized."""
        # Calculate based on how optimal dimensions compare to available
        width_ratio = min(avail_width / optimal["width"], 1.5)
        height_ratio = min(avail_height / optimal["height"], 1.5)

        # If available space is much larger than optimal, fill percent decreases
        if avail_width > optimal["width"] * 1.2 and avail_height > optimal["height"] * 1.2:
            # Large space - visual will look smaller
            fill = int(70 * (optimal["width"] / avail_width) * (optimal["height"] / avail_height))
        elif avail_width >= optimal["width"] and avail_height >= optimal["height"]:
            # Good fit
            fill = int(min(width_ratio, height_ratio) * 85)
        else:
            # Smaller than optimal - will fill well but may be cramped
            fill = int(min(width_ratio, height_ratio) * 100)

        return max(30, min(100, fill))

    def _check_aspect_ratio(
        self,
        visual_type: str,
        width: int,
        height: int
    ) -> Tuple[bool, str]:
        """Check if aspect ratio is appropriate for visual type."""
        if height == 0:
            return False, "Invalid height"

        aspect = width / height
        ratio_prefs = self.ASPECT_RATIOS.get(
            visual_type,
            {"min": 0.8, "max": 2.0, "optimal": 1.5}
        )

        if ratio_prefs["min"] <= aspect <= ratio_prefs["max"]:
            if abs(aspect - ratio_prefs["optimal"]) < 0.3:
                return True, "Optimal aspect ratio"
            return True, "Acceptable aspect ratio"
        else:
            if aspect < ratio_prefs["min"]:
                return False, f"Too narrow for {visual_type}"
            else:
                return False, f"Too wide for {visual_type}"

    def _build_reason(
        self,
        fits_well: bool,
        fill_percent: int,
        aspect_ok: bool,
        aspect_reason: str,
        visual_type: str
    ) -> str:
        """Build human-readable reason string."""
        if fits_well:
            if fill_percent >= 80:
                return f"Excellent fit for {visual_type} - {fill_percent}% utilization"
            elif fill_percent >= 60:
                return f"Good fit for {visual_type} - {fill_percent}% utilization"
            else:
                return f"Adequate fit for {visual_type} - {fill_percent}% utilization"
        else:
            if not aspect_ok:
                return f"{aspect_reason} - consider different layout"
            return f"Poor space utilization ({fill_percent}%) for {visual_type}"

    def get_recommended_space(
        self, visual_type: str, item_count: int = 4
    ) -> Dict[str, int]:
        """Get recommended space for a visual type."""
        optimal = self.OPTIMAL_REQUIREMENTS.get(
            visual_type,
            {"width": 1000, "height": 700}
        )
        return self._adjust_for_item_count(optimal, item_count, visual_type)
