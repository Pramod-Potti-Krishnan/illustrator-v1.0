"""
Golden Example Generator for Illustrator Service v1.0
=====================================================

Generates test data from variant spec golden examples for automated testing.
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models_v2 import IllustrationGenerationRequest
from app.core.layout_selector import LayoutSelector


class GoldenExampleGenerator:
    """Generates test data from variant spec golden examples"""

    ILLUSTRATION_TYPES = [
        # L01
        "pros_cons", "process_flow_horizontal", "pyramid_3tier",
        "funnel_4stage", "venn_2circle", "before_after",
        # L25
        "swot_2x2", "ansoff_matrix", "kpi_dashboard",
        "bcg_matrix", "porters_five_forces",
        # L02
        "timeline_horizontal", "org_chart", "value_chain", "circular_process"
    ]

    def __init__(self, variant_specs_dir: str = None):
        if variant_specs_dir is None:
            base_dir = Path(__file__).parent.parent
            variant_specs_dir = base_dir / "app" / "variant_specs"
        self.specs_dir = Path(variant_specs_dir)

    def load_spec(self, illustration_type: str) -> Dict:
        """Load variant specification JSON"""
        spec_path = self.specs_dir / illustration_type / "base.json"
        with open(spec_path, 'r') as f:
            return json.load(f)

    def load_all_specs(self) -> Dict[str, Dict]:
        """Load all variant spec JSONs"""
        specs = {}
        for illust_type in self.ILLUSTRATION_TYPES:
            specs[illust_type] = self.load_spec(illust_type)
        return specs

    def _extract_topics(self, golden: Dict) -> List[str]:
        """Extract topics from golden example for request"""
        topics = []

        # Handle different golden example structures
        if isinstance(golden, dict):
            for key, value in golden.items():
                if isinstance(value, list):
                    topics.extend([str(item) for item in value[:2]])  # Take first 2 items
                elif isinstance(value, dict) and "title" in value:
                    topics.append(value["title"])
                elif isinstance(value, str) and len(value) < 100:
                    topics.append(value)

        # Default topics if extraction failed
        if not topics:
            topics = ["Test topic 1", "Test topic 2", "Test topic 3"]

        return topics[:5]  # Limit to 5 topics

    def generate_request_from_golden(
        self,
        illustration_type: str,
        spec: Dict = None
    ) -> IllustrationGenerationRequest:
        """Convert golden example to valid request"""
        if spec is None:
            spec = self.load_spec(illustration_type)

        golden = spec["golden_example"]
        layout_id = LayoutSelector.get_layout(illustration_type)

        return IllustrationGenerationRequest(
            presentation_id="test_pres_001",
            slide_id=f"slide_{illustration_type}",
            slide_number=1,
            illustration_type=illustration_type,
            variant_id="base",
            topics=self._extract_topics(golden),
            narrative=f"Test narrative for {illustration_type.replace('_', ' ')}",
            data=golden,
            context={
                "theme": "professional",
                "audience": "executives",
                "slide_title": f"Test {illustration_type.replace('_', ' ').title()}"
            },
            layout_id=layout_id,
            theme="professional"
        )

    def generate_all_test_requests(self) -> Dict[str, IllustrationGenerationRequest]:
        """Generate requests for all 15 illustrations"""
        specs = self.load_all_specs()
        requests = {}

        for illust_type, spec in specs.items():
            requests[illust_type] = self.generate_request_from_golden(
                illust_type,
                spec
            )

        return requests

    def save_golden_examples(self, output_dir: str = None):
        """Save golden examples as JSON files"""
        if output_dir is None:
            output_dir = Path(__file__).parent / "golden_examples"

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        requests = self.generate_all_test_requests()

        for illust_type, request in requests.items():
            output_file = output_dir / f"{illust_type}_request.json"
            with open(output_file, 'w') as f:
                json.dump(request.model_dump(), f, indent=2)

        print(f"✅ Saved {len(requests)} golden example requests to {output_dir}")


if __name__ == "__main__":
    generator = GoldenExampleGenerator()
    generator.save_golden_examples()

    # Print summary
    requests = generator.generate_all_test_requests()
    print(f"\n📊 Generated {len(requests)} test requests")
    print(f"   L01: {len([r for r in requests.values() if r.layout_id == 'L01'])}")
    print(f"   L25: {len([r for r in requests.values() if r.layout_id == 'L25'])}")
    print(f"   L02: {len([r for r in requests.values() if r.layout_id == 'L02'])}")
