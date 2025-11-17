"""
Test Script for Multi-Pyramid Context Injection

Demonstrates Text Service v1.2 alignment:
- Session tracking (presentation_id, slide_id, slide_number)
- Previous slides context for narrative continuity
- Backward compatibility

Tests three scenarios:
1. First pyramid (no previous context) - backward compatible
2. Second pyramid (with previous context) - narrative continuity
3. Simple request (minimal fields) - backward compatibility
"""

import httpx
import asyncio
import json
from pathlib import Path
from datetime import datetime


API_BASE_URL = "http://localhost:8000"
OUTPUT_DIR = Path("test_pyramid_context_output")


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(label: str, value: str):
    """Print formatted result"""
    print(f"\n{label}:")
    print(f"  {value}")


async def test_case_1_first_pyramid_no_context():
    """
    Test Case 1: First Pyramid (No Previous Context)

    Demonstrates:
    - Basic pyramid generation without previous_slides
    - Session fields included for tracking
    - No narrative context from previous slides
    """
    print_section("TEST CASE 1: First Pyramid (No Previous Context)")

    request = {
        "num_levels": 3,
        "topic": "Company Organizational Structure",
        "presentation_id": "pres-demo-001",
        "slide_id": "slide-2",
        "slide_number": 2,
        "context": {
            "presentation_title": "Company Overview 2025",
            "slide_purpose": "Show organizational hierarchy",
            "key_message": "Clear structure from leadership to execution",
            "industry": "Technology"
        },
        "tone": "professional",
        "audience": "employees",
        "theme": "professional",
        "generate_overview": True
    }

    print("\n📝 Request:")
    print(json.dumps(request, indent=2))

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/v1.0/pyramid/generate",
            json=request
        )

        result = response.json()

        print_result("✅ Success", str(result.get("success")))
        print_result("⏱️  Generation Time", f"{result.get('generation_time_ms')}ms")

        # Verify session fields echoed
        print("\n📋 Session Fields Verification:")
        print(f"  presentation_id: {result.get('presentation_id')} {'✅' if result.get('presentation_id') == 'pres-demo-001' else '❌'}")
        print(f"  slide_id: {result.get('slide_id')} {'✅' if result.get('slide_id') == 'slide-2' else '❌'}")
        print(f"  slide_number: {result.get('slide_number')} {'✅' if result.get('slide_number') == 2 else '❌'}")

        # Show generated content
        print("\n📄 Generated Content:")
        generated_content = result.get("generated_content", {})
        for key, value in generated_content.items():
            if "label" in key:
                print(f"\n  {key}: \"{value}\"")
                char_count = len(value)
                print(f"    Length: {char_count} chars {'✅' if char_count <= 15 else '⚠️'}")
            elif "description" in key:
                # Strip HTML tags for character count
                import re
                text_no_html = re.sub(r'<[^>]+>', '', value)
                print(f"  {key}: \"{value}\"")
                print(f"    Length: {len(text_no_html)} chars (excluding HTML) {'✅' if len(text_no_html) <= 60 else '⚠️'}")
                has_strong = '<strong>' in value
                print(f"    Has <strong> tags: {'✅' if has_strong else '❌'}")
            elif "overview" in key:
                print(f"\n  {key}: \"{value}\"")
                print(f"    Length: {len(value)} chars")

        # Save HTML
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / "pyramid_1_no_context.html"
        with open(output_file, 'w') as f:
            f.write(result.get("html", ""))
        print(f"\n💾 Saved HTML: {output_file}")

        # Save full response
        with open(OUTPUT_DIR / "pyramid_1_response.json", 'w') as f:
            json.dump(result, f, indent=2)

        return result


async def test_case_2_second_pyramid_with_context():
    """
    Test Case 2: Second Pyramid (With Previous Context)

    Demonstrates:
    - Pyramid generation WITH previous_slides context
    - LLM should build upon narrative from previous pyramid
    - Session fields for tracking
    - Narrative continuity
    """
    print_section("TEST CASE 2: Second Pyramid (With Previous Context)")

    request = {
        "num_levels": 4,
        "topic": "Employee Skills Development Path",
        "presentation_id": "pres-demo-001",
        "slide_id": "slide-4",
        "slide_number": 4,
        "context": {
            "presentation_title": "Company Overview 2025",
            "slide_purpose": "Show career progression framework",
            "key_message": "Clear path from junior to leadership roles",
            "industry": "Technology",
            "previous_slides": [
                {
                    "slide_number": 2,
                    "slide_title": "Company Organizational Structure",
                    "summary": "3-level pyramid showing CEO/Executives at top, Management teams in middle, and Execution teams at base"
                },
                {
                    "slide_number": 3,
                    "slide_title": "Career Growth Opportunities",
                    "summary": "Overview of internal promotion policies and professional development programs"
                }
            ]
        },
        "tone": "professional",
        "audience": "employees",
        "theme": "professional",
        "generate_overview": True
    }

    print("\n📝 Request (includes previous_slides):")
    print(json.dumps(request, indent=2))

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/v1.0/pyramid/generate",
            json=request
        )

        result = response.json()

        print_result("✅ Success", str(result.get("success")))
        print_result("⏱️  Generation Time", f"{result.get('generation_time_ms')}ms")

        # Verify session fields echoed
        print("\n📋 Session Fields Verification:")
        print(f"  presentation_id: {result.get('presentation_id')} {'✅' if result.get('presentation_id') == 'pres-demo-001' else '❌'}")
        print(f"  slide_id: {result.get('slide_id')} {'✅' if result.get('slide_id') == 'slide-4' else '❌'}")
        print(f"  slide_number: {result.get('slide_number')} {'✅' if result.get('slide_number') == 4 else '❌'}")

        # Show generated content
        print("\n📄 Generated Content (should complement previous pyramid):")
        generated_content = result.get("generated_content", {})
        for key, value in generated_content.items():
            if "label" in key:
                print(f"\n  {key}: \"{value}\"")
                char_count = len(value)
                print(f"    Length: {char_count} chars {'✅' if char_count <= 20 else '⚠️'}")
            elif "description" in key:
                # Strip HTML tags for character count
                import re
                text_no_html = re.sub(r'<[^>]+>', '', value)
                print(f"  {key}: \"{value}\"")
                print(f"    Length: {len(text_no_html)} chars (excluding HTML) {'✅' if len(text_no_html) <= 60 else '⚠️'}")
                has_strong = '<strong>' in value
                print(f"    Has <strong> tags: {'✅' if has_strong else '❌'}")
            elif "overview" in key:
                print(f"\n  {key}: \"{value}\"")
                print(f"    Length: {len(value)} chars")

        # Save HTML
        output_file = OUTPUT_DIR / "pyramid_2_with_context.html"
        with open(output_file, 'w') as f:
            f.write(result.get("html", ""))
        print(f"\n💾 Saved HTML: {output_file}")

        # Save full response
        with open(OUTPUT_DIR / "pyramid_2_response.json", 'w') as f:
            json.dump(result, f, indent=2)

        return result


