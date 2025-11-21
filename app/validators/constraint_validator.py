"""
Constraint Validator

Validates generated content against character limits and formatting rules.
Provides detailed violation reports for debugging and retry optimization.
"""

import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class ConstraintValidator:
    """Validator for illustration content constraints"""

    def __init__(self):
        """Initialize validator"""
        pass

    def count_characters(self, text: str) -> int:
        """
        Count characters excluding HTML tags

        Args:
            text: Text to count (may contain HTML tags)

        Returns:
            Character count (excluding HTML tags)
        """
        # Remove HTML tags
        text_without_html = re.sub(r'<[^>]+>', '', text)
        return len(text_without_html)

    def calculate_character_counts(self, generated_content: Dict[str, str]) -> Dict[str, Dict[str, int]]:
        """
        Calculate character counts for all fields

        Args:
            generated_content: Dict of field_name: value

        Returns:
            Dict of field_name: {"char_count": int, "with_html": int}
        """
        character_counts = {}
        for field_name, value in generated_content.items():
            character_counts[field_name] = {
                "char_count": self.count_characters(value),
                "with_html": len(value)
            }
        return character_counts

    def validate_concept_spread_content(
        self,
        generated_content: Dict[str, str],
        constraints: Dict[str, Any]
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate concept-spread generated content against constraints

        Args:
            generated_content: LLM-generated content
            constraints: Character limits and rules

        Returns:
            (is_valid, violations) tuple
        """
        violations = []

        # Validate central_text
        if "central_text" in constraints and "central_text" in generated_content:
            central_text_value = generated_content["central_text"]
            text_min, text_max = constraints["central_text"]["text"]
            text_count = self.count_characters(central_text_value)

            if text_count < text_min or text_count > text_max:
                violations.append({
                    "field": "central_text",
                    "value": central_text_value,
                    "char_count": text_count,
                    "min_allowed": text_min,
                    "max_allowed": text_max,
                    "violation_type": "too_short" if text_count < text_min else "too_long"
                })

        # Validate each hexagon
        for i in range(1, 7):
            hex_key = f"hex_{i}"
            if hex_key not in constraints:
                continue

            # Validate label
            label_field = f"hex_{i}_label"
            if label_field in generated_content:
                label_value = generated_content[label_field]
                label_min, label_max = constraints[hex_key]["label"]
                label_count = self.count_characters(label_value)

                if label_count < label_min or label_count > label_max:
                    violations.append({
                        "field": label_field,
                        "value": label_value,
                        "char_count": label_count,
                        "min_allowed": label_min,
                        "max_allowed": label_max,
                        "violation_type": "too_short" if label_count < label_min else "too_long"
                    })

            # Validate icon (must be single character)
            icon_field = f"hex_{i}_icon"
            if icon_field in generated_content:
                icon_value = generated_content[icon_field]
                icon_count = len(icon_value)
                expected_count = constraints[hex_key]["icon"][0]

                if icon_count != expected_count:
                    violations.append({
                        "field": icon_field,
                        "value": icon_value,
                        "char_count": icon_count,
                        "expected": expected_count,
                        "violation_type": "icon_length_mismatch"
                    })

        # Validate each description box
        for i in range(1, 7):
            box_key = f"box_{i}"
            if box_key not in constraints:
                continue

            # Validate bullets
            for bullet_num in range(1, 4):
                bullet_field = f"box_{i}_bullet_{bullet_num}"
                if bullet_field not in generated_content:
                    continue

                bullet_value = generated_content[bullet_field]
                bullet_min, bullet_max = constraints[box_key][f"bullet_{bullet_num}"]
                bullet_count = self.count_characters(bullet_value)

                if bullet_count < bullet_min or bullet_count > bullet_max:
                    violations.append({
                        "field": bullet_field,
                        "value": bullet_value,
                        "char_count": bullet_count,
                        "min_allowed": bullet_min,
                        "max_allowed": bullet_max,
                        "violation_type": "too_short" if bullet_count < bullet_min else "too_long"
                    })

        is_valid = len(violations) == 0
        if violations:
            logger.warning(f"Validation failed: {len(violations)} violations")
        else:
            logger.info("Validation passed: all constraints met")

        return is_valid, violations
