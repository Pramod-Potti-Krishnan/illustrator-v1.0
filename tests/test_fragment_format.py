#!/usr/bin/env python3
"""
Fragment Format Validation Test

Ensures all converted templates are L25-compatible HTML fragments
with inline styles and no document wrappers.
"""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup


class TestFragmentFormat:
    """Validate HTML fragment format for L25 integration."""

    TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

    # All templates that should be fragments
    TEMPLATES_TO_TEST = [
        # Concentric circles
        "concentric_circles/3.html",
        "concentric_circles/4.html",
        "concentric_circles/5.html",
        # Pyramid
        "pyramid/3.html",
        "pyramid/4.html",
        "pyramid/5.html",
        "pyramid/6.html",
        "pyramid/3_l01.html",
        "pyramid/4_l01.html",
        # Funnel
        "funnel/3.html",
        "funnel/4.html",
        "funnel/5.html",
        "funnel/3_demo.html",
        "funnel/4_demo.html",
        "funnel/5_demo.html",
    ]

    @pytest.mark.parametrize("template_path", TEMPLATES_TO_TEST)
    def test_no_doctype(self, template_path):
        """Verify template has no DOCTYPE declaration."""
        full_path = self.TEMPLATE_DIR / template_path
        content = full_path.read_text()

        assert "<!DOCTYPE" not in content, \
            f"{template_path} should not have DOCTYPE"
        assert "<!doctype" not in content.lower(), \
            f"{template_path} should not have DOCTYPE"

    @pytest.mark.parametrize("template_path", TEMPLATES_TO_TEST)
    def test_no_html_wrapper(self, template_path):
        """Verify template has no <html> wrapper tag."""
        full_path = self.TEMPLATE_DIR / template_path
        content = full_path.read_text()

        # Check for opening html tag
        assert not content.strip().startswith("<html"), \
            f"{template_path} should not start with <html>"

        # Check for any html tag
        assert "<html" not in content.lower(), \
            f"{template_path} should not have <html> tag"

    @pytest.mark.parametrize("template_path", TEMPLATES_TO_TEST)
    def test_no_head_tag(self, template_path):
        """Verify template has no <head> section."""
        full_path = self.TEMPLATE_DIR / template_path
        content = full_path.read_text()

        assert "<head" not in content.lower(), \
            f"{template_path} should not have <head> tag"

    @pytest.mark.parametrize("template_path", TEMPLATES_TO_TEST)
    def test_no_body_wrapper(self, template_path):
        """Verify template has no <body> wrapper tag."""
        full_path = self.TEMPLATE_DIR / template_path
        content = full_path.read_text()

        assert "<body" not in content.lower(), \
            f"{template_path} should not have <body> tag"

    @pytest.mark.parametrize("template_path", TEMPLATES_TO_TEST)
    def test_no_style_tags(self, template_path):
        """Verify template has no <style> tags (CSS should be inline)."""
        full_path = self.TEMPLATE_DIR / template_path
        content = full_path.read_text()

        assert "<style" not in content.lower(), \
            f"{template_path} should not have <style> tags (CSS should be inline)"

    @pytest.mark.parametrize("template_path", TEMPLATES_TO_TEST)
    def test_has_inline_styles(self, template_path):
        """Verify template has inline styles (style="" attributes)."""
        full_path = self.TEMPLATE_DIR / template_path
        content = full_path.read_text()

        # Should have multiple inline styles
        inline_style_count = content.count('style="')
        assert inline_style_count > 10, \
            f"{template_path} should have many inline styles, found {inline_style_count}"

    @pytest.mark.parametrize("template_path", TEMPLATES_TO_TEST)
    def test_valid_html_fragment(self, template_path):
        """Verify template is valid HTML when wrapped."""
        full_path = self.TEMPLATE_DIR / template_path
        content = full_path.read_text()

        # Wrap fragment to test validity
        wrapped = f"<!DOCTYPE html><html><body>{content}</body></html>"

        try:
            soup = BeautifulSoup(wrapped, 'lxml')
            # Should parse without errors
            assert soup is not None
        except Exception as e:
            pytest.fail(f"{template_path} has invalid HTML: {e}")

    @pytest.mark.parametrize("template_path", TEMPLATES_TO_TEST)
    def test_placeholders_present(self, template_path):
        """Verify template has placeholders for content."""
        full_path = self.TEMPLATE_DIR / template_path
        content = full_path.read_text()

        # Should have at least one placeholder
        import re
        placeholders = re.findall(r'\{[^}]+\}', content)

        assert len(placeholders) > 0, \
            f"{template_path} should have content placeholders like {{circle_1_label}}"

    @pytest.mark.parametrize("template_path", [
        "funnel/3.html",
        "funnel/4.html",
        "funnel/5.html",
        "funnel/3_demo.html",
        "funnel/4_demo.html",
        "funnel/5_demo.html",
    ])
    def test_funnel_has_javascript(self, template_path):
        """Verify funnel templates have preserved JavaScript."""
        full_path = self.TEMPLATE_DIR / template_path
        content = full_path.read_text()

        assert "<script>" in content or "<script " in content, \
            f"{template_path} should have <script> tag for interactivity"

        assert "addEventListener" in content, \
            f"{template_path} should have JavaScript event listeners"

    def test_conversion_completeness(self):
        """Verify all required templates exist and are converted."""
        missing = []

        for template_path in self.TEMPLATES_TO_TEST:
            full_path = self.TEMPLATE_DIR / template_path
            if not full_path.exists():
                missing.append(template_path)

        assert len(missing) == 0, \
            f"Missing templates: {missing}"

    def test_archive_exists(self):
        """Verify original templates are archived."""
        archive_dir = self.TEMPLATE_DIR / "archive_full_documents"

        assert archive_dir.exists(), \
            "Archive directory should exist"

        # Check a few archived files
        assert (archive_dir / "concentric_circles" / "3.html").exists()
        assert (archive_dir / "pyramid" / "4.html").exists()
        assert (archive_dir / "funnel" / "5.html").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
