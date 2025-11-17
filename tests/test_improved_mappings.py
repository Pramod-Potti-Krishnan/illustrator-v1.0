"""
Test Improved Template Mappings
================================

Tests that template engine now handles various placeholder naming conventions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.golden_example_generator import GoldenExampleGenerator
from app.core.template_engine import TemplateEngine


def test_swot_mapping():
    """Test SWOT with _items suffix"""
    print("\n🧪 Testing SWOT mapping...")

    generator = GoldenExampleGenerator()
    engine = TemplateEngine()

    request = generator.generate_request_from_golden("swot_2x2")
    html = engine.generate_illustration(
        illustration_type="swot_2x2",
        data=request.data,
        theme_name="professional"
    )

    assert len(html) > 0
    assert "<li>" in html
    assert "Strong brand recognition" in html
    print(f"   ✅ SWOT generated ({len(html)} chars)")


def test_process_flow_mapping():
    """Test process flow with process_ prefix"""
    print("\n🧪 Testing process flow mapping...")

    generator = GoldenExampleGenerator()
    engine = TemplateEngine()

    request = generator.generate_request_from_golden("process_flow_horizontal")
    html = engine.generate_illustration(
        illustration_type="process_flow_horizontal",
        data=request.data,
        theme_name="professional"
    )

    assert len(html) > 0
    assert "Discovery" in html or "Design" in html
    print(f"   ✅ Process flow generated ({len(html)} chars)")


def test_all_illustrations():
    """Test all 15 illustrations"""
    print("\n🧪 Testing all illustration types...")

    generator = GoldenExampleGenerator()
    engine = TemplateEngine()

    results = []
    for illust_type in generator.ILLUSTRATION_TYPES:
        try:
            request = generator.generate_request_from_golden(illust_type)
            html = engine.generate_illustration(
                illustration_type=illust_type,
                data=request.data,
                theme_name="professional"
            )
            print(f"   ✅ {illust_type}: {len(html)} chars")
            results.append((illust_type, True, len(html)))
        except Exception as e:
            print(f"   ❌ {illust_type}: {e}")
            results.append((illust_type, False, str(e)))

    successful = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    print(f"\n📊 Results: {len(successful)}/{len(results)} successful")

    if failed:
        print("\n❌ Failed:")
        for illust_type, _, error in failed:
            print(f"   {illust_type}: {error}")

    return results


if __name__ == "__main__":
    try:
        # Test specific mappings
        test_swot_mapping()
        test_process_flow_mapping()

        # Test all
        results = test_all_illustrations()

        successful = [r for r in results if r[1]]
        print(f"\n✅ {len(successful)}/15 illustrations working!")

        sys.exit(0 if len(successful) == 15 else 1)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
