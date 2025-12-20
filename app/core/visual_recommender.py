"""
Visual Recommender for Director Integration

Recommends the best visualization type for given content.
Used by /recommend-visual endpoint.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

from app.models.coordination_models import (
    SlideContent,
    AvailableSpace,
    Preferences,
    VisualRecommendation,
    NotRecommended,
    FallbackRecommendation,
    VariantConfig,
    SpaceReqs,
)
from app.core.content_analyzer import ContentAnalyzer, AnalysisResult
from app.core.space_validator import SpaceValidator

logger = logging.getLogger(__name__)


@dataclass
class RecommendationResult:
    """Result of visual type recommendation."""
    recommended: List[VisualRecommendation]
    not_recommended: List[NotRecommended]
    fallback: Optional[FallbackRecommendation]


class VisualRecommender:
    """
    Recommends visual types based on content analysis and space constraints.

    Provides ranked recommendations with confidence scores, variant configs,
    and generation endpoints.
    """

    # Minimum confidence to recommend
    MIN_RECOMMEND_CONFIDENCE = 0.35

    # Generation endpoints for each visual type
    GENERATION_ENDPOINTS = {
        "pyramid": "/v1.0/pyramid/generate",
        "funnel": "/v1.0/funnel/generate",
        "concentric_circles": "/v1.0/concentric_circles/generate",
        "concept_spread": "/concept-spread/generate",
    }

    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        self.space_validator = SpaceValidator()

    def recommend(
        self,
        content: SlideContent,
        available_space: Optional[AvailableSpace] = None,
        preferences: Optional[Preferences] = None
    ) -> RecommendationResult:
        """
        Recommend visual types for the given content.

        Args:
            content: Slide content to analyze
            available_space: Available space from layout (optional)
            preferences: User preferences (optional)

        Returns:
            RecommendationResult with ranked recommendations
        """
        # Analyze content
        analysis = self.content_analyzer.analyze(content, None)

        # Build recommendations
        recommended = []
        not_recommended = []

        for visual_type in ["pyramid", "funnel", "concentric_circles", "concept_spread"]:
            score = analysis.scores.get(visual_type, 0)

            # Validate space
            space_validation = None
            if available_space:
                space_validation = self.space_validator.validate(
                    visual_type,
                    available_space,
                    content.topic_count
                )

            # Build recommendation or not-recommended
            if score >= self.MIN_RECOMMEND_CONFIDENCE:
                rec = self._build_recommendation(
                    visual_type,
                    score,
                    analysis,
                    content,
                    available_space,
                    space_validation,
                    preferences,
                )
                recommended.append(rec)
            else:
                reason = self._get_not_recommended_reason(
                    visual_type, score, analysis, space_validation
                )
                not_recommended.append(
                    NotRecommended(visual_type=visual_type, reason=reason)
                )

        # Sort recommendations by confidence
        recommended.sort(key=lambda x: x.confidence, reverse=True)

        # Build fallback if no good recommendations
        fallback = None
        if not recommended or recommended[0].confidence < 0.5:
            fallback = FallbackRecommendation(
                service="text-service",
                reason="If visual not desired, text-service can render as structured content"
            )

        logger.info(
            f"Recommendations for '{content.title[:30]}...': "
            f"{len(recommended)} recommended, {len(not_recommended)} not recommended"
        )

        return RecommendationResult(
            recommended=recommended,
            not_recommended=not_recommended,
            fallback=fallback,
        )

    def _build_recommendation(
        self,
        visual_type: str,
        score: float,
        analysis: AnalysisResult,
        content: SlideContent,
        available_space: Optional[AvailableSpace],
        space_validation,
        preferences: Optional[Preferences],
    ) -> VisualRecommendation:
        """Build a VisualRecommendation object."""
        # Adjust score based on space validation
        adjusted_score = score
        if space_validation and not space_validation.fits_well:
            adjusted_score *= 0.8

        # Build reason
        reason = self.content_analyzer.get_reason(
            visual_type, analysis, content.topic_count
        )

        # Build variant config
        variant = self._build_variant_config(
            visual_type, content.topic_count, preferences
        )

        # Build space requirements
        space_reqs = None
        if space_validation:
            space_reqs = SpaceReqs(
                width=space_validation.required_width,
                height=space_validation.required_height,
                fits_available=space_validation.fits_well,
            )
        else:
            # Use default requirements
            recommended_space = self.space_validator.get_recommended_space(
                visual_type, content.topic_count
            )
            space_reqs = SpaceReqs(
                width=recommended_space["width"],
                height=recommended_space["height"],
                fits_available=True,  # Assume fits if no constraints
            )

        return VisualRecommendation(
            visual_type=visual_type,
            confidence=round(adjusted_score, 2),
            reason=reason,
            variant=variant,
            space_requirements=space_reqs,
            generation_endpoint=self.GENERATION_ENDPOINTS[visual_type],
        )

    def _build_variant_config(
        self,
        visual_type: str,
        topic_count: int,
        preferences: Optional[Preferences]
    ) -> VariantConfig:
        """Build variant configuration for the visual type."""
        style = preferences.style if preferences else "professional"

        if visual_type == "pyramid":
            return VariantConfig(
                num_levels=topic_count,
                style=style,
            )
        elif visual_type == "funnel":
            return VariantConfig(
                num_stages=topic_count,
                style=style,
            )
        elif visual_type == "concentric_circles":
            return VariantConfig(
                num_circles=topic_count,
                style=style,
            )
        elif visual_type == "concept_spread":
            return VariantConfig(
                num_hexagons=6,  # Always 6 hexagons
                style=style,
            )
        else:
            return VariantConfig(style=style)

    def _get_not_recommended_reason(
        self,
        visual_type: str,
        score: float,
        analysis: AnalysisResult,
        space_validation
    ) -> str:
        """Get reason why a visual type is not recommended."""
        reasons = []

        # Low keyword match
        if score < 0.2:
            reasons.append(f"No strong {visual_type} indicators in content")

        # Negative signals
        if analysis.negative_signals:
            reasons.append("Content appears data-heavy")

        # Topic count doesn't fit
        if not analysis.topic_count_fit.get(visual_type, False):
            ranges = {
                "pyramid": (3, 6),
                "funnel": (3, 5),
                "concentric_circles": (3, 5),
                "concept_spread": (6, 6),
            }
            min_items, max_items = ranges.get(visual_type, (3, 5))
            reasons.append(f"Item count better suited for {min_items}-{max_items} items")

        # Space doesn't fit
        if space_validation and not space_validation.fits_well:
            reasons.append(space_validation.reason)

        return "; ".join(reasons) if reasons else f"Low confidence for {visual_type}"
