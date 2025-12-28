"""
Text Utilities for Illustrator Service

Provides text transformation functions for labels and content.
"""

import re
from typing import Optional


def to_title_case(text: Optional[str]) -> str:
    """
    Convert text to title case with exceptions for small words.

    - First word is always capitalized
    - Small words (and, of, the, etc.) stay lowercase unless first word
    - Handles <br> tags by processing text segments separately

    Args:
        text: The text to convert

    Returns:
        Title-cased text with proper handling of small words and HTML tags

    Examples:
        >>> to_title_case("PRODUCT DEVELOPMENT STRATEGY")
        'Product Development Strategy'
        >>> to_title_case("CORE OF THE BUSINESS")
        'Core of the Business'
        >>> to_title_case("VISION<br>STATEMENT")
        'Vision<br>Statement'
    """
    if not text:
        return ""

    # Words that should remain lowercase (unless first word)
    small_words = {
        'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in',
        'of', 'on', 'or', 'the', 'to', 'with', 'via', 'vs', 'nor'
    }

    # Split by <br> tags, preserving them
    parts = re.split(r'(<br\s*/?>)', text, flags=re.IGNORECASE)
    result_parts = []

    is_first_segment = True

    for part in parts:
        # If it's a <br> tag, preserve it as-is
        if re.match(r'<br\s*/?>', part, re.IGNORECASE):
            result_parts.append(part)
            is_first_segment = True  # Next segment starts fresh
        else:
            words = part.split()
            result = []
            for i, word in enumerate(words):
                word_lower = word.lower()
                # Capitalize if: first word of segment OR not a small word
                if (i == 0 and is_first_segment) or word_lower not in small_words:
                    result.append(word.capitalize())
                else:
                    result.append(word_lower)
            result_parts.append(' '.join(result))
            if words:  # Only mark as not first if we had words
                is_first_segment = False

    return ''.join(result_parts)


def apply_title_case_to_labels(content: dict, label_keys: list) -> dict:
    """
    Apply title case transformation to specified keys in a content dictionary.

    Args:
        content: Dictionary containing label values
        label_keys: List of keys to transform (e.g., ['level_1_label', 'level_2_label'])

    Returns:
        Modified dictionary with title-cased labels
    """
    result = content.copy()
    for key in label_keys:
        if key in result and result[key]:
            result[key] = to_title_case(result[key])
    return result
