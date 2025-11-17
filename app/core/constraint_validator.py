"""
Constraint Validator for Illustrator Service v1.0
=================================================

Validates illustration content meets variant spec constraints.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from models_v2 import ValidationResult


class ConstraintValidator:
    """Validates illustration content meets spec constraints"""

    def __init__(self, variant_specs_dir: str = None):
        if variant_specs_dir is None:
            base_dir = Path(__file__).parent.parent
            variant_specs_dir = base_dir / "variant_specs"
        self.specs_dir = Path(variant_specs_dir)

    def load_spec(self, illustration_type: str) -> Dict:
        """Load variant specification"""
        spec_path = self.specs_dir / illustration_type / "base.json"
        with open(spec_path, 'r') as f:
            return json.load(f)

    def validate(
        self,
        illustration_type: str,
        data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate data against constraints"""
        spec = self.load_spec(illustration_type)
        violations = []
        warnings = []

        for element in spec.get("elements", []):
            element_id = element["element_id"]

            # Check item constraints (for lists)
            if "item_constraints" in element:
                element_data = data.get(element_id)

                if element_data is None:
                    violations.append(f"{element_id}: Missing required field")
                    continue

                # Handle different data structures
                if isinstance(element_data, list):
                    items = element_data
                elif isinstance(element_data, dict) and "items" in element_data:
                    items = element_data["items"]
                else:
                    items = []

                if items:
                    item_count = len(items)
                    constraints = element["item_constraints"]

                    # Validate item count
                    if item_count < constraints.get("min_items", 0):
                        violations.append(
                            f"{element_id}: {item_count} items < {constraints['min_items']} min"
                        )
                    elif item_count > constraints.get("max_items", 999):
                        violations.append(
                            f"{element_id}: {item_count} items > {constraints['max_items']} max"
                        )

                    # Validate character counts per item
                    if "chars_per_item" in constraints:
                        for idx, item in enumerate(items):
                            item_str = str(item)
                            char_count = len(item_str)
                            char_limits = constraints["chars_per_item"]

                            if char_count < char_limits.get("min", 0):
                                warnings.append(
                                    f"{element_id}[{idx}]: {char_count} chars < {char_limits['min']} min (may look sparse)"
                                )
                            elif char_count > char_limits.get("max", 999):
                                violations.append(
                                    f"{element_id}[{idx}]: {char_count} chars > {char_limits['max']} max (will overflow)"
                                )

            # Check general constraints (for non-list fields)
            elif "constraints" in element:
                constraints = element["constraints"]
                element_data = data.get(element_id)

                if element_data is None:
                    if element.get("required_fields"):
                        violations.append(f"{element_id}: Missing required field")
                    continue

                # Validate string length constraints
                for field in element.get("required_fields", []):
                    field_value = element_data.get(field) if isinstance(element_data, dict) else None

                    if field_value is None:
                        continue

                    field_str = str(field_value)
                    char_count = len(field_str)

                    # Check field-specific constraints
                    constraint_key = f"{field}_chars"
                    if constraint_key in constraints:
                        char_limits = constraints[constraint_key]

                        if char_count < char_limits.get("min", 0):
                            warnings.append(
                                f"{element_id}.{field}: {char_count} chars < {char_limits['min']} min"
                            )
                        elif char_count > char_limits.get("max", 999):
                            violations.append(
                                f"{element_id}.{field}: {char_count} chars > {char_limits['max']} max"
                            )

        return ValidationResult(
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings
        )


if __name__ == "__main__":
    # Test validator
    validator = ConstraintValidator()

    # Test with pros_cons golden example
    test_data = {
        "pros": [
            "Proven track record in enterprise markets",
            "Strong financial position and cash reserves"
        ],
        "cons": [
            "High operational costs compared to competitors"
        ]
    }

    result = validator.validate("pros_cons", test_data)
    print(f"✅ Validation: valid={result.valid}")
    print(f"   Violations: {len(result.violations)}")
    print(f"   Warnings: {len(result.warnings)}")

    if result.violations:
        for v in result.violations:
            print(f"   ❌ {v}")

    if result.warnings:
        for w in result.warnings:
            print(f"   ⚠️  {w}")
