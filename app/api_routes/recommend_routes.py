"""
Recommend-Visual Routes - Phase 3 Director Integration

POST /v1.0/recommend-visual endpoint for Director Agent's Strawman Service
to get specific visual type recommendations.
"""

import logging
from fastapi import APIRouter

from app.models.coordination_models import (
    RecommendRequest,
    RecommendResponse,
)
from app.core.visual_recommender import VisualRecommender

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1.0", tags=["director-integration"])

# Singleton recommender instance
_visual_recommender = VisualRecommender()


@router.post("/recommend-visual", response_model=RecommendResponse)
async def recommend_visual(request: RecommendRequest) -> RecommendResponse:
    """
    Recommend the best visualization type for the given content.

    This endpoint is called after Director determines this service
    can handle the content (via /can-handle). It provides ranked
    recommendations with confidence scores and generation endpoints.

    The response includes:
    - recommended_visuals: Ranked list of suitable visualizations
    - not_recommended: Visual types that don't fit with reasons
    - fallback_recommendation: Alternative service if visuals not ideal

    Args:
        request: RecommendRequest with slide_content, available_space, preferences

    Returns:
        RecommendResponse with ranked recommendations
    """
    logger.info(
        f"Recommend-visual request: title='{request.slide_content.title[:50]}...', "
        f"topic_count={request.slide_content.topic_count}"
    )

    # Get recommendations
    result = _visual_recommender.recommend(
        content=request.slide_content,
        available_space=request.available_space,
        preferences=request.preferences,
    )

    # Log results
    if result.recommended:
        top_rec = result.recommended[0]
        logger.info(
            f"Top recommendation: {top_rec.visual_type} "
            f"(confidence={top_rec.confidence:.2f})"
        )
    else:
        logger.info("No recommendations - suggesting fallback to text-service")

    return RecommendResponse(
        recommended_visuals=result.recommended,
        not_recommended=result.not_recommended if result.not_recommended else None,
        fallback_recommendation=result.fallback,
    )
