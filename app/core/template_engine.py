"""
Template Engine for Illustrator Service v1.0
============================================

Fills HTML templates with data and applies themes.
"""

from pathlib import Path
from typing import Dict, Any
import sys

# Import themes
sys.path.insert(0, str(Path(__file__).parent.parent))
from themes import THEMES


class TemplateEngine:
    """Fills HTML templates with data and applies themes"""

    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            base_dir = Path(__file__).parent.parent.parent
            templates_dir = base_dir / "templates"
        self.templates_dir = Path(templates_dir)

    def load_template(self, illustration_type: str, variant_id: str = "base") -> str:
        """Load HTML template"""
        template_path = self.templates_dir / illustration_type / f"{variant_id}.html"
        with open(template_path, 'r') as f:
            return f.read()

    def fill_template(
        self,
        template: str,
        data: Dict[str, Any],
        theme: Dict[str, str]
    ) -> str:
        """Fill template placeholders with data and theme"""
        # Apply theme colors first
        for key, value in theme.items():
            placeholder = f"{{{key}}}"
            template = template.replace(placeholder, value)

        # Apply data
        template = self._fill_data(template, data)

        return template

    def _fill_data(self, template: str, data: Dict[str, Any], prefix: str = "") -> str:
        """Recursively fill template with nested data"""
        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key

            if isinstance(value, list):
                # Convert list to HTML list items
                if all(isinstance(item, str) for item in value):
                    html_items = "".join([f"<li>{item}</li>" for item in value])
                    # Try both {key} and {key_items} placeholders
                    template = template.replace(f"{{{full_key}}}", html_items)
                    template = template.replace(f"{{{full_key}_items}}", html_items)
                elif all(isinstance(item, dict) for item in value):
                    # Handle list of dicts (e.g., process steps)
                    html_items = self._render_list_of_dicts(value, full_key)
                    template = template.replace(f"{{{full_key}}}", html_items)
                    # Also try {key_items} for dict lists
                    template = template.replace(f"{{{full_key}_items}}", html_items)
                    # Also try common prefixes like {process_steps} for data key "steps"
                    if not full_key.startswith("process_") and "step" in str(value[0].keys()).lower():
                        template = template.replace(f"{{process_{full_key}}}", html_items)
                    if not full_key.startswith("timeline_") and "date" in str(value[0].keys()).lower():
                        template = template.replace(f"{{timeline_{full_key}}}", html_items)
            elif isinstance(value, dict):
                # Handle nested dict (e.g., tier1, tier2)
                template = self._fill_data(template, value, f"{full_key}_")
            else:
                # Simple string replacement
                template = template.replace(f"{{{full_key}}}", str(value))

        return template

    def _render_list_of_dicts(self, items: list, key: str) -> str:
        """Render list of dicts as HTML (for process steps, timeline events, etc.)"""
        html_parts = []

        for idx, item in enumerate(items):
            if "number" in item and "title" in item:
                # Process step or funnel stage
                html = f"""
                <div class="step">
                    <div class="step-number">{item.get('number', idx + 1)}</div>
                    <div class="step-title">{item['title']}</div>
                    <div class="step-description">{item.get('description', '')}</div>
                </div>
                """
                html_parts.append(html)
            elif "date" in item and "title" in item:
                # Timeline event
                html = f"""
                <div class="timeline-event">
                    <div class="event-marker"></div>
                    <div class="event-date">{item['date']}</div>
                    <div class="event-title">{item['title']}</div>
                    <div class="event-description">{item.get('description', '')}</div>
                </div>
                """
                html_parts.append(html)

        if not html_parts:
            # Generic rendering
            for item in items:
                html_parts.append(f"<div>{item}</div>")

        return "".join(html_parts)

    def generate_illustration(
        self,
        illustration_type: str,
        data: Dict[str, Any],
        theme_name: str = "professional",
        variant_id: str = "base"
    ) -> str:
        """Complete illustration generation pipeline"""
        # Load template
        template = self.load_template(illustration_type, variant_id)

        # Get theme
        theme = THEMES[theme_name].to_dict()

        # Apply illustration-specific data mappings before filling
        mapped_data = self._map_data_to_template(illustration_type, data)

        # Fill template
        html = self.fill_template(template, mapped_data, theme)

        return html

    def _map_data_to_template(self, illustration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map golden example data to template-expected field names.

        Some templates use different field names than the golden examples.
        This method creates a normalized data structure with both naming conventions.
        """
        mapped = data.copy()

        # Common mappings based on illustration type
        if illustration_type == "process_flow_horizontal":
            if "steps" in data and "process_steps" not in data:
                mapped["process_steps"] = data["steps"]
        elif illustration_type == "timeline_horizontal":
            if "events" in data and "timeline_events" not in data:
                mapped["timeline_events"] = data["events"]

        return mapped


if __name__ == "__main__":
    # Test template engine
    engine = TemplateEngine()

    # Test with simple data
    test_data = {
        "pros": ["Strong brand", "Good financials"],
        "cons": ["High costs", "Limited presence"]
    }

    try:
        html = engine.generate_illustration("pros_cons", test_data, "professional")
        print(f"✅ Template engine working: {len(html)} chars generated")
    except Exception as e:
        print(f"❌ Template engine error: {e}")
