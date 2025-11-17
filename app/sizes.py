"""
Size preset definitions

3 predefined sizes: Small, Medium, Large
"""

from dataclasses import dataclass
from math import gcd
from typing import Dict


@dataclass
class SizePreset:
    """Size preset for illustrations"""

    name: str
    width: int
    height: int

    @property
    def aspect_ratio(self) -> str:
        """Calculate aspect ratio as string (e.g., '3:2')"""
        divisor = gcd(self.width, self.height)
        return f"{self.width // divisor}:{self.height // divisor}"

    def to_dict(self) -> Dict[str, any]:
        """Convert size to dictionary"""
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "aspect_ratio": self.aspect_ratio
        }


# Small - Thumbnail previews, small slides
SMALL = SizePreset(
    name="small",
    width=600,
    height=400
)

# Medium - Standard PowerPoint slides (default)
MEDIUM = SizePreset(
    name="medium",
    width=1200,
    height=800
)

# Large - Widescreen presentations, banners
LARGE = SizePreset(
    name="large",
    width=1800,
    height=720
)

# Size registry
SIZES: Dict[str, SizePreset] = {
    "small": SMALL,
    "medium": MEDIUM,
    "large": LARGE
}


def get_size(size_name: str) -> SizePreset:
    """
    Get size preset by name

    Args:
        size_name: Name of the size preset

    Returns:
        SizePreset object

    Raises:
        KeyError: If size name is not found
    """
    if size_name not in SIZES:
        raise KeyError(
            f"Size '{size_name}' not found. "
            f"Available sizes: {', '.join(SIZES.keys())}"
        )
    return SIZES[size_name]


def list_sizes() -> list[Dict[str, any]]:
    """
    List all available size presets

    Returns:
        List of size dictionaries
    """
    return [size.to_dict() for size in SIZES.values()]
