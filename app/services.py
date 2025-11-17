"""
Template loading and filling service

Simple service that:
1. Loads HTML/CSS templates from disk
2. Fills placeholders with data
3. Applies theme colors
4. Returns filled HTML
"""

import logging
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any

from .themes import Theme, get_theme
from .sizes import SizePreset, get_size

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for loading and filling templates"""

    def __init__(self, templates_dir: Path):
        """
        Initialize template service

        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = templates_dir
        logger.info(f"TemplateService initialized with directory: {templates_dir}")

    @lru_cache(maxsize=128)
    def load_template(self, illustration_type: str, variant_id: str) -> str:
        """
        Load template from disk with caching

        Args:
            illustration_type: Type of illustration (e.g., 'swot_2x2')
            variant_id: Variant ID (e.g., 'base', 'rounded')

        Returns:
            Template HTML string

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = self.templates_dir / illustration_type / f"{variant_id}.html"

        if not template_path.exists():
            raise FileNotFoundError(
                f"Template not found: {template_path}. "
                f"Illustration type: '{illustration_type}', Variant: '{variant_id}'"
            )

        logger.info(f"Loading template: {template_path}")
        return template_path.read_text()

    def fill_template(
        self,
        template: str,
        data: Dict[str, Any],
        theme: Theme,
        size: SizePreset
    ) -> str:
        """
        Fill template with data and apply theme

        Args:
            template: Template HTML string with placeholders
            data: Data to fill into template
            theme: Theme object with color palette
            size: Size preset object

        Returns:
            Filled HTML string
        """
        # Prepare all substitutions
        substitutions = {
            # Size
            "width": size.width,
            "height": size.height,

            # Theme colors (all theme.* placeholders)
            **theme.to_dict(),

            # User data (merge last to allow potential overrides)
            **data
        }

        # Simple string replacement
        try:
            filled_html = template.format(**substitutions)
            logger.info(f"Template filled successfully. Size: {size.name}, Theme: {theme.name}")
            return filled_html
        except KeyError as e:
            logger.error(f"Missing placeholder in data: {e}")
            raise ValueError(
                f"Missing required field in data: {e}. "
                f"Template expects this placeholder but it wasn't provided."
            )

    def generate(
        self,
        illustration_type: str,
        variant_id: str,
        data: Dict[str, Any],
        theme_name: str,
        size_name: str
    ) -> str:
        """
        Full generation pipeline: Load → Fill → Return

        Args:
            illustration_type: Type of illustration
            variant_id: Variant ID
            data: Illustration data
            theme_name: Theme name
            size_name: Size preset name

        Returns:
            Filled HTML string

        Raises:
            FileNotFoundError: If template not found
            KeyError: If theme or size not found
            ValueError: If data missing required fields
        """
        # 1. Load template
        template = self.load_template(illustration_type, variant_id)

        # 2. Get theme and size
        theme = get_theme(theme_name)
        size = get_size(size_name)

        # 3. Fill template
        html = self.fill_template(template, data, theme, size)

        return html

    def list_available_templates(self) -> list[Dict[str, Any]]:
        """
        List all available templates (excludes archived templates)

        Returns:
            List of dictionaries with template info
        """
        available = []

        if not self.templates_dir.exists():
            return available

        for type_dir in self.templates_dir.iterdir():
            if type_dir.is_dir() and type_dir.name != "archive":  # Skip archive folder
                illustration_type = type_dir.name
                variants = []

                for template_file in type_dir.glob("*.html"):
                    variant_id = template_file.stem
                    variants.append(variant_id)

                if variants:
                    available.append({
                        "illustration_type": illustration_type,
                        "variants": sorted(variants)
                    })

        return sorted(available, key=lambda x: x["illustration_type"])