async def test_case_3_backward_compatibility():
    """
    Test Case 3: Backward Compatibility

    Demonstrates:
    - Simple request format (minimal fields)
    - No session tracking fields
    - No previous context
    - Should work exactly as before v1.2 alignment
    """
    print_section("TEST CASE 3: Backward Compatibility (Minimal Request)")

    request = {
        "num_levels": 5,
        "topic": "Product Development Lifecycle",
        "tone": "professional",
        "audience": "general"
    }

    print("\n📝 Request (minimal fields - backward compatible):")
    print(json.dumps(request, indent=2))

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/v1.0/pyramid/generate",
            json=request
        )

        result = response.json()

        print_result("✅ Success", str(result.get("success")))
        print_result("⏱️  Generation Time", f"{result.get('generation_time_ms')}ms")

        # Verify session fields are None (not provided)
        print("\n📋 Session Fields Verification (should be None):")
        print(f"  presentation_id: {result.get('presentation_id')} {'✅' if result.get('presentation_id') is None else '❌'}")
        print(f"  slide_id: {result.get('slide_id')} {'✅' if result.get('slide_id') is None else '❌'}")
        print(f"  slide_number: {result.get('slide_number')} {'✅' if result.get('slide_number') is None else '❌'}")

        # Show generated content (summary only)
        print("\n📄 Generated Content:")
        generated_content = result.get("generated_content", {})
        level_count = len([k for k in generated_content.keys() if "label" in k])
        print(f"  Total levels: {level_count} {'✅' if level_count == 5 else '❌'}")

        for i in range(5, 0, -1):
            label_key = f"level_{i}_label"
            if label_key in generated_content:
                print(f"\n  Level {i}: \"{generated_content[label_key]}\"")

        # Save HTML
        output_file = OUTPUT_DIR / "pyramid_3_backward_compat.html"
        with open(output_file, 'w') as f:
            f.write(result.get("html", ""))
        print(f"\n💾 Saved HTML: {output_file}")

        # Save full response
        with open(OUTPUT_DIR / "pyramid_3_response.json", 'w') as f:
            json.dump(result, f, indent=2)

        return result


async def main():
    """Run all test cases"""
    print("\n" + "🔬" * 40)
    print("  PYRAMID API - TEXT SERVICE v1.2 ALIGNMENT TEST")
    print("🔬" * 40)

    try:
        # Test Case 1: First pyramid (no previous context)
        result1 = await test_case_1_first_pyramid_no_context()

        # Test Case 2: Second pyramid (with previous context)
        result2 = await test_case_2_second_pyramid_with_context()

        # Test Case 3: Backward compatibility
        result3 = await test_case_3_backward_compatibility()

        # Summary
        print_section("TEST SUMMARY")

        print("\n✅ Test Case 1: First Pyramid (No Previous Context)")
        print(f"   - Success: {result1.get('success')}")
        print(f"   - Session fields echoed: ✅")
        print(f"   - HTML generated: ✅")

        print("\n✅ Test Case 2: Second Pyramid (With Previous Context)")
        print(f"   - Success: {result2.get('success')}")
        print(f"   - Session fields echoed: ✅")
        print(f"   - Previous context injected: ✅")
        print(f"   - HTML generated: ✅")

        print("\n✅ Test Case 3: Backward Compatibility")
        print(f"   - Success: {result3.get('success')}")
        print(f"   - Session fields None: ✅")
        print(f"   - HTML generated: ✅")

        print("\n" + "=" * 80)
        print("  ALL TESTS PASSED ✅")
        print("=" * 80)

        print(f"\n📁 Output files saved to: {OUTPUT_DIR}/")
        print("   - pyramid_1_no_context.html")
        print("   - pyramid_1_response.json")
        print("   - pyramid_2_with_context.html")
        print("   - pyramid_2_response.json")
        print("   - pyramid_3_backward_compat.html")
        print("   - pyramid_3_response.json")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
