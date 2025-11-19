"""
Funnel Content Validator

Validates that generated funnel content meets character count constraints.
Follows the same pattern as pyramid_validator.py.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class FunnelValidator:
    """Validates funnel content against character constraints"""

    def __init__(self, constraints_path: str = None):
        """
        Initialize validator with constraints file.

        Args:
            constraints_path: Path to funnel_constraints.json
        """
        if constraints_path is None:
            # Default path relative to this file
            base_dir = Path(__file__).parent.parent
            constraints_path = base_dir / "variant_specs" / "funnel_constraints.json"

        self.constraints_path = Path(constraints_path)
        self.constraints = self._load_constraints()

    def _load_constraints(self) -> Dict[str, Dict[str, Dict[str, list]]]:
        """Load character constraints from JSON file"""
        try:
            with open(self.constraints_path, 'r') as f:
                constraints = json.load(f)
            logger.info(f"Loaded funnel constraints from {self.constraints_path}")
            return constraints
        except Exception as e:
            logger.error(f"Failed to load funnel constraints: {e}")
            raise

    def get_constraints_for_funnel(self, num_stages: int) -> Dict[str, Dict[str, list]]:
        """
        Get character constraints for a specific funnel size.

        Args:
            num_stages: Number of funnel stages (3-5)

        Returns:
            Dict mapping stage keys to constraints
        """
        funnel_key = f"funnel_{num_stages}"
        if funnel_key not in self.constraints:
            raise ValueError(f"No constraints defined for {num_stages}-stage funnel")

        return self.constraints[funnel_key]

    def _count_characters(self, text: str) -> int:
        """
        Count characters excluding HTML tags.

        Args:
            text: Text that may contain HTML tags

        Returns:
            Character count without HTML tags
        """
        # Strip HTML tags for character counting
        text_no_html = re.sub(r'<[^>]+>', '', text)
        return len(text_no_html)

    def validate_content(
        self,
        content: Dict[str, str],
        num_stages: int
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate generated content against character constraints.

        Args:
            content: Dict with stage_N_name and stage_N_bullet_1/2/3 keys
            num_stages: Number of funnel stages (3-5)

        Returns:
            Tuple of (is_valid, violations_list)
        """
        constraints = self.get_constraints_for_funnel(num_stages)
        violations = []

        for stage_num in range(1, num_stages + 1):
            stage_key = f"stage_{stage_num}"

            if stage_key not in constraints:
                continue

            # Check stage name
            name_key = f"{stage_key}_name"
            if name_key in content:
                name_text = content[name_key]
                name_length = self._count_characters(name_text)
                min_chars, max_chars = constraints[stage_key]["name"]

                if name_length < min_chars or name_length > max_chars:
                    violations.append({
                        "field": name_key,
                        "actual_length": name_length,
                        "min_required": min_chars,
                        "max_required": max_chars,
                        "status": "under" if name_length < min_chars else "over",
                        "text": name_text[:50] + "..." if len(name_text) > 50 else name_text
                    })

            # Check each bullet point (dynamic count based on constraints)
            # Determine max bullets by checking which bullet keys exist in constraints
            max_bullets = sum(1 for key in constraints[stage_key].keys() if key.startswith("bullet_"))

            for bullet_num in range(1, max_bullets + 1):
                bullet_field_key = f"bullet_{bullet_num}"
                if bullet_field_key in constraints[stage_key]:
                    bullet_key = f"{stage_key}_bullet_{bullet_num}"
                    if bullet_key in content:
                        bullet_text = content[bullet_key]
                        bullet_length = self._count_characters(bullet_text)
                        min_chars, max_chars = constraints[stage_key][bullet_field_key]

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
        num_stages: int
    ) -> Dict[str, Dict[str, int]]:
        """
        Get character counts for all content fields.

        Args:
            content: Dict with stage content
            num_stages: Number of funnel stages

        Returns:
            Dict mapping field names to character counts
        """
        counts = {}

        for stage_num in range(1, num_stages + 1):
            stage_key = f"stage_{stage_num}"
            counts[stage_key] = {}

            # Count stage name
            name_key = f"{stage_key}_name"
            if name_key in content:
                counts[stage_key]["name"] = self._count_characters(content[name_key])

            # Count each bullet (dynamic - check content for all bullet keys)
            bullet_num = 1
            while True:
                bullet_key = f"{stage_key}_bullet_{bullet_num}"
                if bullet_key in content:
                    counts[stage_key][f"bullet_{bullet_num}"] = self._count_characters(content[bullet_key])
                    bullet_num += 1
                else:
                    break

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
            return "✅ All funnel content meets character constraints"

        report = f"❌ Found {len(violations)} constraint violation(s):\n\n"

        for i, violation in enumerate(violations, 1):
            report += f"{i}. {violation['field']}:\n"
            report += f"   - Actual: {violation['actual_length']} chars\n"
            report += f"   - Required: {violation['min_required']}-{violation['max_required']} chars\n"
            report += f"   - Status: {violation['status'].upper()}\n"
            report += f"   - Text: \"{violation['text']}\"\n\n"

        return report


# Global validator instance
_funnel_validator: FunnelValidator = None


def get_funnel_validator() -> FunnelValidator:
    """Get or create the global funnel validator instance"""
    global _funnel_validator

    if _funnel_validator is None:
        _funnel_validator = FunnelValidator()

    return _funnel_validator
