"""
Response Models for Layout Service Integration

Defines the response schema for the unified infographic generation endpoint.
Aligns with the Layout Service API specification.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RenderedOutput(BaseModel):
    """Rendered output in multiple formats."""
    svg: str = Field(
        ...,
        description="Complete SVG content (always present)"
    )
    html: str = Field(
        ...,
        description="HTML wrapper with embedded SVG"
    )
    png: Optional[str] = Field(
        default=None,
        description="Base64-encoded PNG image (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "svg": "<svg viewBox=\"0 0 1200 600\">...</svg>",
                "html": "<div class=\"infographic-container\"><svg>...</svg></div>",
                "png": None
            }
        }


class InfographicMetadata(BaseModel):
    """Metadata about the generated infographic."""
    type: str = Field(
        ...,
        description="Infographic type that was generated"
    )
    itemCount: int = Field(
        ...,
        description="Number of items in the infographic"
    )
    dimensions: Dict[str, int] = Field(
        ...,
        description="Actual dimensions in pixels (width, height)"
    )
    aspectRatio: float = Field(
        ...,
        description="Aspect ratio (width / height)"
    )
    colorPalette: List[str] = Field(
        ...,
        description="Colors used in the infographic (hex values)"
    )
    iconsUsed: Optional[List[str]] = Field(
        default=None,
        description="Icons/emojis used in the infographic"
    )
    generationMethod: str = Field(
        ...,
        description="Generation method: 'template' or 'dynamic_svg'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "timeline",
                "itemCount": 5,
                "dimensions": {"width": 1500, "height": 450},
                "aspectRatio": 3.33,
                "colorPalette": ["#1E40AF", "#3B82F6", "#60A5FA"],
                "iconsUsed": ["rocket", "chart", "target"],
                "generationMethod": "dynamic_svg"
            }
        }


class EditableItem(BaseModel):
    """Information about an editable item in the infographic."""
    itemId: str = Field(
        ...,
        description="Unique identifier for the item"
    )
    itemType: str = Field(
        ...,
        description="Type of item: 'title', 'description', 'label', 'icon'"
    )
    currentValue: str = Field(
        ...,
        description="Current value of the item"
    )
    maxLength: Optional[int] = Field(
        default=None,
        description="Maximum allowed length for text items"
    )
    position: Optional[int] = Field(
        default=None,
        description="Position/order of the item (0-based)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "itemId": "item_001",
                "itemType": "title",
                "currentValue": "2020: Foundation",
                "maxLength": 50,
                "position": 0
            }
        }


class EditInfo(BaseModel):
    """Information about editing capabilities."""
    editableItems: List[EditableItem] = Field(
        default_factory=list,
        description="List of items that can be edited"
    )
    reorderableItems: bool = Field(
        default=False,
        description="Whether items can be reordered"
    )
    addableItems: bool = Field(
        default=False,
        description="Whether new items can be added"
    )
    deletableItems: bool = Field(
        default=False,
        description="Whether items can be deleted"
    )
    maxItems: Optional[int] = Field(
        default=None,
        description="Maximum number of items allowed"
    )
    minItems: Optional[int] = Field(
        default=None,
        description="Minimum number of items required"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "editableItems": [],
                "reorderableItems": True,
                "addableItems": True,
                "deletableItems": True,
                "maxItems": 10,
                "minItems": 3
            }
        }


class ErrorResponse(BaseModel):
    """Error information when generation fails."""
    code: str = Field(
        ...,
        description="Error code (e.g., INVALID_TYPE, GENERATION_FAILED)"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    retryable: bool = Field(
        default=False,
        description="Whether the request can be retried"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )
    suggestion: Optional[str] = Field(
        default=None,
        description="Suggestion for fixing the error"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": "CONSTRAINT_VIOLATION",
                "message": "Grid size too small for timeline infographic",
                "retryable": False,
                "details": {"minWidth": 8, "providedWidth": 4},
                "suggestion": "Use a minimum grid width of 8 for timelines"
            }
        }


class InfographicItem(BaseModel):
    """
    A single item in the infographic.
    Structure varies by infographic type.
    """
    id: str = Field(
        ...,
        description="Unique identifier for the item"
    )
    title: str = Field(
        ...,
        description="Item title/label"
    )
    description: Optional[str] = Field(
        default=None,
        description="Item description"
    )
    icon: Optional[str] = Field(
        default=None,
        description="Icon identifier or emoji"
    )
    value: Optional[Any] = Field(
        default=None,
        description="Value (for statistics, percentages, etc.)"
    )
    color: Optional[str] = Field(
        default=None,
        description="Color for this item (hex)"
    )
    position: Optional[int] = Field(
        default=None,
        description="Position/order in the infographic"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional type-specific metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "item_001",
                "title": "Foundation Year",
                "description": "Company was established",
                "icon": "rocket",
                "value": "2020",
                "color": "#1E40AF",
                "position": 0
            }
        }


class InfographicData(BaseModel):
    """
    Structured data representation of the infographic.
    Enables programmatic editing and regeneration.
    """
    items: List[InfographicItem] = Field(
        default_factory=list,
        description="List of items in the infographic"
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional overall title"
    )
    subtitle: Optional[str] = Field(
        default=None,
        description="Optional subtitle"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "item_001",
                        "title": "2020",
                        "description": "Company founded",
                        "icon": "rocket",
                        "position": 0
                    }
                ],
                "title": "Our Journey",
                "metadata": {"orientation": "horizontal"}
            }
        }


class ResponseData(BaseModel):
    """Successful response data payload."""
    generationId: str = Field(
        ...,
        description="Unique identifier for this generation"
    )
    rendered: RenderedOutput = Field(
        ...,
        description="Rendered output in multiple formats"
    )
    infographicData: InfographicData = Field(
        ...,
        description="Structured data for the infographic"
    )
    metadata: InfographicMetadata = Field(
        ...,
        description="Metadata about the generation"
    )
    editInfo: EditInfo = Field(
        default_factory=EditInfo,
        description="Information about editing capabilities"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "generationId": "gen_abc123xyz",
                "rendered": {
                    "svg": "<svg>...</svg>",
                    "html": "<div>...</div>"
                },
                "infographicData": {
                    "items": [],
                    "metadata": {}
                },
                "metadata": {
                    "type": "timeline",
                    "itemCount": 5,
                    "dimensions": {"width": 1500, "height": 450},
                    "aspectRatio": 3.33,
                    "colorPalette": ["#1E40AF"],
                    "generationMethod": "dynamic_svg"
                },
                "editInfo": {
                    "editableItems": [],
                    "reorderableItems": True,
                    "addableItems": True,
                    "maxItems": 10
                }
            }
        }


class InfographicGenerateResponse(BaseModel):
    """
    Response model for the unified infographic generation endpoint.

    Returns either success with data, or error information.
    """
    success: bool = Field(
        ...,
        description="Whether the generation was successful"
    )
    data: Optional[ResponseData] = Field(
        default=None,
        description="Response data (present when success=True)"
    )
    error: Optional[ErrorResponse] = Field(
        default=None,
        description="Error information (present when success=False)"
    )

    # Echo request identifiers for correlation
    presentationId: Optional[str] = Field(
        default=None,
        description="Echoed presentation ID"
    )
    slideId: Optional[str] = Field(
        default=None,
        description="Echoed slide ID"
    )
    elementId: Optional[str] = Field(
        default=None,
        description="Echoed element ID"
    )

    # Timing
    generationTimeMs: Optional[int] = Field(
        default=None,
        description="Total generation time in milliseconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "generationId": "gen_abc123",
                    "rendered": {
                        "svg": "<svg>...</svg>",
                        "html": "<div>...</div>"
                    },
                    "infographicData": {"items": [], "metadata": {}},
                    "metadata": {
                        "type": "timeline",
                        "itemCount": 5,
                        "dimensions": {"width": 1500, "height": 450},
                        "aspectRatio": 3.33,
                        "colorPalette": ["#1E40AF"],
                        "generationMethod": "dynamic_svg"
                    },
                    "editInfo": {"editableItems": [], "reorderableItems": True}
                },
                "presentationId": "pres_abc123",
                "slideId": "slide_xyz789",
                "elementId": "elem_001",
                "generationTimeMs": 2450
            }
        }
