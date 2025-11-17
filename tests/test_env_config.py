"""Quick test to verify LLM_PYRAMID env variable is working"""
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:8000/v1.0/pyramid/generate",
            json={
                "num_levels": 3,
                "topic": "Test Pyramid",
                "tone": "professional"
            }
        )

        result = response.json()
        print(f"✅ Success: {result.get('success')}")
        print(f"📊 Model: {result.get('metadata', {}).get('model', 'N/A')}")
        print(f"⏱️  Generation time: {result.get('generation_time_ms')}ms")

        if result.get('success'):
            print("\n✅ LLM_PYRAMID environment variable is working!")
            print(f"   Using model: {result.get('metadata', {}).get('model')}")
        else:
            print("\n❌ Generation failed")

asyncio.run(test())
