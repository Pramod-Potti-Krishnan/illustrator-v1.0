"""
Test script for Funnel Generation API

Tests the /v1.0/funnel/generate endpoint with various configurations.
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


async def test_funnel_generation(
    num_stages: int,
    topic: str,
    context: dict = None,
    target_points: list = None
):
    """Test funnel generation with specific parameters"""

    payload = {
        "num_stages": num_stages,
        "topic": topic,
        "context": context or {},
        "target_points": target_points,
        "tone": "professional",
        "audience": "general",
        "theme": "professional",
        "size": "medium",
        "validate_constraints": True
    }

    print(f"\n{'='*80}")
    print(f"Testing {num_stages}-stage funnel: {topic}")
    print(f"{'='*80}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/v1.0/funnel/generate",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()

                print(f"✅ SUCCESS!")
                print(f"  Generation Time: {result['generation_time_ms']}ms")
                print(f"  Attempts: {result['metadata']['attempts']}")
                print(f"  Valid: {result['validation']['valid']}")

                if not result['validation']['valid']:
                    print(f"  ⚠️  Violations: {len(result['validation']['violations'])}")
                    for v in result['validation']['violations']:
                        print(f"     - {v['field']}: {v['actual_length']} chars ({v['status']})")

                # Print generated content
                print("\n Generated Content:")
                for key, value in result['generated_content'].items():
                    print(f"   {key}: {value[:60]}...")

                # Save HTML to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_funnel_{num_stages}stage_{timestamp}.html"
                with open(filename, 'w') as f:
                    f.write(result['html'])
                print(f"\n  💾 Saved to: {filename}")

                return True

            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"  Error: {response.text}")
                return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False


async def main():
    """Run comprehensive funnel generation tests"""

    print("\n" + "="*80)
    print("FUNNEL GENERATION API TEST SUITE")
    print("="*80)

    # Test 1: 3-Stage Sales Funnel
    await test_funnel_generation(
        num_stages=3,
        topic="Sales Conversion Funnel",
        context={
            "presentation_title": "Q4 Sales Strategy",
            "slide_purpose": "Show our sales pipeline stages",
            "industry": "B2B SaaS"
        },
        target_points=["Lead Generation", "Qualification", "Closed-Won"]
    )

    # Test 2: 4-Stage Marketing Funnel
    await test_funnel_generation(
        num_stages=4,
        topic="Customer Acquisition Journey",
        context={
            "presentation_title": "Marketing Strategy 2025",
            "slide_purpose": "Illustrate customer journey from awareness to loyalty",
            "industry": "E-commerce"
        },
        target_points=["Awareness", "Consideration", "Purchase", "Retention"]
    )

    # Test 3: 5-Stage Recruitment Funnel
    await test_funnel_generation(
        num_stages=5,
        topic="Talent Acquisition Pipeline",
        context={
            "presentation_title": "HR Operations Review",
            "slide_purpose": "Show our hiring process stages",
            "industry": "Technology"
        }
    )

    # Test 4: With Previous Slides Context
    await test_funnel_generation(
        num_stages=4,
        topic="Product Development Funnel",
        context={
            "presentation_title": "Product Roadmap Q1",
            "slide_purpose": "Demonstrate systematic development approach",
            "industry": "SaaS",
            "previous_slides": [
                {
                    "slide_number": 1,
                    "slide_title": "Market Opportunity",
                    "summary": "Identified $5B addressable market in enterprise collaboration"
                },
                {
                    "slide_number": 2,
                    "slide_title": "Competitive Analysis",
                    "summary": "Key differentiators: AI-powered workflow automation and integrated analytics"
                }
            ]
        },
        target_points=["Ideation", "Validation", "Development", "Launch"]
    )

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    # Check if service is running
    try:
        import requests
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  Warning: Illustrator service may not be running")
            print(f"   Please start with: python main.py")
    except:
        print("❌ ERROR: Cannot connect to Illustrator service")
        print(f"   Please ensure service is running at {BASE_URL}")
        print(f"   Start with: python main.py")
        exit(1)

    # Run tests
    asyncio.run(main())
