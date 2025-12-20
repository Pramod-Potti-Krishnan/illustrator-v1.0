"""
Coordination Models for Director Integration

Pydantic models for the capabilities, can-handle, and recommend-visual endpoints
required by Director Agent v4.0's Strawman Service.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class ServiceStatus(str, Enum):
    """Service operational status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class VisualType(str, Enum):
    """Supported visualization types."""
    PYRAMID = "pyramid"
    FUNNEL = "funnel"
    CONCENTRIC_CIRCLES = "concentric_circles"


# === Phase 1: Capabilities Models ===

class ItemCountRange(BaseModel):
    """Range of items supported by a visualization type."""
    min: int
    max: int
    optimal: int


class SpaceDimensions(BaseModel):
    """Width and height dimensions in pixels."""
    width: int
    height: int


class SpaceRequirements(BaseModel):
    """Minimum and optimal space requirements for a visualization."""
    min: SpaceDimensions
    optimal: SpaceDimensions


class VisualizationSpecialization(BaseModel):
    """Detailed info about a specific visualization type."""
    description: str
    best_for: List[str]
    keywords: List[str]
    ideal_item_count: ItemCountRange
    space_requirements: SpaceRequirements


class ContentSignals(BaseModel):
    """Signals indicating what content types this service handles."""
    handles_well: List[str]
    handles_poorly: List[str]
    keywords: List[str]


class ServiceCapabilities(BaseModel):
    """Core capabilities of the service."""
    slide_types: List[str]
    visualization_types: List[str]
    supports_themes: bool
    ai_generated_content: bool
    supported_layouts: List[str]


class CapabilitiesResponse(BaseModel):
    """Response for GET /capabilities endpoint."""
    service: str
    version: str
    status: ServiceStatus
    capabilities: ServiceCapabilities
    content_signals: ContentSignals
    specializations: Dict[str, VisualizationSpecialization]
    endpoints: Dict[str, str]


# === Phase 2: Can-Handle Models ===

class SlideContent(BaseModel):
    """Content of a slide to be analyzed."""
    title: str
    topics: List[str]
    topic_count: int


class ContentHints(BaseModel):
    """Hints about the content to assist analysis."""
    has_numbers: bool = False
    is_comparison: bool = False
    is_time_based: bool = False
    detected_keywords: List[str] = Field(default_factory=list)


class SubZone(BaseModel):
    """A sub-zone within the available space."""
    zone_id: str
    width: int
    height: int


class AvailableSpace(BaseModel):
    """Available space for rendering the visual."""
    width: int
    height: int
    sub_zones: Optional[List[SubZone]] = None
    layout_id: Optional[str] = None


class CanHandleRequest(BaseModel):
    """Request body for POST /v1.0/can-handle endpoint."""
    slide_content: SlideContent
    content_hints: Optional[ContentHints] = None
    available_space: Optional[AvailableSpace] = None


class SpaceUtilization(BaseModel):
    """Information about how well content fits the space."""
    fits_well: bool
    estimated_fill_percent: int = Field(ge=0, le=100)


class AlternativeApproach(BaseModel):
    """Alternative visualization approach suggestion."""
    visual_type: str
    confidence: float = Field(ge=0, le=1)
    reason: str


class CanHandleResponse(BaseModel):
    """Response for POST /v1.0/can-handle endpoint."""
    can_handle: bool
    confidence: float = Field(ge=0, le=1)
    reason: str
    suggested_approach: Optional[str] = None
    space_utilization: Optional[SpaceUtilization] = None
    alternative_approaches: Optional[List[AlternativeApproach]] = None


# === Phase 3: Recommend-Visual Models ===

class Preferences(BaseModel):
    """User preferences for visualization style."""
    style: str = "professional"
    complexity: str = "medium"


class RecommendRequest(BaseModel):
    """Request body for POST /v1.0/recommend-visual endpoint."""
    slide_content: SlideContent
    available_space: Optional[AvailableSpace] = None
    preferences: Optional[Preferences] = None


class VariantConfig(BaseModel):
    """Configuration for the recommended variant."""
    num_levels: Optional[int] = None
    num_stages: Optional[int] = None
    num_circles: Optional[int] = None
    style: Optional[str] = None


class SpaceReqs(BaseModel):
    """Space requirements for a recommendation."""
    width: int
    height: int
    fits_available: bool


class VisualRecommendation(BaseModel):
    """A single visual type recommendation."""
    visual_type: str
    confidence: float = Field(ge=0, le=1)
    reason: str
    variant: Optional[VariantConfig] = None
    space_requirements: Optional[SpaceReqs] = None
    generation_endpoint: str


class NotRecommended(BaseModel):
    """A visual type that is not recommended with reason."""
    visual_type: str
    reason: str


class FallbackRecommendation(BaseModel):
    """Fallback recommendation to another service."""
    service: str
    reason: str


class RecommendResponse(BaseModel):
    """Response for POST /v1.0/recommend-visual endpoint."""
    recommended_visuals: List[VisualRecommendation]
    not_recommended: Optional[List[NotRecommended]] = None
    fallback_recommendation: Optional[FallbackRecommendation] = None
