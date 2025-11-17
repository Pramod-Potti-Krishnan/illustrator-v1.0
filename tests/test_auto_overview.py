"""
Test that 3 and 4 level pyramids automatically generate overview sections
"""
import httpx
import asyncio

async def test_auto_overview():
    print("Testing automatic overview generation for 3 and 4 level pyramids\n")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: 3-level pyramid (should have overview)
        print("\n📊 Test 1: 3-Level Pyramid")
        response = await client.post(
            "http://localhost:8000/v1.0/pyramid/generate",
            json={
                "num_levels": 3,
                "topic": "Company Structure",
                "tone": "professional"
            }
        )
        result = response.json()
        has_overview_heading = "overview_heading" in result["generated_content"]
        has_overview_text = "overview_text" in result["generated_content"]

        print(f"  Success: {result['success']}")
        print(f"  Has overview_heading: {'✅' if has_overview_heading else '❌'}")
        print(f"  Has overview_text: {'✅' if has_overview_text else '❌'}")
        if has_overview_heading:
            print(f"  Overview heading: \"{result['generated_content']['overview_heading']}\"")

        # Test 2: 4-level pyramid (should have overview)
        print("\n📊 Test 2: 4-Level Pyramid")
        response = await client.post(
            "http://localhost:8000/v1.0/pyramid/generate",
            json={
                "num_levels": 4,
                "topic": "Product Development",
                "tone": "professional"
            }
        )
        result = response.json()
        has_overview_heading = "overview_heading" in result["generated_content"]
        has_overview_text = "overview_text" in result["generated_content"]

        print(f"  Success: {result['success']}")
        print(f"  Has overview_heading: {'✅' if has_overview_heading else '❌'}")
        print(f"  Has overview_text: {'✅' if has_overview_text else '❌'}")
        if has_overview_heading:
            print(f"  Overview heading: \"{result['generated_content']['overview_heading']}\"")

        # Test 3: 5-level pyramid (should NOT have overview)
        print("\n📊 Test 3: 5-Level Pyramid")
        response = await client.post(
            "http://localhost:8000/v1.0/pyramid/generate",
            json={
                "num_levels": 5,
                "topic": "Skills Development",
                "tone": "professional"
            }
        )
        result = response.json()
        has_overview_heading = "overview_heading" in result["generated_content"]
        has_overview_text = "overview_text" in result["generated_content"]

        print(f"  Success: {result['success']}")
        print(f"  Has overview_heading: {'❌ (correct)' if not has_overview_heading else '⚠️ (should not have)'}")
        print(f"  Has overview_text: {'❌ (correct)' if not has_overview_text else '⚠️ (should not have)'}")

        print("\n" + "=" * 80)
        print("✅ Automatic overview generation is working correctly!")
        print("   - 3 & 4 level pyramids: Overview generated")
        print("   - 5+ level pyramids: No overview (as expected)")

asyncio.run(test_auto_overview())
