"""
Individual Illustration Presentations
======================================

Creates separate presentation for each working illustration type.
Provides multiple URLs for detailed verification.
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import time

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.golden_example_generator import GoldenExampleGenerator
from app.core.template_engine import TemplateEngine
from app.core.content_builder import ContentBuilder
from tests.integration.layout_builder_client import LayoutBuilderClient


# Working illustrations for individual presentations
WORKING_ILLUSTRATIONS = [
    ("pros_cons", "L01", "Pros & Cons Analysis"),
    ("pyramid_3tier", "L01", "3-Tier Pyramid Model"),
    ("funnel_4stage", "L01", "4-Stage Sales Funnel"),
    ("venn_2circle", "L01", "2-Circle Venn Diagram"),
    ("before_after", "L01", "Before & After Comparison"),
]


def create_single_illustration_presentation(
    illustration_type: str,
    layout_id: str,
    title: str
) -> dict:
    """Create presentation with single illustration"""
    print(f"\n📊 Creating presentation for: {illustration_type}")

    try:
        generator = GoldenExampleGenerator()
        engine = TemplateEngine()
        client = LayoutBuilderClient()

        # Generate request
        request = generator.generate_request_from_golden(illustration_type)

        # Generate HTML
        html = engine.generate_illustration(
            illustration_type=illustration_type,
            data=request.data,
            theme_name="professional"
        )

        # Build slides
        slides = [
            # Title slide
            {
                "slide_title": f"{title}",
                "subtitle": f"Illustrator Service v1.0 - {illustration_type}",
                "body_text": f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nThis presentation demonstrates the {illustration_type.replace('_', ' ')} illustration type using golden example data.",
                "layout_id": "L01"
            },
            # Illustration slide
            ContentBuilder.build_l01_response(
                diagram_html=html,
                title=title,
                subtitle=f"Type: {illustration_type}",
                body_text=f"This slide showcases the {illustration_type.replace('_', ' ')} illustration with professionally themed styling."
            )
        ]

        # Create presentation
        presentation = client.create_presentation(
            title=f"Illustrator Test: {title}",
            slides=slides
        )

        url = client.get_presentation_url(presentation['presentation_id'])
        print(f"   ✅ Created: {presentation['presentation_id']}")
        print(f"   🔗 URL: {url}")

        return {
            "illustration_type": illustration_type,
            "layout_id": layout_id,
            "title": title,
            "presentation_id": presentation['presentation_id'],
            "url": url,
            "success": True
        }

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "illustration_type": illustration_type,
            "success": False,
            "error": str(e)
        }


def main():
    """Create individual presentations for all working illustrations"""
    print("\n" + "="*70)
    print("🎨 CREATING INDIVIDUAL ILLUSTRATION PRESENTATIONS")
    print("="*70)

    results = []

    for illustration_type, layout_id, title in WORKING_ILLUSTRATIONS:
        result = create_single_illustration_presentation(
            illustration_type,
            layout_id,
            title
        )
        results.append(result)
        time.sleep(0.5)  # Brief pause between API calls

    # Save results
    output_dir = Path(__file__).parent.parent / "integration_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "individual_presentations_results.json"

    summary = {
        "total": len(results),
        "successful": len([r for r in results if r.get("success")]),
        "failed": len([r for r in results if not r.get("success")]),
        "timestamp": datetime.now().isoformat(),
        "presentations": results
    }

    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print("\n" + "="*70)
    print("📊 INDIVIDUAL PRESENTATIONS SUMMARY")
    print("="*70)

    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    print(f"\nTotal: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")

    if successful:
        print(f"\n🔗 VIEWABLE PRESENTATION URLS:")
        for r in successful:
            print(f"\n   {r['title']}")
            print(f"   {r['url']}")

    print(f"\n📄 Results saved to: {output_file}")

    return summary


if __name__ == "__main__":
    try:
        summary = main()
        sys.exit(0 if summary["failed"] == 0 else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
