"""
Simple Pipeline Test
====================

Quick validation that the entire generation pipeline works.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.golden_example_generator import GoldenExampleGenerator
from app.core.template_engine import TemplateEngine
from app.core.constraint_validator import ConstraintValidator
from app.core.layout_selector import LayoutSelector
from app.core.content_builder import ContentBuilder


def test_simple_pipeline():
    """Test complete pipeline with one illustration"""
    print("\n🧪 Testing Simple Pipeline...")

    # Setup
    generator = GoldenExampleGenerator()
    engine = TemplateEngine()
    validator = ConstraintValidator()

    # Test with pros_cons (L01)
    illustration_type = "pros_cons"
    print(f"\n📋 Testing: {illustration_type}")

    # Generate request
    request = generator.generate_request_from_golden(illustration_type)
    print(f"   ✅ Request generated: {request.presentation_id}")

    # Get layout
    layout_id = LayoutSelector.get_layout(illustration_type)
    print(f"   ✅ Layout selected: {layout_id}")
    assert layout_id == "L01", f"Expected L01, got {layout_id}"

    # Validate constraints
    result = validator.validate(illustration_type, request.data)
    print(f"   ✅ Validation: valid={result.valid}, violations={len(result.violations)}")
    if not result.valid:
        for v in result.violations:
            print(f"      ❌ {v}")
    assert result.valid, f"Constraint validation failed: {result.violations}"

    # Generate HTML
    html = engine.generate_illustration(
        illustration_type=illustration_type,
        data=request.data,
        theme_name="professional"
    )
    print(f"   ✅ HTML generated: {len(html)} characters")
    assert len(html) > 0, "HTML generation failed"
    assert "<html>" in html or "<div" in html, "HTML structure invalid"

    # Build response
    content = ContentBuilder.build_l01_response(
        diagram_html=html,
        title=request.context["slide_title"],
        subtitle="Test subtitle",
        body_text="Test body text"
    )
    print(f"   ✅ Response built: {len(content)} fields")
    assert "slide_title" in content
    assert "element_4" in content
    assert content["element_4"] == html

    print("\n✅ Simple pipeline test PASSED!")
    return True


if __name__ == "__main__":
    try:
        test_simple_pipeline()
        print("\n🎉 All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
