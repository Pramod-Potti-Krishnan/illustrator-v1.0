"""
Concentric Circles Content Validator

Validates that generated concentric circles content meets character count constraints.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re

logger = logging.getLogger(__name__)


class ConcentricCirclesValidator:
    """Validates concentric circles content against character constraints"""

    def __init__(self, constraints_path: str = None):
        """
        Initialize validator with constraints file.

        Args:
            constraints_path: Path to concentric_circles_constraints.json
        """
        if constraints_path is None:
            # Default path relative to this file
            base_dir = Path(__file__).parent.parent
            constraints_path = base_dir / "variant_specs" / "concentric_circles_constraints.json"

        self.constraints_path = Path(constraints_path)
        self.constraints = self._load_constraints()

    def _load_constraints(self) -> Dict[str, Dict[str, Dict[str, list]]]:
        """Load character constraints from JSON file"""
        try:
            with open(self.constraints_path, 'r') as f:
                constraints = json.load(f)
            logger.info(f"Loaded concentric circles constraints from {self.constraints_path}")
            return constraints
        except Exception as e:
            logger.error(f"Failed to load constraints: {e}")
            raise

    def get_constraints_for_circles(self, num_circles: int) -> Dict[str, Dict[str, list]]:
        """
        Get character constraints for a specific number of circles.

        Args:
            num_circles: Number of concentric circles (3-5)

        Returns:
            Dict mapping circle keys to constraints
        """
        circles_key = f"concentric_circles_{num_circles}"
        if circles_key not in self.constraints:
            raise ValueError(f"No constraints defined for {num_circles}-circle variant")

        return self.constraints[circles_key]

    def validate_content(
        self,
        content: Dict[str, str],
        num_circles: int
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate generated content against character constraints.

        Args:
            content: Dict with circle_N_label and legend_N_bullet_M keys
            num_circles: Number of concentric circles

        Returns:
            Tuple of (is_valid, violations_list)
        """
        constraints = self.get_constraints_for_circles(num_circles)
        violations = []

        # Check circle labels
        for circle_num in range(1, num_circles + 1):
            label_key = f"circle_{circle_num}_label"

            if label_key in content and label_key in constraints:
                label_text = content[label_key]
                # Strip HTML tags (like <br>) for character counting
                label_text_no_html = re.sub(r'<[^>]+>', '', label_text)
                label_length = len(label_text_no_html)
                min_chars, max_chars = constraints[label_key]["min_chars"], constraints[label_key]["max_chars"]

                if label_length < min_chars or label_length > max_chars:
                    violations.append({
                        "field": label_key,
                        "actual_length": label_length,
                        "min_required": min_chars,
                        "max_required": max_chars,
                        "status": "under" if label_length < min_chars else "over",
                        "text": label_text[:50] + "..." if len(label_text) > 50 else label_text
                    })

        # Check legend bullets
        # Determine number of bullets per legend based on num_circles
        bullets_per_legend = {3: 5, 4: 4, 5: 3}
        num_bullets = bullets_per_legend.get(num_circles, 3)

        for legend_num in range(1, num_circles + 1):
            for bullet_num in range(1, num_bullets + 1):
                bullet_key = f"legend_{legend_num}_bullet_{bullet_num}"

                if bullet_key in content:
                    bullet_text = content[bullet_key]
                    # Strip HTML tags for character counting
                    bullet_text_no_html = re.sub(r'<[^>]+>', '', bullet_text)
                    bullet_length = len(bullet_text_no_html)

                    # Get constraints for this bullet
                    if bullet_key in constraints:
                        min_chars, max_chars = constraints[bullet_key]["min_chars"], constraints[bullet_key]["max_chars"]

                        if bullet_length < min_chars or bullet_length > max_chars:
                            violations.append({
                                "field": bullet_key,
                                "actual_length": bullet_length,
                                "min_required": min_chars,
                                "max_required": max_chars,
                                "status": "under" if bullet_length < min_chars else "over",
                                "text": bullet_text[:50] + "..." if len(bullet_text) > 50 else bullet_text
                            })

        is_valid = len(violations) == 0
        return is_valid, violations

    def get_character_counts(
        self,
        content: Dict[str, str],
        num_circles: int
    ) -> Dict[str, Dict[str, int]]:
        """
        Get character counts for all content fields.

        Args:
            content: Dict with circle and legend content
            num_circles: Number of concentric circles

        Returns:
            Dict mapping field names to character counts
        """
        counts = {}

        # Count circle labels
        for circle_num in range(1, num_circles + 1):
            label_key = f"circle_{circle_num}_label"
            if label_key in content:
                # Strip HTML for accurate counting
                label_text_no_html = re.sub(r'<[^>]+>', '', content[label_key])
                counts[label_key] = len(label_text_no_html)

        # Count legend bullets
        bullets_per_legend = {3: 5, 4: 4, 5: 3}
        num_bullets = bullets_per_legend.get(num_circles, 3)

        for legend_num in range(1, num_circles + 1):
            for bullet_num in range(1, num_bullets + 1):
                bullet_key = f"legend_{legend_num}_bullet_{bullet_num}"
                if bullet_key in content:
                    # Strip HTML for accurate counting
                    bullet_text_no_html = re.sub(r'<[^>]+>', '', content[bullet_key])
                    counts[bullet_key] = len(bullet_text_no_html)

        return counts

    def format_validation_report(
        self,
        violations: List[Dict[str, Any]]
    ) -> str:
        """
        Format validation violations into a readable report.

        Args:
            violations: List of violation dicts

        Returns:
            Formatted string report
        """
        if not violations:
            return "✅ All content meets character constraints"

        report = f"❌ Found {len(violations)} constraint violation(s):\n\n"

        for i, violation in enumerate(violations, 1):
            report += f"{i}. {violation['field']}:\n"
            report += f"   - Actual: {violation['actual_length']} chars\n"
            report += f"   - Required: {violation['min_required']}-{violation['max_required']} chars\n"
            report += f"   - Status: {violation['status'].upper()}\n"
            report += f"   - Text: \"{violation['text']}\"\n\n"

        return report


# Global validator instance
_validator: ConcentricCirclesValidator = None


def get_validator() -> ConcentricCirclesValidator:
    """Get or create the global validator instance"""
    global _validator

    if _validator is None:
        _validator = ConcentricCirclesValidator()

    return _validator
