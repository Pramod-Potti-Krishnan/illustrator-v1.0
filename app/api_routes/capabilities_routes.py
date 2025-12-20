"""
Capabilities Routes - Phase 1 Director Integration

GET /capabilities endpoint for Director Agent's Strawman Service
to discover what this service can do.
"""

import logging
from fastapi import APIRouter

from app.models.coordination_models import (
    ServiceStatus,
    ItemCountRange,
    SpaceDimensions,
    SpaceRequirements,
    VisualizationSpecialization,
    ContentSignals,
    ServiceCapabilities,
    CapabilitiesResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["director-integration"])

# Service version - update when capabilities change
SERVICE_VERSION = "1.0.2"


def get_capabilities_data() -> CapabilitiesResponse:
    """
    Build the capabilities response.

    This is the single source of truth for what this service can do.
    Director Agent uses this to make intelligent routing decisions.
    """
    return CapabilitiesResponse(
        service="illustrator-service",
        version=SERVICE_VERSION,
        status=ServiceStatus.HEALTHY,
        capabilities=ServiceCapabilities(
            slide_types=["infographic", "visual_metaphor"],
            visualization_types=["pyramid", "funnel", "concentric_circles", "concept_spread"],
            supports_themes=True,
            ai_generated_content=True,
            supported_layouts=["C4-infographic", "V4-infographic-text", "L25", "L01", "L02"],
        ),
        content_signals=ContentSignals(
            handles_well=[
                "hierarchies",
                "levels",
                "stages",
                "layers",
                "visual_metaphors",
                "progressions",
                "funnels",
                "concentric_concepts",
                "organizational_structures",
                "tiered_systems",
            ],
            handles_poorly=[
                "data_heavy_content",
                "many_items",
                "tabular_data",
                "time_series",
                "numerical_comparisons",
                "charts",
                "graphs",
                "detailed_statistics",
            ],
            keywords=[
                "pyramid", "funnel", "hierarchy", "levels", "stages",
                "core", "layers", "ecosystem", "tier", "foundation",
                "conversion", "pipeline", "narrowing", "concentric",
                "stakeholder", "organizational", "priority", "influence",
                "concept", "pillars", "key areas", "dimensions", "hexagon",
            ],
        ),
        specializations={
            "pyramid": VisualizationSpecialization(
                description="Hierarchical structure from foundation to peak",
                best_for=[
                    "hierarchy",
                    "levels",
                    "foundation to peak",
                    "priority",
                    "organizational tiers",
                    "strategic layers",
                    "needs hierarchy (Maslow)",
                ],
                keywords=[
                    "pyramid", "levels", "hierarchy", "tier", "foundation",
                    "top-down", "layers", "base", "peak", "strategic",
                    "organizational", "priority", "structure",
                ],
                ideal_item_count=ItemCountRange(min=3, max=6, optimal=4),
                space_requirements=SpaceRequirements(
                    min=SpaceDimensions(width=800, height=600),
                    optimal=SpaceDimensions(width=1200, height=700),
                ),
            ),
            "funnel": VisualizationSpecialization(
                description="Narrowing stages from wide to narrow",
                best_for=[
                    "conversion",
                    "stages",
                    "narrowing process",
                    "pipeline",
                    "sales funnel",
                    "marketing funnel",
                    "customer journey",
                ],
                keywords=[
                    "funnel", "conversion", "pipeline", "stages", "leads",
                    "narrowing", "filtering", "awareness", "interest",
                    "decision", "action", "AIDA", "sales", "marketing",
                ],
                ideal_item_count=ItemCountRange(min=3, max=5, optimal=4),
                space_requirements=SpaceRequirements(
                    min=SpaceDimensions(width=700, height=600),
                    optimal=SpaceDimensions(width=1000, height=700),
                ),
            ),
            "concentric_circles": VisualizationSpecialization(
                description="Layers radiating from core outward",
                best_for=[
                    "core to periphery",
                    "layers",
                    "ecosystem",
                    "influence zones",
                    "stakeholder mapping",
                    "spheres of influence",
                    "target audiences",
                ],
                keywords=[
                    "core", "layers", "surrounding", "ecosystem", "center",
                    "concentric", "radiate", "inner", "outer", "ring",
                    "stakeholder", "influence", "sphere", "zone", "orbit",
                ],
                ideal_item_count=ItemCountRange(min=3, max=5, optimal=4),
                space_requirements=SpaceRequirements(
                    min=SpaceDimensions(width=700, height=700),
                    optimal=SpaceDimensions(width=900, height=700),
                ),
            ),
            "concept_spread": VisualizationSpecialization(
                description="Six hexagon grid showing key concepts with supporting details",
                best_for=[
                    "key concepts",
                    "pillars",
                    "dimensions",
                    "strategic areas",
                    "framework components",
                    "initiative categories",
                    "capability areas",
                ],
                keywords=[
                    "concept", "pillars", "dimensions", "key areas", "framework",
                    "strategic", "initiative", "capability", "component",
                    "element", "factor", "aspect", "principle",
                ],
                ideal_item_count=ItemCountRange(min=6, max=6, optimal=6),
                space_requirements=SpaceRequirements(
                    min=SpaceDimensions(width=1000, height=700),
                    optimal=SpaceDimensions(width=1800, height=840),
                ),
            ),
        },
        endpoints={
            "capabilities": "GET /capabilities",
            "pyramid": "POST /v1.0/pyramid/generate",
            "funnel": "POST /v1.0/funnel/generate",
            "concentric": "POST /v1.0/concentric_circles/generate",
            "concept_spread": "POST /concept-spread/generate",
            "can_handle": "POST /v1.0/can-handle",
            "recommend_visual": "POST /v1.0/recommend-visual",
            "layout_service_generate": "POST /api/ai/illustrator/generate",
        },
    )


@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities() -> CapabilitiesResponse:
    """
    Return service capabilities for Director Agent coordination.

    This endpoint enables the Strawman Service to understand what
    visualizations this service can generate and when to route
    content here vs. other services.

    Returns:
        CapabilitiesResponse with:
        - service: Service identifier
        - version: Semantic version
        - status: Operational status (healthy/degraded)
        - capabilities: What we can do
        - content_signals: What content types we handle well/poorly
        - specializations: Details for each visual type
        - endpoints: Available API endpoints
    """
    logger.info("Capabilities requested by Director Agent")
    return get_capabilities_data()


# Export capabilities data for use by other modules
CAPABILITIES = get_capabilities_data()
