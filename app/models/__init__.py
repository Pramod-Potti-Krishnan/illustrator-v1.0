"""
Illustrator Service Models

All Pydantic models for request/response validation.
"""

# Layout Service Integration Models (new)
from .layout_service_request import (
    InfographicType,
    GridConstraints,
    StyleOptions,
    ContentOptions,
    PresentationContext,
    InfographicGenerateRequest,
)
from .layout_service_response import (
    RenderedOutput,
    InfographicMetadata,
    EditableItem,
    EditInfo,
    ErrorResponse,
    InfographicItem,
    InfographicData,
    ResponseData,
    InfographicGenerateResponse,
)

# Original Illustration Models (legacy endpoints)
from .illustration_models import (
    IllustrationRequest,
    IllustrationResponse,
    IllustrationError,
    PyramidGenerationRequest,
    PyramidGenerationResponse,
    FunnelGenerationRequest,
    FunnelGenerationResponse,
    ConcentricCirclesGenerationRequest,
    ConcentricCirclesGenerationResponse,
)

# Director Integration Models (coordination endpoints)
from .coordination_models import (
    ServiceStatus,
    VisualType,
    ItemCountRange,
    SpaceDimensions,
    SpaceRequirements,
    VisualizationSpecialization,
    ContentSignals,
    ServiceCapabilities,
    CapabilitiesResponse,
    SlideContent,
    ContentHints,
    SubZone,
    AvailableSpace,
    CanHandleRequest,
    SpaceUtilization,
    AlternativeApproach,
    CanHandleResponse,
    Preferences,
    RecommendRequest,
    VariantConfig,
    SpaceReqs,
    VisualRecommendation,
    NotRecommended,
    FallbackRecommendation,
    RecommendResponse,
)

__all__ = [
    # Layout Service models
    "InfographicType",
    "GridConstraints",
    "StyleOptions",
    "ContentOptions",
    "PresentationContext",
    "InfographicGenerateRequest",
    "RenderedOutput",
    "InfographicMetadata",
    "EditableItem",
    "EditInfo",
    "ErrorResponse",
    "InfographicItem",
    "InfographicData",
    "ResponseData",
    "InfographicGenerateResponse",
    # Original models
    "IllustrationRequest",
    "IllustrationResponse",
    "IllustrationError",
    "PyramidGenerationRequest",
    "PyramidGenerationResponse",
    "FunnelGenerationRequest",
    "FunnelGenerationResponse",
    "ConcentricCirclesGenerationRequest",
    "ConcentricCirclesGenerationResponse",
    # Director Integration models
    "ServiceStatus",
    "VisualType",
    "ItemCountRange",
    "SpaceDimensions",
    "SpaceRequirements",
    "VisualizationSpecialization",
    "ContentSignals",
    "ServiceCapabilities",
    "CapabilitiesResponse",
    "SlideContent",
    "ContentHints",
    "SubZone",
    "AvailableSpace",
    "CanHandleRequest",
    "SpaceUtilization",
    "AlternativeApproach",
    "CanHandleResponse",
    "Preferences",
    "RecommendRequest",
    "VariantConfig",
    "SpaceReqs",
    "VisualRecommendation",
    "NotRecommended",
    "FallbackRecommendation",
    "RecommendResponse",
]
