#!/usr/bin/env python3
"""
Generate presentation with 8 illustrations for user review
===========================================================

Creates a presentation with the following illustrations:
- Process Flow Horizontal (L01)
- Pyramid 3-Tier (L01)
- Funnel 4-Stage (L01)
- Venn 2-Circle (L01)
- Timeline Horizontal (L02)
- Organization Chart (L02)
- Value Chain (L02)
- Circular Process (L02)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.integration.layout_builder_client import LayoutBuilderClient
from tests.golden_example_generator import GoldenExampleGenerator
from app.core.template_engine import TemplateEngine
from app.core.content_builder import ContentBuilder


def generate_review_presentation():
    """Generate presentation with 8 specific illustrations"""

    print("🎨 Generating Review Presentation with 8 Illustrations")
    print("=" * 70)

    # Initialize components
    client = LayoutBuilderClient()
    generator = GoldenExampleGenerator()
    engine = TemplateEngine()
    content_builder = ContentBuilder()

    # Selected illustration types
    selected_illustrations = [
        # L01 illustrations
        ("process_flow_horizontal", "L01", "Process Flow Horizontal"),
        ("pyramid_3tier", "L01", "3-Tier Pyramid Model"),
        ("funnel_4stage", "L01", "4-Stage Sales Funnel"),
        ("venn_2circle", "L01", "2-Circle Venn Diagram"),
        # L02 illustrations
        ("timeline_horizontal", "L02", "Horizontal Timeline"),
        ("org_chart", "L02", "Organization Chart"),
        ("value_chain", "L02", "Value Chain Analysis"),
        ("circular_process", "L02", "Circular Process Model"),
    ]

    # Generate slides
    slides = []

    # Title slide
    title_slide = {
        "layout": "L29",
        "content": {
            "hero_content": """
                <div style="width: 100%; height: 100%;
                     background: linear-gradient(135deg, #2563EB 0%, #1e40af 100%);
                     display: flex; flex-direction: column;
                     align-items: center; justify-content: center;">
                    <h1 style="font-size: 96px; color: white; font-weight: 900; margin: 0;">
                        Illustration Review
                    </h1>
                    <p style="font-size: 42px; color: rgba(255,255,255,0.9); margin-top: 32px;">
                        8 Business Illustrations for Optimization
                    </p>
                    <p style="font-size: 28px; color: rgba(255,255,255,0.8); margin-top: 24px;">
                        4 L01 + 4 L02 Layouts
                    </p>
                </div>
            """
        }
    }
    slides.append(title_slide)

    # Generate each illustration
    for idx, (illust_type, layout_id, title) in enumerate(selected_illustrations, 1):
        print(f"\n{idx}. Generating {illust_type}...")

        try:
            # Load golden example data
            spec = generator.load_spec(illust_type)
            golden_data = spec["golden_example"]

            # Generate HTML using template engine
            html = engine.generate_illustration(
                illustration_type=illust_type,
                data=golden_data,
                theme_name="professional",
                variant_id="base"
            )

            # Build content for layout
            if layout_id == "L01":
                content = content_builder.build_l01_response(
                    diagram_html=html,
                    title=title,
                    subtitle="Golden Example Data",
                    body_text=f"This {illust_type.replace('_', ' ')} demonstrates the template with baseline data."
                )
                # Add footer fields
                content["presentation_name"] = "Illustration Review"
                content["company_logo"] = "🎨"

            elif layout_id == "L02":
                content = content_builder.build_l02_response(
                    diagram_html=html,
                    text_html=f"<div style='padding: 20px; font-size: 18px; line-height: 1.6;'><p>This {illust_type.replace('_', ' ')} shows the layout with golden example data.</p><p>The diagram is on the left (element_3) and this explanation text is on the right (element_2).</p></div>",
                    title=title,
                    subtitle="Golden Example Data"
                )
                # Add footer fields
                content["presentation_name"] = "Illustration Review"
                content["company_logo"] = "🎨"

            # Create slide
            slide = {
                "layout": layout_id,
                "content": content
            }
            slides.append(slide)

            print(f"   ✅ Generated {len(html)} chars of HTML")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue

    # Create presentation
    print("\n" + "=" * 70)
    print("📤 Creating presentation on Layout Builder...")

    try:
        result = client.create_presentation(
            title="Illustration Review - 8 Examples",
            slides=slides
        )

        presentation_id = result.get("presentation_id") or result.get("id")
        url = client.get_presentation_url(presentation_id)

        print("\n" + "=" * 70)
        print("✅ PRESENTATION CREATED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\n🔗 View URL: {url}")
        print(f"\n📊 Presentation Details:")
        print(f"   - ID: {presentation_id}")
        print(f"   - Total Slides: {len(slides)}")
        print(f"   - Title Slide: 1")
        print(f"   - L01 Illustrations: 4")
        print(f"   - L02 Illustrations: 4")
        print("\n" + "=" * 70)

        # Save result to file
        result_file = Path(__file__).parent / "integration_results" / "review_8_results.json"
        result_file.parent.mkdir(exist_ok=True)

        import json
        with open(result_file, 'w') as f:
            json.dump({
                "presentation_id": presentation_id,
                "url": url,
                "total_slides": len(slides),
                "illustrations": [
                    {"type": t, "layout": l, "title": ti}
                    for t, l, ti in selected_illustrations
                ]
            }, f, indent=2)

        print(f"\n💾 Results saved to: {result_file}")
        print("\n🎯 READY FOR REVIEW!")
        print("   Please open the URL above to review the illustrations.")
        print("   Provide feedback on design, layout, spacing, colors, etc.")

        return url

    except Exception as e:
        print(f"\n❌ Error creating presentation: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    url = generate_review_presentation()

    if url:
        print("\n" + "=" * 70)
        print("🎉 SUCCESS!")
        print("=" * 70)
        print(f"\nPresentation URL: {url}")
        print("\nNext steps:")
        print("1. Open the URL in your browser")
        print("2. Review all 8 illustrations")
        print("3. Provide feedback for optimization")
        print("=" * 70)
