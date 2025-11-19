"""
Test Script for Concentric Circles Generation API

Tests all 3 variants (3, 4, 5 circles) with comprehensive validation.
"""

import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime


BASE_URL = "http://localhost:8000"
OUTPUT_DIR = Path(__file__).parent / "test_output" / "concentric_circles"


async def test_concentric_circles(num_circles: int, topic: str, context: dict = None):
    """Test concentric circles generation with specific parameters"""

    print(f"\n{'='*60}")
    print(f"Testing {num_circles}-Circle Concentric Circles: '{topic}'")
    print(f"{'='*60}")

    payload = {
        "num_circles": num_circles,
        "topic": topic,
        "context": context or {},
        "tone": "professional",
        "audience": "general",
        "validate_constraints": True
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/v1.0/concentric_circles/generate",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()

                print(f"\n✅ Generation successful!")
                print(f"Generation time: {result['generation_time_ms']}ms")
                print(f"Validation: {'✅ PASSED' if result['validation']['valid'] else '❌ FAILED'}")

                if not result['validation']['valid']:
                    print(f"\nViolations found: {len(result['validation']['violations'])}")
                    for v in result['validation']['violations'][:3]:
                        print(f"  - {v['field']}: {v['actual_length']} chars (expected {v['min_required']}-{v['max_required']})")

                # Show character counts
                print(f"\nCharacter Counts:")
                for key, count in list(result['character_counts'].items())[:10]:
                    print(f"  {key}: {count} chars")

                # Save HTML output
                output_file = OUTPUT_DIR / f"{num_circles}_circles_{topic.replace(' ', '_')[:30]}.html"
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, 'w') as f:
                    f.write(result['html'])

                print(f"\n📁 Saved: {output_file}")

                return True

            else:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                return False

    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        return False


async def main():
    """Run comprehensive tests"""

    print("\n" + "="*60)
    print("CONCENTRIC CIRCLES API TEST SUITE")
    print("="*60)

    results = []

    # Test 3-circle variant
    results.append(await test_concentric_circles(
        num_circles=3,
        topic="Business Strategy Layers",
        context={
            "presentation_title": "Strategic Planning 2024",
            "industry": "Technology"
        }
    ))

    # Test 4-circle variant
    results.append(await test_concentric_circles(
        num_circles=4,
        topic="Product Development Stages",
        context={
            "presentation_title": "Product Roadmap",
            "industry": "Software"
        }
    ))

    # Test 5-circle variant
    results.append(await test_concentric_circles(
        num_circles=5,
        topic="Market Influence Zones",
        context={
            "presentation_title": "Market Analysis",
            "industry": "Marketing"
        }
    ))

    # Test with previous_slides context
    results.append(await test_concentric_circles(
        num_circles=4,
        topic="Customer Engagement Model",
        context={
            "presentation_title": "Customer Success Framework",
            "previous_slides": [
                {
                    "title": "Customer Acquisition",
                    "key_points": ["Digital marketing", "Referrals", "Partnerships"]
                },
                {
                    "title": "Onboarding Process",
                    "key_points": ["Training", "Support", "Resources"]
                }
            ]
        }
    ))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")

    if all(results):
        print("\n✅ All tests PASSED!")
    else:
        print("\n❌ Some tests FAILED")

    print(f"\nOutput directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
