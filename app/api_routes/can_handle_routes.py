"""
Can-Handle Routes - Phase 2 Director Integration

POST /v1.0/can-handle endpoint for Director Agent's Strawman Service
to determine if this service can handle specific content.
"""

import logging
from fastapi import APIRouter

from app.models.coordination_models import (
    CanHandleRequest,
    CanHandleResponse,
    SpaceUtilization,
    AlternativeApproach,
    ContentHints,
)
from app.core.content_analyzer import ContentAnalyzer
from app.core.space_validator import SpaceValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1.0", tags=["director-integration"])

# Singleton instances
_content_analyzer = ContentAnalyzer()
_space_validator = SpaceValidator()

# Minimum confidence threshold to say "can handle"
MIN_CONFIDENCE_THRESHOLD = 0.35


@router.post("/can-handle", response_model=CanHandleResponse)
async def can_handle(request: CanHandleRequest) -> CanHandleResponse:
    """
    Determine if this service can handle the given content.

    This endpoint enables Director's Strawman Service to query multiple
    content services in parallel and pick the one with highest confidence.

    Confidence scoring:
    - 0.90+ : Excellent fit, high confidence
    - 0.70-0.89: Good fit, can handle well
    - 0.50-0.69: Acceptable, but other services might be better
    - 0.35-0.49: Poor fit, likely prefer other service
    - < 0.35: Cannot handle effectively

    Args:
        request: CanHandleRequest with slide_content, content_hints, available_space

    Returns:
        CanHandleResponse with can_handle, confidence, reason, and alternatives
    """
    logger.info(
        f"Can-handle request: title='{request.slide_content.title[:50]}...', "
        f"topic_count={request.slide_content.topic_count}"
    )

    # Analyze content
    hints = request.content_hints or ContentHints()
    analysis = _content_analyzer.analyze(request.slide_content, hints)

    # Get best visual type and confidence
    best_type = analysis.best_match
    best_confidence = analysis.scores.get(best_type, 0) if best_type != "none" else 0

    # Validate space if provided
    space_validation = None
    if request.available_space and best_type != "none":
        space_validation = _space_validator.validate(
            best_type,
            request.available_space,
            request.slide_content.topic_count
        )

        # Reduce confidence if space doesn't fit well
        if not space_validation.fits_well:
            best_confidence *= 0.7

    # Determine if we can handle
    can_handle = best_confidence >= MIN_CONFIDENCE_THRESHOLD and best_type != "none"

    # Build reason
    reason = _build_reason(analysis, best_type, best_confidence, space_validation)

    # Build alternative approaches
    alternatives = _build_alternatives(analysis, best_type)

    # Build space utilization
    space_util = None
    if space_validation:
        space_util = SpaceUtilization(
            fits_well=space_validation.fits_well,
            estimated_fill_percent=space_validation.estimated_fill_percent,
        )

    logger.info(
        f"Can-handle result: can_handle={can_handle}, confidence={best_confidence:.2f}, "
        f"suggested={best_type}"
    )

    return CanHandleResponse(
        can_handle=can_handle,
        confidence=round(best_confidence, 2),
        reason=reason,
        suggested_approach=best_type if can_handle else None,
        space_utilization=space_util,
        alternative_approaches=alternatives if alternatives else None,
    )


def _build_reason(
    analysis,
    best_type: str,
    confidence: float,
    space_validation
) -> str:
    """Build a human-readable reason for the response."""
    if best_type == "none" or confidence < MIN_CONFIDENCE_THRESHOLD:
        # Explain why we can't handle
        if analysis.negative_signals:
            signal_types = [s.split(":")[0] for s in analysis.negative_signals[:3]]
            if "hint" in signal_types or "keyword" in signal_types:
                return (
                    "Content appears data-heavy or comparison-focused - "
                    "better suited for charts or text service"
                )
        return "No strong visual metaphor detected - content may be better as text or chart"

    # Build positive reason
    parts = []

    # Keyword matches
    matches = analysis.keyword_matches.get(best_type, [])
    strong_matches = [m.split(":")[1] for m in matches if m.startswith("strong:")]
    if strong_matches:
        parts.append(f"Keywords: {', '.join(strong_matches[:2])}")

    # Pattern matches
    relevant_patterns = {
        "pyramid": ["hierarchy"],
        "funnel": ["conversion_stages", "narrowing", "sequential"],
        "concentric_circles": ["layers"],
    }
    for pattern in analysis.patterns_detected:
        if pattern in relevant_patterns.get(best_type, []):
            parts.append(f"Pattern: {pattern.replace('_', ' ')}")
            break

    # Topic count
    topic_fit = analysis.topic_count_fit.get(best_type, False)
    if topic_fit:
        parts.append("Item count fits well")

    # Space validation
    if space_validation:
        if space_validation.fits_well:
            parts.append(f"Space: {space_validation.estimated_fill_percent}% utilization")
        else:
            parts.append(f"Note: {space_validation.reason}")

    return " - ".join(parts) if parts else f"Suitable for {best_type} visualization"


def _build_alternatives(analysis, best_type: str) -> list:
    """Build list of alternative visual approaches."""
    alternatives = []

    for visual_type, score in sorted(
        analysis.scores.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        # Skip best type and low scores
        if visual_type == best_type or score < 0.2:
            continue

        reason = _content_analyzer.get_reason(
            visual_type, analysis, 4  # Default topic count
        )

        alternatives.append(
            AlternativeApproach(
                visual_type=visual_type,
                confidence=round(score, 2),
                reason=reason,
            )
        )

    return alternatives[:2]  # Return top 2 alternatives
