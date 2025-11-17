#!/usr/bin/env python3
"""
Test script for Pyramid Generation API

Tests the /v1.0/pyramid/generate endpoint with various configurations.
"""

import asyncio
import httpx
import json
from pathlib import Path


async def test_pyramid_generation():
    """Test pyramid generation endpoint"""

    base_url = "http://localhost:8000"

    # Test cases for different pyramid levels
    test_cases = [
        {
            "name": "4-Level Growth Strategy",
            "request": {
                "num_levels": 4,
                "topic": "Product Development Strategy",
                "context": {
                    "presentation_title": "Q4 Strategic Plan",
                    "slide_purpose": "Show hierarchical development approach",
                    "key_message": "Building from foundation to market leadership",
                    "industry": "Technology"
                },
                "target_points": [
                    "User Research",
                    "Product Design",
                    "Development & Testing",
                    "Market Launch"
                ],
                "tone": "professional",
                "audience": "executives",
                "theme": "professional",
                "validate_constraints": True
            }
        },
        {
            "name": "3-Level Organizational Structure",
            "request": {
                "num_levels": 3,
                "topic": "Team Organization Model",
                "context": {
                    "presentation_title": "Organization Design",
                    "key_message": "Clear hierarchy from execution to strategy"
                },
                "tone": "professional",
                "audience": "managers"
            }
        },
        {
            "name": "5-Level Skills Development",
            "request": {
                "num_levels": 5,
                "topic": "Professional Skills Progression",
                "target_points": [
                    "Foundation Skills",
                    "Core Competencies",
                    "Advanced Expertise",
                    "Leadership Abilities",
                    "Strategic Vision"
                ],
                "tone": "casual",
                "audience": "employees"
            }
        }
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'=' * 80}")
            print(f"Test {i}/{len(test_cases)}: {test_case['name']}")
            print(f"{'=' * 80}")

            try:
                # Make request
                response = await client.post(
                    f"{base_url}/v1.0/pyramid/generate",
                    json=test_case["request"]
                )

                if response.status_code == 200:
                    result = response.json()

                    print(f"✅ Success!")
                    print(f"   Generation time: {result['generation_time_ms']}ms")
                    print(f"   Validation: {'PASSED' if result['validation']['valid'] else 'FAILED'}")

                    # Print character counts
                    print(f"\n   Character Counts:")
                    for level, counts in result["character_counts"].items():
                        print(f"      {level}:")
                        for field, count in counts.items():
                            print(f"         {field}: {count} chars")

                    # Print generated content
                    print(f"\n   Generated Content:")
                    for key, value in result["generated_content"].items():
                        if "label" in key:
                            print(f"      {key}: \"{value}\"")

                    # Save HTML output
                    output_dir = Path("test_pyramid_outputs")
                    output_dir.mkdir(exist_ok=True)

                    filename = f"pyramid_{test_case['request']['num_levels']}_level_{i}.html"
                    output_path = output_dir / filename

                    with open(output_path, 'w') as f:
                        f.write(result["html"])

                    print(f"\n   📄 HTML saved to: {output_path}")

                    # Print validation violations if any
                    if result["validation"]["violations"]:
                        print(f"\n   ⚠️  Validation Violations:")
                        for violation in result["validation"]["violations"]:
                            print(f"      - {violation['field']}: "
                                  f"{violation['actual_length']} chars "
                                  f"({violation['min_required']}-{violation['max_required']} required)")

                else:
                    print(f"❌ Failed: HTTP {response.status_code}")
                    print(f"   {response.text}")

            except Exception as e:
                print(f"❌ Error: {e}")

    print(f"\n{'=' * 80}")
    print("Test Complete!")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    print("\n🔺 Pyramid API Test Script")
    print("=" * 80)
    print("Testing endpoint: POST /v1.0/pyramid/generate")
    print("Make sure the illustrator service is running on port 8000")
    print("=" * 80)

    asyncio.run(test_pyramid_generation())
