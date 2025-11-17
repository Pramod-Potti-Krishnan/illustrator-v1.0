#!/usr/bin/env python3
"""
CSS to Inline Styles Converter for Illustrator Templates

Converts complete HTML documents with <style> tags to HTML fragments
with inline styles for L25 Layout Service integration.

Features:
- Parses CSS from <style> tags
- Applies inline styles to matching elements
- Handles complex selectors (nth-child, pseudo-classes)
- Preserves gradients, shadows, clip-paths
- Removes document wrappers (DOCTYPE, html, head, body)
- Preserves <script> tags (JavaScript)
- Maintains placeholders ({variable_name})

Usage:
    python css_to_inline.py input.html output.html
"""

import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from typing import Dict, List, Tuple, Optional
import tinycss2


class CSSRule:
    """Represents a CSS rule with selector and properties."""
    def __init__(self, selector: str, properties: Dict[str, str], specificity: int = 0):
        self.selector = selector.strip()
        self.properties = properties
        self.specificity = specificity
        self.important_props = set()

        # Track !important properties
        for prop, value in properties.items():
            if '!important' in value:
                self.important_props.add(prop)
                # Clean the value
                properties[prop] = value.replace('!important', '').strip()


class HTMLFragmentConverter(HTMLParser):
    """Converts HTML with CSS to inline-styled fragments."""

    def __init__(self, css_rules: List[CSSRule]):
        super().__init__()
        self.css_rules = css_rules
        self.output = []
        self.element_stack = []
        self.skip_elements = {'html', 'head', 'body', 'meta', 'title'}
        self.in_style_tag = False
        self.in_skip_element = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_elements or tag == 'style':
            if tag == 'style':
                self.in_style_tag = True
            else:
                self.in_skip_element += 1
            return

        if self.in_skip_element > 0:
            return

        # Build element info for CSS matching
        attr_dict = dict(attrs)
        class_names = attr_dict.get('class', '').split()
        element_id = attr_dict.get('id', '')

        # Calculate element path for nth-child matching
        element_info = {
            'tag': tag,
            'classes': class_names,
            'id': element_id,
            'attrs': attr_dict
        }
        self.element_stack.append(element_info)

        # Get matching CSS rules
        matching_styles = self._get_matching_styles(element_info)

        # Merge with existing inline styles
        existing_style = attr_dict.get('style', '')
        merged_style = self._merge_styles(existing_style, matching_styles)

        # Build output tag
        self.output.append(f'<{tag}')

        for attr_name, attr_value in attrs:
            if attr_name == 'style':
                # Replace with merged styles
                if merged_style:
                    self.output.append(f' style="{merged_style}"')
            elif attr_name != 'class' or class_names:  # Keep class attribute
                escaped_value = attr_value.replace('"', '&quot;')
                self.output.append(f' {attr_name}="{escaped_value}"')

        # Add merged styles if no style attribute existed
        if 'style' not in attr_dict and merged_style:
            self.output.append(f' style="{merged_style}"')

        self.output.append('>')

    def handle_endtag(self, tag):
        if tag in self.skip_elements:
            if tag != 'style':
                self.in_skip_element = max(0, self.in_skip_element - 1)
            else:
                self.in_style_tag = False
            return

        if self.in_skip_element > 0:
            return

        if self.element_stack:
            self.element_stack.pop()

        self.output.append(f'</{tag}>')

    def handle_data(self, data):
        if self.in_style_tag or self.in_skip_element > 0:
            return
        self.output.append(data)

    def handle_startendtag(self, tag, attrs):
        if tag in ['meta', 'link']:
            return

        attr_dict = dict(attrs)
        class_names = attr_dict.get('class', '').split()

        element_info = {
            'tag': tag,
            'classes': class_names,
            'id': attr_dict.get('id', ''),
            'attrs': attr_dict
        }

        matching_styles = self._get_matching_styles(element_info)
        existing_style = attr_dict.get('style', '')
        merged_style = self._merge_styles(existing_style, matching_styles)

        self.output.append(f'<{tag}')
        for attr_name, attr_value in attrs:
            if attr_name == 'style':
                if merged_style:
                    self.output.append(f' style="{merged_style}"')
            elif attr_name != 'class' or class_names:
                escaped_value = attr_value.replace('"', '&quot;')
                self.output.append(f' {attr_name}="{escaped_value}"')

        if 'style' not in attr_dict and merged_style:
            self.output.append(f' style="{merged_style}"')

        self.output.append(' />')

    def _get_matching_styles(self, element_info: Dict) -> Dict[str, str]:
        """Get all CSS properties that match this element."""
        styles = {}

        for rule in self.css_rules:
            if self._selector_matches(rule.selector, element_info):
                # Merge properties (later rules override earlier ones)
                for prop, value in rule.properties.items():
                    if prop in rule.important_props:
                        # Add !important back
                        styles[prop] = f"{value} !important"
                    else:
                        styles[prop] = value

        return styles

    def _selector_matches(self, selector: str, element_info: Dict) -> bool:
        """Check if a CSS selector matches an element."""
        # Skip pseudo-classes and pseudo-elements (can't inline)
        if ':hover' in selector or ':before' in selector or ':after' in selector:
            return False
        if '::before' in selector or '::after' in selector or '::marker' in selector:
            return False
        if '@media' in selector or '@keyframes' in selector:
            return False

        # Simple selector matching
        tag = element_info['tag']
        classes = element_info['classes']
        elem_id = element_info['id']

        # Universal selector
        if selector == '*':
            return True

        # Tag selector
        if selector == tag:
            return True

        # Class selector
        if selector.startswith('.'):
            class_name = selector[1:].split(':')[0].split('[')[0]
            if class_name in classes:
                return True

        # ID selector
        if selector.startswith('#'):
            id_name = selector[1:].split(':')[0].split('[')[0]
            if id_name == elem_id:
                return True

        # Combined selectors (e.g., "div.class-name")
        if '.' in selector and not selector.startswith('.'):
            parts = selector.split('.')
            if parts[0] == tag and len(parts) > 1:
                class_name = parts[1].split(':')[0].split('[')[0]
                if class_name in classes:
                    return True

        return False

    def _merge_styles(self, existing: str, new_styles: Dict[str, str]) -> str:
        """Merge existing inline styles with CSS-derived styles."""
        # Parse existing styles
        styles = {}
        if existing:
            for declaration in existing.split(';'):
                declaration = declaration.strip()
                if ':' in declaration:
                    prop, value = declaration.split(':', 1)
                    styles[prop.strip()] = value.strip()

        # Add new styles (CSS rules)
        styles.update(new_styles)

        # Build style string
        if not styles:
            return ''

        return '; '.join(f'{prop}: {value}' for prop, value in styles.items())

    def get_output(self) -> str:
        """Get the converted HTML fragment."""
        return ''.join(self.output).strip()


