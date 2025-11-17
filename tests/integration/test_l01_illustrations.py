"""
L01 Illustration Integration Tests
===================================

Tests all 6 L01 illustrations with Layout Builder API.
Generates actual presentations and provides viewable URLs.
"""

import sys
from pathlib import Path
import json

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.golden_example_generator import GoldenExampleGenerator
from app.core.template_engine import TemplateEngine
from app.core.constraint_validator import ConstraintValidator
from app.core.content_builder import ContentBuilder
from tests.integration.layout_builder_client import LayoutBuilderClient


class L01IntegrationTester:
    """Integration tests for L01 illustrations"""

    L01_ILLUSTRATIONS = [
        "pros_cons",
        "process_flow_horizontal",
        "pyramid_3tier",
        "funnel_4stage",
        "venn_2circle",
        "before_after"
    ]

    def __init__(self):
        self.generator = GoldenExampleGenerator()
        self.engine = TemplateEngine()
        self.validator = ConstraintValidator()
        self.client = LayoutBuilderClient()
        self.results = []

    def test_single_illustration(self, illustration_type: str) -> dict:
        """Test single L01 illustration end-to-end"""
        print(f"\n🧪 Testing {illustration_type}...")

        try:
            # 1. Generate request from golden example
            request = self.generator.generate_request_from_golden(illustration_type)
            print(f"   ✅ Request generated")

            # 2. Validate constraints
            validation = self.validator.validate(illustration_type, request.data)
            if not validation.valid:
                print(f"   ❌ Validation failed: {validation.violations}")
                return {
                    "illustration_type": illustration_type,
                    "success": False,
                    "error": f"Validation failed: {validation.violations}"
                }
            print(f"   ✅ Validation passed")

            # 3. Generate HTML
            html = self.engine.generate_illustration(
                illustration_type=illustration_type,
                data=request.data,
                theme_name="professional"
            )
            print(f"   ✅ HTML generated ({len(html)} chars)")

            # 4. Build L01 response
            content = ContentBuilder.build_l01_response(
                diagram_html=html,
                title=request.context["slide_title"],
                subtitle=f"Demonstrating {illustration_type.replace('_', ' ')}",
                body_text=f"This slide showcases the {illustration_type.replace('_', ' ')} illustration type with golden example data."
            )
            print(f"   ✅ Content built")

            # 5. Create presentation on Layout Builder
            presentation = self.client.create_presentation(
                title=f"L01 Test: {illustration_type.replace('_', ' ').title()}",
                slides=[content]
            )
            print(f"   ✅ Presentation created: {presentation['presentation_id']}")

            # 6. Get viewable URL
            url = self.client.get_presentation_url(presentation['presentation_id'])
            print(f"   🔗 URL: {url}")

            return {
                "illustration_type": illustration_type,
                "success": True,
                "presentation_id": presentation['presentation_id'],
                "url": url,
                "html_size": len(html),
                "validation": {
                    "valid": validation.valid,
                    "warnings": validation.warnings
                }
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

    def test_all_l01(self) -> list:
        """Test all 6 L01 illustrations"""
        print("\n" + "="*60)
        print("🧪 L01 ILLUSTRATION INTEGRATION TESTS")
        print("="*60)

        for illustration_type in self.L01_ILLUSTRATIONS:
            result = self.test_single_illustration(illustration_type)
            self.results.append(result)

        return self.results

    def generate_report(self, output_file: str = None) -> dict:
        """Generate test report with URLs"""
        successful = [r for r in self.results if r.get("success")]
        failed = [r for r in self.results if not r.get("success")]

        report = {
            "test_suite": "L01 Illustrations",
            "total_tests": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": f"{len(successful)/len(self.results)*100:.1f}%",
            "results": self.results,
            "viewable_urls": [
                {
                    "type": r["illustration_type"],
                    "url": r["url"]
                }
                for r in successful
            ]
        }

        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Report saved to: {output_path}")

        return report

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 L01 TEST SUMMARY")
        print("="*60)

        successful = [r for r in self.results if r.get("success")]
        failed = [r for r in self.results if not r.get("success")]

        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"Success Rate: {len(successful)/len(self.results)*100:.1f}%")

        if successful:
            print(f"\n🔗 VIEWABLE URLS:")
            for result in successful:
                print(f"   {result['illustration_type']:<30} {result['url']}")

        if failed:
            print(f"\n❌ FAILED TESTS:")
            for result in failed:
                print(f"   {result['illustration_type']}: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    tester = L01IntegrationTester()

    try:
        # Run all tests
        tester.test_all_l01()

        # Generate report
        report_path = Path(__file__).parent.parent / "integration_results" / "l01_results.json"
        tester.generate_report(str(report_path))

        # Print summary
        tester.print_summary()

        print("\n✅ L01 integration tests complete!")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
