"""
Content Analyzer for Director Integration

Analyzes slide content to determine suitability for visualization types.
Used by both /can-handle and /recommend-visual endpoints.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.models.coordination_models import SlideContent, ContentHints

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result of content analysis."""
    best_match: str
    scores: Dict[str, float]
    patterns_detected: List[str]
    negative_signals: List[str]
    topic_count_fit: Dict[str, bool]
    keyword_matches: Dict[str, List[str]]


class ContentAnalyzer:
    """
    Analyzes content for visual type suitability.

    Scoring weights:
    - Keyword matching: 40%
    - Topic count fit: 30%
    - Pattern detection: 20%
    - Negative signal penalty: 10%
    """

    # Keywords strongly associated with each visual type
    VISUAL_KEYWORDS = {
        "pyramid": {
            "strong": [
                "pyramid", "hierarchy", "tier", "foundation", "organizational",
                "top-down", "strategic levels", "maslow",
            ],
            "moderate": [
                "level", "layer", "structure", "base", "peak", "priority",
                "bottom-up", "vertical",
            ],
            "weak": [
                "build", "stack", "strategic", "rank", "order",
            ],
        },
        "funnel": {
            "strong": [
                "funnel", "conversion", "pipeline", "sales funnel", "leads",
                "marketing funnel", "aida",
            ],
            "moderate": [
                "stage", "narrowing", "filtering", "flow", "process",
                "awareness", "interest", "decision", "action",
            ],
            "weak": [
                "steps", "phases", "journey", "qualify", "prospect",
            ],
        },
        "concentric_circles": {
            "strong": [
                "core", "ecosystem", "concentric", "stakeholder", "sphere",
                "influence zone",
            ],
            "moderate": [
                "surrounding", "center", "radiate", "influence", "orbit",
                "layers", "zone", "inner", "outer",
            ],
            "weak": [
                "ring", "circle", "target", "audience", "periphery",
            ],
        },
        "concept_spread": {
            "strong": [
                "pillars", "dimensions", "key concepts", "framework",
                "strategic areas", "capability areas", "six concepts",
            ],
            "moderate": [
                "concept", "initiative", "component", "element",
                "principle", "factor", "aspect", "area",
            ],
            "weak": [
                "key", "main", "primary", "focus", "domain",
            ],
        },
    }

    # Keywords that reduce confidence (better for other services)
    NEGATIVE_KEYWORDS = [
        "chart", "graph", "trend", "percentage", "revenue", "data",
        "vs", "versus", "compare", "comparison", "table", "timeline",
        "over time", "growth", "decline", "quarterly", "monthly", "yearly",
        "statistics", "metrics", "kpi", "dashboard", "bar", "line", "pie",
    ]

    # Ideal item counts for each visual type
    ITEM_COUNT_RANGES = {
        "pyramid": {"min": 3, "max": 6, "optimal": 4},
        "funnel": {"min": 3, "max": 5, "optimal": 4},
        "concentric_circles": {"min": 3, "max": 5, "optimal": 4},
        "concept_spread": {"min": 6, "max": 6, "optimal": 6},
    }

    def analyze(
        self,
        content: SlideContent,
        hints: Optional[ContentHints] = None
    ) -> AnalysisResult:
        """
        Analyze content and return comprehensive analysis result.

        Args:
            content: The slide content to analyze
            hints: Optional hints about the content

        Returns:
            AnalysisResult with scores, patterns, and recommendations
        """
        # Combine title and topics for analysis
        all_text = self._combine_text(content)
        all_text_lower = all_text.lower()

        # Calculate keyword scores and track matches
        keyword_scores, keyword_matches = self._calculate_keyword_scores(all_text_lower)

        # Check topic count fit
        topic_fit = self._check_topic_count_fit(content.topic_count)

        # Detect negative signals
        negative_signals = self._detect_negative_signals(all_text_lower, hints)

        # Detect content patterns
        patterns = self._detect_patterns(all_text_lower, content.topics)

        # Apply pattern bonuses
        final_scores = self._apply_pattern_bonuses(keyword_scores.copy(), patterns)

        # Apply negative signal penalties
        final_scores = self._apply_penalties(final_scores, negative_signals, topic_fit)

        # Apply topic count adjustments
        final_scores = self._apply_topic_count_adjustments(final_scores, topic_fit)

        # Normalize scores to 0-1 range
        final_scores = self._normalize_scores(final_scores)

        # Determine best match
        best_match = max(final_scores, key=final_scores.get) if any(
            v > 0.2 for v in final_scores.values()
        ) else "none"

        logger.debug(
            f"Content analysis complete: best_match={best_match}, "
            f"scores={final_scores}, patterns={patterns}"
        )

        return AnalysisResult(
            best_match=best_match,
            scores=final_scores,
            patterns_detected=patterns,
            negative_signals=negative_signals,
            topic_count_fit=topic_fit,
            keyword_matches=keyword_matches,
        )

    def _combine_text(self, content: SlideContent) -> str:
        """Combine title and topics into single text for analysis."""
        texts = [content.title] + content.topics
        return " ".join(texts)

    def _calculate_keyword_scores(
        self, text: str
    ) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
        """
        Calculate keyword match scores for each visual type.

        Returns:
            Tuple of (scores dict, matched keywords dict)
        """
        scores = {}
        matches = {}

        for visual_type, keywords in self.VISUAL_KEYWORDS.items():
            score = 0.0
            matched = []

            for keyword in keywords["strong"]:
                if keyword in text:
                    score += 0.25
                    matched.append(f"strong:{keyword}")

            for keyword in keywords["moderate"]:
                if keyword in text:
                    score += 0.12
                    matched.append(f"moderate:{keyword}")

            for keyword in keywords["weak"]:
                if keyword in text:
                    score += 0.05
                    matched.append(f"weak:{keyword}")

            scores[visual_type] = min(score, 1.0)  # Cap at 1.0
            matches[visual_type] = matched

        return scores, matches

    def _check_topic_count_fit(self, topic_count: int) -> Dict[str, bool]:
        """Check if topic count fits each visual type's ideal range."""
        fits = {}
        for visual_type, range_info in self.ITEM_COUNT_RANGES.items():
            fits[visual_type] = range_info["min"] <= topic_count <= range_info["max"]
        return fits

    def _detect_negative_signals(
        self, text: str, hints: Optional[ContentHints]
    ) -> List[str]:
        """Detect signals that indicate content is better for other services."""
        signals = []

        # Check for negative keywords
        for keyword in self.NEGATIVE_KEYWORDS:
            if keyword in text:
                signals.append(f"keyword:{keyword}")

        # Check hints
        if hints:
            if hints.has_numbers:
                signals.append("hint:has_numbers")
            if hints.is_comparison:
                signals.append("hint:is_comparison")
            if hints.is_time_based:
                signals.append("hint:is_time_based")

            # Check detected keywords from Director
            for kw in hints.detected_keywords:
                if kw.lower() in self.NEGATIVE_KEYWORDS:
                    signals.append(f"director_keyword:{kw}")

        return signals

    def _detect_patterns(self, text: str, topics: List[str]) -> List[str]:
        """Detect content patterns that suggest specific visual types."""
        patterns = []

        # Hierarchy pattern
        hierarchy_indicators = [
            "top", "bottom", "base", "peak", "foundation", "executive",
            "management", "strategic", "operational", "tactical",
        ]
        if any(indicator in text for indicator in hierarchy_indicators):
            patterns.append("hierarchy")

        # Conversion/stages pattern (AIDA model)
        conversion_indicators = [
            "awareness", "interest", "decision", "action", "consideration",
            "purchase", "loyalty", "advocacy", "qualify", "close",
        ]
        if sum(1 for ind in conversion_indicators if ind in text) >= 2:
            patterns.append("conversion_stages")

        # Layers/core pattern
        layer_indicators = [
            "core", "inner", "outer", "surrounding", "central", "peripheral",
        ]
        if any(indicator in text for indicator in layer_indicators):
            patterns.append("layers")

        # Sequential numbering in topics (e.g., "Step 1", "Phase 1")
        if self._has_sequential_numbering(topics):
            patterns.append("sequential")

        # Narrowing/filtering pattern
        narrowing_indicators = [
            "narrow", "filter", "reduce", "qualify", "select", "refine",
        ]
        if any(indicator in text for indicator in narrowing_indicators):
            patterns.append("narrowing")

        # Concepts/pillars pattern
        concept_indicators = [
            "pillar", "dimension", "concept", "framework", "principle",
            "strategic area", "capability", "initiative",
        ]
        if any(indicator in text for indicator in concept_indicators):
            patterns.append("concepts")

        return patterns

    def _has_sequential_numbering(self, topics: List[str]) -> bool:
        """Check if topics have sequential numbering."""
        number_pattern = re.compile(r"^(\d+|step\s*\d+|phase\s*\d+|stage\s*\d+)", re.I)
        numbered_count = sum(1 for topic in topics if number_pattern.search(topic))
        return numbered_count >= len(topics) * 0.5  # At least half are numbered

    def _apply_pattern_bonuses(
        self, scores: Dict[str, float], patterns: List[str]
    ) -> Dict[str, float]:
        """Apply bonuses based on detected patterns."""
        pattern_bonuses = {
            "hierarchy": {"pyramid": 0.20, "funnel": 0.05, "concentric_circles": 0.05, "concept_spread": 0.0},
            "conversion_stages": {"funnel": 0.25, "pyramid": 0.05, "concentric_circles": 0.0, "concept_spread": 0.0},
            "layers": {"concentric_circles": 0.25, "pyramid": 0.05, "funnel": 0.0, "concept_spread": 0.05},
            "sequential": {"funnel": 0.10, "pyramid": 0.10, "concentric_circles": 0.0, "concept_spread": 0.0},
            "narrowing": {"funnel": 0.15, "pyramid": 0.05, "concentric_circles": 0.0, "concept_spread": 0.0},
            "concepts": {"concept_spread": 0.25, "pyramid": 0.0, "funnel": 0.0, "concentric_circles": 0.0},
        }

        for pattern in patterns:
            if pattern in pattern_bonuses:
                for visual_type, bonus in pattern_bonuses[pattern].items():
                    scores[visual_type] = scores.get(visual_type, 0) + bonus

        return scores

    def _apply_penalties(
        self,
        scores: Dict[str, float],
        negative_signals: List[str],
        topic_fit: Dict[str, bool]
    ) -> Dict[str, float]:
        """Apply penalties for negative signals."""
        # Base penalty for each negative signal
        penalty_per_signal = 0.08
        total_penalty = min(len(negative_signals) * penalty_per_signal, 0.5)

        for visual_type in scores:
            scores[visual_type] = max(0, scores[visual_type] - total_penalty)

        return scores

    def _apply_topic_count_adjustments(
        self, scores: Dict[str, float], topic_fit: Dict[str, bool]
    ) -> Dict[str, float]:
        """Adjust scores based on topic count fit."""
        for visual_type, fits in topic_fit.items():
            if not fits:
                # Reduce score if topic count doesn't fit
                scores[visual_type] *= 0.6

        return scores

    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores to 0-1 range."""
        return {k: round(min(max(v, 0), 1.0), 2) for k, v in scores.items()}

    def get_reason(
        self, visual_type: str, analysis: AnalysisResult, topic_count: int
    ) -> str:
        """Generate a human-readable reason for the score."""
        score = analysis.scores.get(visual_type, 0)
        matches = analysis.keyword_matches.get(visual_type, [])
        fits = analysis.topic_count_fit.get(visual_type, False)

        if score < 0.2:
            if analysis.negative_signals:
                return f"Content appears data-heavy - better suited for charts or text service"
            return f"No strong indicators for {visual_type} visualization"

        reasons = []

        # Keyword matches
        strong_matches = [m.split(":")[1] for m in matches if m.startswith("strong:")]
        if strong_matches:
            reasons.append(f"Keywords detected: {', '.join(strong_matches[:3])}")

        # Pattern matches
        relevant_patterns = {
            "pyramid": ["hierarchy"],
            "funnel": ["conversion_stages", "sequential", "narrowing"],
            "concentric_circles": ["layers"],
            "concept_spread": ["concepts"],
        }
        matched_patterns = [
            p for p in analysis.patterns_detected
            if p in relevant_patterns.get(visual_type, [])
        ]
        if matched_patterns:
            reasons.append(f"Pattern: {matched_patterns[0]}")

        # Topic count
        if fits:
            reasons.append(f"{topic_count} items fits well")
        else:
            range_info = self.ITEM_COUNT_RANGES.get(visual_type, {})
            reasons.append(
                f"{topic_count} items (ideal: {range_info.get('min', 3)}-{range_info.get('max', 6)})"
            )

        return " - ".join(reasons) if reasons else f"Moderate fit for {visual_type}"
