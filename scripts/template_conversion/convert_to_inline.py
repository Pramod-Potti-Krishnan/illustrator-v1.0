#!/usr/bin/env python3
"""
Simple HTML to Inline Styles Converter

Converts complete HTML documents to fragments with inline styles.
Uses BeautifulSoup for reliable HTML parsing.
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import cssutils
import logging

# Suppress cssutils warnings
cssutils.log.setLevel(logging.CRITICAL)


def parse_css(css_text):
    """Parse CSS and return dict of {selector: {property: value}}."""
    css_rules = {}

    try:
        sheet = cssutils.parseString(css_text)
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                selector = rule.selectorText
                properties = {}

                for prop in rule.style:
                    prop_name = prop.name
                    prop_value = prop.value
                    prop_priority = prop.priority

                    if prop_priority:
                        properties[prop_name] = f"{prop_value} !important"
                    else:
                        properties[prop_name] = prop_value

                if selector not in css_rules:
                    css_rules[selector] = {}
                css_rules[selector].update(properties)

    except Exception as e:
        print(f"Warning: CSS parsing error: {e}")

    return css_rules


def selector_matches(selector, tag_name, classes, elem_id):
    """Check if selector matches element (simple matching only)."""
    # Skip pseudo-classes and media queries
    if any(x in selector for x in [':hover', ':before', ':after', '::before', '::after',
                                   '::marker', '@media', '@keyframes', ':nth-child']):
        return False

    # Universal selector
    if selector.strip() == '*':
        return True

    # Tag selector
    if selector.strip() == tag_name:
        return True

    # Class selector
    if selector.startswith('.'):
        class_name = selector[1:].split(':')[0].split('[')[0].strip()
        if class_name in classes:
            return True

    # ID selector
    if selector.startswith('#'):
        id_name = selector[1:].split(':')[0].split('[')[0].strip()
        if id_name == elem_id:
            return True

    # Combined tag.class
    if '.' in selector and not selector.startswith('.'):
        parts = selector.split('.')
        tag_part = parts[0].strip()
        class_part = parts[1].split(':')[0].split('[')[0].strip()
        if tag_part == tag_name and class_part in classes:
            return True

    # Tag#id
    if '#' in selector and not selector.startswith('#'):
        parts = selector.split('#')
        tag_part = parts[0].strip()
        id_part = parts[1].split(':')[0].split('[')[0].strip()
        if tag_part == tag_name and id_part == elem_id:
            return True

    return False


def get_matching_styles(css_rules, tag_name, classes, elem_id):
    """Get all styles matching this element."""
    styles = {}

    for selector, properties in css_rules.items():
        if selector_matches(selector, tag_name, classes, elem_id):
            styles.update(properties)

    return styles


def apply_inline_styles(element, css_rules):
    """Recursively apply inline styles to element and children."""
    if not hasattr(element, 'name') or element.name is None:
        return

    tag_name = element.name
    classes = element.get('class', [])
    elem_id = element.get('id', '')

    # Get matching CSS
    matching_styles = get_matching_styles(css_rules, tag_name, classes, elem_id)

    if matching_styles:
        # Parse existing inline styles
        existing_style = element.get('style', '')
        existing_props = {}

        if existing_style:
            for decl in existing_style.split(';'):
                decl = decl.strip()
                if ':' in decl:
                    prop, val = decl.split(':', 1)
                    existing_props[prop.strip()] = val.strip()

        # Merge (CSS rules < inline styles for precedence)
        merged = {}
        merged.update(matching_styles)
        merged.update(existing_props)

        # Build style string
        style_str = '; '.join(f'{k}: {v}' for k, v in merged.items())
        element['style'] = style_str

    # Recurse to children
    for child in element.children:
        apply_inline_styles(child, css_rules)


def convert_to_fragment(input_path, output_path, preserve_js=True):
    """Convert HTML document to inline-styled fragment."""
    print(f"Converting: {input_path.name}")

    # Read HTML
    html_content = input_path.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'lxml')

    # Extract CSS
    css_text = ''
    for style_tag in soup.find_all('style'):
        css_text += style_tag.string or ''
        style_tag.decompose()  # Remove style tag

    print(f"  - Extracted CSS ({len(css_text)} chars)")

    # Parse CSS
    css_rules = parse_css(css_text)
    print(f"  - Parsed {len(css_rules)} CSS rules")

    # Get body content
    body = soup.find('body')
    if not body:
        print("  ✗ No <body> tag found!")
        return

    # Apply inline styles to body content
    print("  - Applying inline styles...")
    for element in body.children:
        apply_inline_styles(element, css_rules)

    # Extract body content (excluding body tag itself)
    fragment_parts = []
    for element in body.children:
        if hasattr(element, 'name') and element.name:
            fragment_parts.append(str(element))
        elif hasattr(element, 'string') and element.string and element.string.strip():
            fragment_parts.append(str(element))

    fragment = '\n'.join(fragment_parts)

    # Preserve JavaScript if requested
    if preserve_js:
        scripts = soup.find_all('script')
        if scripts:
            print(f"  - Preserving {len(scripts)} <script> tag(s)")
            for script in scripts:
                fragment += '\n' + str(script)

    # Clean up
    fragment = fragment.strip()

    # Write output
    output_path.write_text(fragment, encoding='utf-8')
    print(f"  ✓ Saved: {output_path.name}")
    print(f"  ✓ Output size: {len(fragment)} chars")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_inline.py <input.html> [output.html]")
        print("   or: python convert_to_inline.py --batch <directory>")
        sys.exit(1)

    if sys.argv[1] == '--batch':
        if len(sys.argv) < 3:
            print("Error: --batch requires directory path")
            sys.exit(1)

        template_dir = Path(sys.argv[2])
        if not template_dir.is_dir():
            print(f"Error: {template_dir} is not a directory")
            sys.exit(1)

        print("=" * 70)
        print("BATCH CONVERSION: HTML to Inline-Styled Fragments")
        print("=" * 70)
        print()

        # Find all HTML files (excluding samples and archives)
        html_files = []
        for html_file in template_dir.rglob("*.html"):
            if 'sample' not in html_file.name and 'archive' not in str(html_file):
                html_files.append(html_file)

        print(f"Found {len(html_files)} templates to convert\n")

        for html_file in sorted(html_files):
            try:
                convert_to_fragment(html_file, html_file, preserve_js=True)
            except Exception as e:
                print(f"  ✗ Error converting {html_file.name}: {e}\n")

        print("=" * 70)
        print(f"BATCH CONVERSION COMPLETE: {len(html_files)} files processed")
        print("=" * 70)

    else:
        input_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path

        if not input_path.exists():
            print(f"Error: File not found: {input_path}")
            sys.exit(1)

        convert_to_fragment(input_path, output_path, preserve_js=True)
        print("✓ Conversion complete!")


if __name__ == '__main__':
    main()
