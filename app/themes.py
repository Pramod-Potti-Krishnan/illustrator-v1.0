"""
Theme color definitions

4 predefined themes: Professional, Bold, Minimal, Playful
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Theme:
    """Color theme for illustrations"""

    name: str
    primary: str
    secondary: str
    background: str
    text: str
    text_on_primary: str
    border: str
    success: str
    warning: str
    danger: str

    def to_dict(self) -> Dict[str, str]:
        """Convert theme to dictionary for template substitution"""
        return {
            "theme_name": self.name,
            "theme_primary": self.primary,
            "theme_secondary": self.secondary,
            "theme_background": self.background,
            "theme_text": self.text,
            "theme_text_on_primary": self.text_on_primary,
            "theme_border": self.border,
            "theme_success": self.success,
            "theme_warning": self.warning,
            "theme_danger": self.danger
        }


# Professional Theme - Corporate and professional
PROFESSIONAL = Theme(
    name="professional",
    primary="#0066CC",
    secondary="#FF6B35",
    background="#FFFFFF",
    text="#1A1A1A",
    text_on_primary="#FFFFFF",
    border="#CCCCCC",
    success="#28A745",
    warning="#FFC107",
    danger="#DC3545"
)

# Bold Theme - Vibrant and attention-grabbing
BOLD = Theme(
    name="bold",
    primary="#E31E24",
    secondary="#FFD700",
    background="#F5F5F5",
    text="#000000",
    text_on_primary="#FFFFFF",
    border="#333333",
    success="#00C853",
    warning="#FF9100",
    danger="#D50000"
)

# Minimal Theme - Clean and understated
MINIMAL = Theme(
    name="minimal",
    primary="#2C3E50",
    secondary="#95A5A6",
    background="#FFFFFF",
    text="#34495E",
    text_on_primary="#FFFFFF",
    border="#BDC3C7",
    success="#27AE60",
    warning="#F39C12",
    danger="#E74C3C"
)

# Playful Theme - Energetic and creative
PLAYFUL = Theme(
    name="playful",
    primary="#9C27B0",
    secondary="#00BCD4",
    background="#FFFDE7",
    text="#424242",
    text_on_primary="#FFFFFF",
    border="#9E9E9E",
    success="#8BC34A",
    warning="#FF9800",
    danger="#F44336"
)

# Theme registry
THEMES: Dict[str, Theme] = {
    "professional": PROFESSIONAL,
    "bold": BOLD,
    "minimal": MINIMAL,
    "playful": PLAYFUL
}


def get_theme(theme_name: str) -> Theme:
    """
    Get theme by name

    Args:
        theme_name: Name of the theme

    Returns:
        Theme object

    Raises:
        KeyError: If theme name is not found
    """
    if theme_name not in THEMES:
        raise KeyError(
            f"Theme '{theme_name}' not found. "
            f"Available themes: {', '.join(THEMES.keys())}"
        )
    return THEMES[theme_name]


def list_themes() -> list[Dict[str, str]]:
    """
    List all available themes with their palettes

    Returns:
        List of theme dictionaries
    """
    return [
        {
            "name": theme.name,
            "palette": {
                "primary": theme.primary,
                "secondary": theme.secondary,
                "background": theme.background,
                "text": theme.text,
                "text_on_primary": theme.text_on_primary,
                "border": theme.border,
                "success": theme.success,
                "warning": theme.warning,
                "danger": theme.danger
            }
        }
        for theme in THEMES.values()
    ]
