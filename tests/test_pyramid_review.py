#!/usr/bin/env python3
"""
Test Pyramid Templates - All 4 Variants
========================================
Shows 3, 4, 5, and 6 stage pyramids for review
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.integration.layout_builder_client import LayoutBuilderClient
from app.core.template_engine import TemplateEngine


def generate_pyramid_review_presentation():
    """Generate presentation with all 4 pyramid variants"""

    print("🔺 Generating Pyramid Review Presentation")
    print("=" * 70)

    # Initialize components
    client = LayoutBuilderClient()
    engine = TemplateEngine()

    slides = []

    # Title slide
    title_slide = {
        "layout": "L29",
        "content": {
            "hero_content": """
                <div style="width: 100%; height: 100%;
                     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                     display: flex; flex-direction: column;
                     align-items: center; justify-content: center;">
                    <h1 style="font-size: 96px; color: white; font-weight: 900; margin: 0;">
                        Pyramid Templates
                    </h1>
                    <p style="font-size: 42px; color: rgba(255,255,255,0.9); margin-top: 32px;">
                        Review All 4 Variants
                    </p>
                    <p style="font-size: 28px; color: rgba(255,255,255,0.8); margin-top: 24px;">
                        3-Stage, 4-Stage, 5-Stage, 6-Stage
                    </p>
                </div>
            """
        }
    }
    slides.append(title_slide)

    # Test data for each pyramid variant
    pyramid_data = {
        "3": {
            "level_3_label": "Strategic",
            "level_3_description": "Executive leadership setting long-term vision and strategic direction",
            "level_2_label": "Tactical",
            "level_2_description": "Middle management translating strategy into actionable plans",
            "level_1_label": "Operational",
            "level_1_description": "Front-line teams executing daily operations and deliverables",
            "details_text": "This three-tier pyramid model represents a classic organizational hierarchy where strategic decisions flow from top leadership through middle management to operational teams. Each level plays a critical role in translating vision into execution, ensuring alignment across the organization. The strategic tier focuses on long-term planning and vision-setting, establishing the overarching direction and goals. The tactical tier bridges strategy and operations by developing concrete plans, allocating resources, and coordinating initiatives. The operational tier handles day-to-day execution, ensuring that strategic objectives are translated into tangible results through consistent delivery and performance management."
        },
        "4": {
            "level_4_label": "Vision",
            "level_4_description": "Leadership defining organizational vision and strategic objectives",
            "level_3_label": "Strategy",
            "level_3_description": "Strategic planning and resource allocation for achieving vision",
            "level_2_label": "Operations",
            "level_2_description": "Operational management coordinating teams and processes",
            "level_1_label": "Execution",
            "level_1_description": "Day-to-day execution of tasks and delivery of results",
            "details_text": "This four-tier model expands the traditional hierarchy to explicitly separate vision-setting from strategy development, and operational coordination from day-to-day execution, providing clearer accountability at each level. The vision tier establishes the aspirational future state and core purpose, while the strategy tier develops concrete plans to achieve that vision. The operations tier coordinates resources, teams, and processes to implement strategic initiatives effectively. The execution tier focuses on consistent delivery of tasks, maintaining quality standards, and achieving measurable outcomes that ladder up to strategic goals."
        },
        "5": {
            "level_5_label": "Leadership",
            "level_5_description": "Executive leadership and strategic direction for the organization",
            "level_4_label": "Management",
            "level_4_description": "Middle management coordinating teams and resources",
            "level_3_label": "Supervision",
            "level_3_description": "Supervisors overseeing day-to-day operations and team performance",
            "level_2_label": "Specialists",
            "level_2_description": "Subject matter experts providing specialized knowledge and skills",
            "level_1_label": "Operations",
            "level_1_description": "Front-line staff executing core business functions and deliverables",
        },
        "6": {
            "level_6_label": "Executive",
            "level_6_description": "C-suite executives setting vision and long-term strategy",
            "level_5_label": "Senior Management",
            "level_5_description": "Senior managers translating vision into strategic initiatives",
            "level_4_label": "Middle Management",
            "level_4_description": "Department heads managing resources and coordinating teams",
            "level_3_label": "Team Leads",
            "level_3_description": "Team leaders supervising daily operations and deliverables",
            "level_2_label": "Specialists",
            "level_2_description": "Professional staff with specialized expertise and capabilities",
            "level_1_label": "Associates",
            "level_1_description": "Entry-level staff executing operational tasks and support functions",
        }
    }

    # Generate each pyramid variant
    for variant in ["3", "4", "5", "6"]:
        print(f"\n{variant}. Generating {variant}-stage pyramid...")

        try:
            # ALL pyramids use L25 layout (pyramid left, descriptions right)
            template = engine.load_template("pyramid", variant)

            # Fill template
            html = engine.fill_template(
                template=template,
                data=pyramid_data[variant],
                theme={"theme_primary": "#2563EB", "theme_secondary": "#3b82f6",
                       "theme_accent": "#60a5fa", "theme_highlight": "#93c5fd"}
            )

            # Use L25 layout for all pyramids
            layout_id = "L25"
            slide = {
                "layout": "L25",
                "content": {
                    "slide_title": f"{variant}-Stage Pyramid Model",
                    "subtitle": "Hierarchical organizational structure with descriptions",
                    "rich_content": html,
                    "presentation_name": "Pyramid Review",
                    "company_logo": "🔺"
                }
            }

            slides.append(slide)
            print(f"   ✅ Generated {len(html)} chars using layout {layout_id}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Create presentation
    print("\n" + "=" * 70)
    print("📤 Creating presentation on Layout Builder...")

    try:
        result = client.create_presentation(
            title="Pyramid Templates Review",
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
        print(f"   - 3-Stage Pyramid: Slide 2 (L25 layout)")
        print(f"   - 4-Stage Pyramid: Slide 3 (L25 layout)")
        print(f"   - 5-Stage Pyramid: Slide 4 (L25 layout)")
        print(f"   - 6-Stage Pyramid: Slide 5 (L25 layout)")
        print("\n" + "=" * 70)

        # Save result
        import json
        result_file = Path(__file__).parent / "integration_results" / "pyramid_review_results.json"
        result_file.parent.mkdir(exist_ok=True)

        with open(result_file, 'w') as f:
            json.dump({
                "presentation_id": presentation_id,
                "url": url,
                "total_slides": len(slides),
                "variants": ["3-stage", "4-stage", "5-stage", "6-stage"]
            }, f, indent=2)

        print(f"\n💾 Results saved to: {result_file}")
        print("\n🎯 READY FOR REVIEW!")
        print("   Please verify:")
        print("   1. Pyramid orientation CORRECT (widest at bottom, narrowest at top)")
        print("   2. All use L25 layout with descriptions on right")
        print("   3. Colors and gradients are professional")
        print("   4. Text fits within L25 space constraints (no overflow)")
        print("   5. Numbers and labels positioned correctly")

        return url

    except Exception as e:
        print(f"\n❌ Error creating presentation: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    url = generate_pyramid_review_presentation()

    if url:
        print("\n" + "=" * 70)
        print("🎉 SUCCESS!")
        print("=" * 70)
        print(f"\nPresentation URL: {url}")
        print("\nReview all 4 pyramid variants and provide feedback!")
        print("=" * 70)
