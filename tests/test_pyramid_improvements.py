#!/usr/bin/env python3
"""
Test Pyramid API Improvements:
1. Stricter character constraints (top: 10-15 chars, others: 12-20 chars, descriptions: 50-60 chars)
2. Overview section generation (3 and 4 level pyramids)
3. <strong> tags in descriptions
"""

import httpx
import asyncio
import json
from pathlib import Path


async def test_pyramid_improvements():
    """Test all pyramid API improvements"""

    base_url = "http://localhost:8000"

    test_cases = [
        {
            "name": "4-Level with Overview",
            "request": {
                "num_levels": 4,
                "topic": "Product Development",
                "context": {
                    "presentation_title": "Q4 Strategic Plan",
                    "slide_purpose": "Show development stages"
                },
                "tone": "professional",
                "audience": "executives",
                "generate_overview": True  # Request overview section
            },
            "expected": {
                "top_label_max_words": 2,
                "top_label_max_chars": 15,
                "has_overview": True,
                "has_strong_tags": True
            }
        },
        {
            "name": "3-Level with Overview",
            "request": {
                "num_levels": 3,
                "topic": "Team Structure",
                "tone": "professional",
                "audience": "general",
                "generate_overview": True  # Request overview section
            },
            "expected": {
                "top_label_max_words": 2,
                "top_label_max_chars": 15,
                "has_overview": True,
                "has_strong_tags": True
            }
        },
        {
            "name": "5-Level without Overview",
            "request": {
                "num_levels": 5,
                "topic": "Skills Development",
                "tone": "professional",
                "generate_overview": False  # No overview for 5-level
            },
            "expected": {
                "top_label_max_words": 2,
                "top_label_max_chars": 15,
                "has_overview": False,
                "has_strong_tags": True
            }
        }
    ]

    # Create output directory
    output_dir = Path("test_pyramid_improvements_output")
    output_dir.mkdir(exist_ok=True)

    print("🔺 Pyramid API Improvements Test")
    print("=" * 80)
    print(f"Testing endpoint: POST {base_url}/v1.0/pyramid/generate")
    print("=" * 80)
    print()

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            print("=" * 80)
            print(f"Test {i}/{len(test_cases)}: {test_case['name']}")
            print("=" * 80)

            try:
                response = await client.post(
                    f"{base_url}/v1.0/pyramid/generate",
                    json=test_case["request"]
                )

                if response.status_code == 200:
                    result = response.json()

                    print("✅ Success!")
                    print(f"   Generation time: {result['generation_time_ms']}ms")

                    # Check validation
                    validation = result.get("validation", {})
                    if validation.get("valid"):
                        print("   Validation: ✅ PASSED")
                    else:
                        print("   Validation: ⚠️  FAILED")
                        violations = validation.get("violations", [])
                        for violation in violations:
                            print(f"      - {violation['field']}: {violation['actual_length']} chars "
                                  f"({violation['min_required']}-{violation['max_required']} required)")

                    # Check generated content
                    content = result.get("generated_content", {})
                    num_levels = test_case["request"]["num_levels"]

                    # Check top label constraints
                    top_label = content.get(f"level_{num_levels}_label", "")
                    word_count = len(top_label.split())
                    char_count = len(top_label)

                    print()
                    print(f"   Top Label Analysis:")
                    print(f"      Text: \"{top_label}\"")
                    print(f"      Words: {word_count} (expected: ≤2)")
                    print(f"      Chars: {char_count} (expected: 10-15)")

                    if word_count <= 2 and 10 <= char_count <= 15:
                        print(f"      Status: ✅ Meets constraints")
                    else:
                        print(f"      Status: ⚠️  Violates constraints")

                    # Check for <strong> tags
                    has_strong = False
                    strong_count = 0
                    print()
                    print("   Description Analysis:")
                    for level_num in range(num_levels, 0, -1):
                        desc = content.get(f"level_{level_num}_description", "")
                        if "<strong>" in desc:
                            has_strong = True
                            strong_count += 1
                            # Extract strong text
                            import re
                            strong_words = re.findall(r'<strong>(.*?)</strong>', desc)
                            print(f"      Level {level_num}: {len(desc)} chars, "
                                  f"emphasized: {', '.join(strong_words)}")

                    if has_strong:
                        print(f"      Status: ✅ {strong_count}/{num_levels} descriptions have <strong> tags")
                    else:
                        print(f"      Status: ⚠️  No <strong> tags found")

                    # Check overview section
                    has_overview = "overview_heading" in content
                    if test_case["expected"]["has_overview"]:
                        print()
                        print("   Overview Section:")
                        if has_overview:
                            heading = content.get("overview_heading", "")
                            text = content.get("overview_text", "")
                            print(f"      Heading: \"{heading}\" ({len(heading)} chars)")
                            print(f"      Text: \"{text[:100]}...\" ({len(text)} chars)")
                            print(f"      Status: ✅ Overview generated")
                        else:
                            print(f"      Status: ❌ Overview missing (was requested)")

                    # Save HTML
                    html = result.get("html", "")
                    filename = output_dir / f"pyramid_{num_levels}_level_{i}.html"
                    with open(filename, "w") as f:
                        f.write(html)
                    print()
                    print(f"   📄 HTML saved to: {filename}")

                else:
                    print(f"❌ Failed: HTTP {response.status_code}")
                    print(f"   {response.json()}")

            except Exception as e:
                print(f"❌ Error: {e}")

            print()

    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_pyramid_improvements())