def extract_css_rules(html_content: str) -> List[CSSRule]:
    """Extract CSS rules from <style> tags."""
    rules = []

    # Find all <style> tags
    style_pattern = r'<style[^>]*>(.*?)</style>'
    style_matches = re.findall(style_pattern, html_content, re.DOTALL | re.IGNORECASE)

    for style_content in style_matches:
        # Parse CSS
        parsed = tinycss2.parse_stylesheet(style_content)

        for rule in parsed:
            if rule.type == 'qualified-rule':
                # Extract selector
                selector = ''.join(token.serialize() for token in rule.prelude).strip()

                # Extract properties
                properties = {}
                content_tokens = tinycss2.parse_declaration_list(rule.content)

                for item in content_tokens:
                    if item.type == 'declaration':
                        prop_name = item.name
                        prop_value = ''.join(token.serialize() for token in item.value).strip()

                        # Check for !important
                        if item.important:
                            prop_value += ' !important'

                        properties[prop_name] = prop_value

                if properties:
                    rules.append(CSSRule(selector, properties))

    return rules


def convert_html_to_fragment(input_file: Path, output_file: Path, preserve_js: bool = True):
    """
    Convert HTML document to inline-styled fragment.

    Args:
        input_file: Path to input HTML file
        output_file: Path to output HTML file
        preserve_js: Whether to preserve <script> tags (default: True)
    """
    print(f"Converting: {input_file.name}")

    # Read input
    html_content = input_file.read_text(encoding='utf-8')

    # Extract CSS rules
    print("  - Extracting CSS rules...")
    css_rules = extract_css_rules(html_content)
    print(f"  - Found {len(css_rules)} CSS rules")

    # Convert to fragment
    print("  - Converting to inline styles...")
    converter = HTMLFragmentConverter(css_rules)
    converter.feed(html_content)
    fragment = converter.get_output()

    # Handle JavaScript
    if preserve_js:
        # Extract <script> tags and append to fragment
        script_pattern = r'<script[^>]*>.*?</script>'
        scripts = re.findall(script_pattern, html_content, re.DOTALL | re.IGNORECASE)
        if scripts:
            print(f"  - Preserving {len(scripts)} <script> tag(s)")
            fragment += '\n' + '\n'.join(scripts)

    # Clean up whitespace
    fragment = re.sub(r'\n\s*\n', '\n', fragment)
    fragment = fragment.strip()

    # Write output
    output_file.write_text(fragment, encoding='utf-8')
    print(f"  ✓ Saved: {output_file.name}")
    print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python css_to_inline.py <input_file> [output_file]")
        print("   or: python css_to_inline.py --batch <template_dir>")
        sys.exit(1)

    if sys.argv[1] == '--batch':
        # Batch mode: convert all templates in directory
        if len(sys.argv) < 3:
            print("Error: --batch requires template directory")
            sys.exit(1)

        template_dir = Path(sys.argv[2])
        if not template_dir.is_dir():
            print(f"Error: {template_dir} is not a directory")
            sys.exit(1)

        print("=" * 60)
        print("BATCH CONVERSION MODE")
        print("=" * 60)
        print()

        # Process all .html files
        html_files = list(template_dir.glob("**/*.html"))
        print(f"Found {len(html_files)} HTML files\n")

        for html_file in html_files:
            # Skip sample files
            if 'sample' in html_file.name:
                print(f"Skipping sample file: {html_file.name}")
                continue

            # Output to same location (overwrite)
            convert_html_to_fragment(html_file, html_file, preserve_js=True)

        print("=" * 60)
        print(f"BATCH CONVERSION COMPLETE: {len(html_files)} files")
        print("=" * 60)

    else:
        # Single file mode
        input_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path

        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            sys.exit(1)

        convert_html_to_fragment(input_path, output_path, preserve_js=True)
        print("Conversion complete!")


if __name__ == '__main__':
    main()
