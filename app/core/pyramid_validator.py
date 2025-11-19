"""
Pyramid Content Validator

Validates that generated pyramid content meets character count constraints.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class PyramidValidator:
    """Validates pyramid content against character constraints"""

    def __init__(self, constraints_path: str = None):
        """
        Initialize validator with constraints file.

        Args:
            constraints_path: Path to pyramid_constraints.json
        """
        if constraints_path is None:
            # Default path relative to this file
            base_dir = Path(__file__).parent.parent
            constraints_path = base_dir / "variant_specs" / "pyramid_constraints.json"

        self.constraints_path = Path(constraints_path)
        self.constraints = self._load_constraints()

    def _load_constraints(self) -> Dict[str, Dict[str, Dict[str, list]]]:
        """Load character constraints from JSON file"""
        try:
            with open(self.constraints_path, 'r') as f:
                constraints = json.load(f)
            logger.info(f"Loaded pyramid constraints from {self.constraints_path}")
            return constraints
        except Exception as e:
            logger.error(f"Failed to load constraints: {e}")
            raise

    def get_constraints_for_pyramid(self, num_levels: int) -> Dict[str, Dict[str, list]]:
        """
        Get character constraints for a specific pyramid size.

        Args:
            num_levels: Number of pyramid levels (3-6)

        Returns:
            Dict mapping level keys to constraints
        """
        pyramid_key = f"pyramid_{num_levels}"
        if pyramid_key not in self.constraints:
            raise ValueError(f"No constraints defined for {num_levels}-level pyramid")

        return self.constraints[pyramid_key]

    def validate_content(
        self,
        content: Dict[str, str],
        num_levels: int
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate generated content against character constraints.

        Args:
            content: Dict with level_N_label and level_N_bullet_1/2/3/4/5 keys
            num_levels: Number of pyramid levels

        Returns:
            Tuple of (is_valid, violations_list)
        """
        constraints = self.get_constraints_for_pyramid(num_levels)
        violations = []

        import re

        for level_num in range(num_levels, 0, -1):
            level_key = f"level_{level_num}"

            if level_key not in constraints:
                continue

            # Check label
            label_key = f"{level_key}_label"
            if label_key in content:
                label_text = content[label_key]
                label_length = len(label_text)
                min_chars, max_chars = constraints[level_key]["label"]

                if label_length < min_chars or label_length > max_chars:
                    violations.append({
                        "field": label_key,
                        "actual_length": label_length,
                        "min_required": min_chars,
                        "max_required": max_chars,
                        "status": "under" if label_length < min_chars else "over",
                        "text": label_text[:50] + "..." if len(label_text) > 50 else label_text
                    })

            # Check each bullet point (5 bullets per level)
            for bullet_num in range(1, 6):
                bullet_field_key = f"bullet_{bullet_num}"
                if bullet_field_key in constraints[level_key]:
                    bullet_key = f"{level_key}_bullet_{bullet_num}"
                    if bullet_key in content:
                        bullet_text = content[bullet_key]
                        # Strip HTML tags for character counting
                        bullet_text_no_html = re.sub(r'<[^>]+>', '', bullet_text)
                        bullet_length = len(bullet_text_no_html)
                        min_chars, max_chars = constraints[level_key][bullet_field_key]

                        if bullet_length < min_chars or bullet_length > max_chars:
                            violations.append({
                                "field": bullet_key,
                                "actual_length": bullet_length,
                                "min_required": min_chars,
                                "max_required": max_chars,
                                "status": "under" if bullet_length < min_chars else "over",
                                "text": bullet_text[:50] + "..." if len(bullet_text) > 50 else bullet_text
                            })

        # Check overview fields if present
        if "overview" in constraints:
            # Check overview heading
            if "overview_heading" in content:
                heading_text = content["overview_heading"]
                heading_length = len(heading_text)
                min_chars, max_chars = constraints["overview"]["heading"]

                if heading_length < min_chars or heading_length > max_chars:
                    violations.append({
                        "field": "overview_heading",
                        "actual_length": heading_length,
                        "min_required": min_chars,
                        "max_required": max_chars,
                        "status": "under" if heading_length < min_chars else "over",
                        "text": heading_text
                    })

            # Check overview text
            if "overview_text" in content:
                text_content = content["overview_text"]
                text_length = len(text_content)
                min_chars, max_chars = constraints["overview"]["text"]

                if text_length < min_chars or text_length > max_chars:
                    violations.append({
                        "field": "overview_text",
                        "actual_length": text_length,
                        "min_required": min_chars,
                        "max_required": max_chars,
                        "status": "under" if text_length < min_chars else "over",
                        "text": text_content[:100] + "..." if len(text_content) > 100 else text_content
                    })

        is_valid = len(violations) == 0
        return is_valid, violations

    def get_character_counts(
        self,
        content: Dict[str, str],
        num_levels: int
    ) -> Dict[str, Dict[str, int]]:
        """
        Get character counts for all content fields.

        Args:
            content: Dict with level content
            num_levels: Number of pyramid levels

        Returns:
            Dict mapping field names to character counts
        """
        import re
        counts = {}

        for level_num in range(num_levels, 0, -1):
            level_key = f"level_{level_num}"
            counts[level_key] = {}

            # Count label
            label_key = f"{level_key}_label"
            if label_key in content:
                counts[level_key]["label"] = len(content[label_key])

            # Count each bullet (5 bullets per level)
            for bullet_num in range(1, 6):
                bullet_key = f"{level_key}_bullet_{bullet_num}"
                if bullet_key in content:
                    bullet_text = content[bullet_key]
                    # Strip HTML tags for accurate character counting
                    bullet_text_no_html = re.sub(r'<[^>]+>', '', bullet_text)
                    counts[level_key][f"bullet_{bullet_num}"] = len(bullet_text_no_html)

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
_validator: PyramidValidator = None


def get_validator() -> PyramidValidator:
    """Get or create the global validator instance"""
    global _validator

    if _validator is None:
        _validator = PyramidValidator()

    return _validator
