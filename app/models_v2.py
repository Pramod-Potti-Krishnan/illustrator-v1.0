"""
Pydantic models v2.0 - Matching Text Service v1.2 Pattern
==========================================================

New models that align with Text Service architecture for seamless
integration with Director Agent and Layout Builder.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class IllustrationGenerationRequest(BaseModel):
    """
    Request model for illustration generation.
    Matches Text Service v1.2 pattern.
    """
    # Session tracking
    presentation_id: str = Field(
        description="Unique presentation identifier for session tracking"
    )

    # Slide identification
    slide_id: str = Field(
        description="Unique slide identifier like 'slide_003'"
    )
    slide_number: int = Field(
        description="Slide number in presentation sequence"
    )

    # Illustration specification
    illustration_type: str = Field(
        description="Type: swot_2x2, process_flow_horizontal, timeline_horizontal, etc."
    )
    variant_id: str = Field(
        default="base",
        description="Variant: base, rounded, condensed, etc."
    )

    # Content source (from Director's slide data)
    topics: List[str] = Field(
        description="Key points to visualize (Director's key_points field)",
        default_factory=list
    )
    narrative: str = Field(
        description="Overall story for this illustration",
        default=""
    )

    # Raw data (alternative to topics/narrative for pre-structured content)
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Pre-structured illustration data (e.g., SWOT quadrants)"
    )

    # Context for generation
    context: Dict[str, Any] = Field(
        description="Presentation context (theme, audience, slide_title)",
        default_factory=dict
    )

    # Layout metadata (from Director's layout selection)
    layout_id: Optional[str] = Field(
        default="L25",
        description="Layout ID (L01, L02, L25) - determines spatial constraints"
    )

    # Generation preferences
    theme: str = Field(
        default="professional",
        description="Color theme: professional, bold, minimal, playful"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres_12345",
                "slide_id": "slide_003",
                "slide_number": 3,
                "illustration_type": "swot_2x2",
                "variant_id": "base",
                "topics": [
                    "Strong brand recognition",
                    "Market leadership",
                    "High operational costs",
                    "Limited retail presence"
                ],
                "narrative": "SWOT analysis for Q4 strategic planning",
                "context": {
                    "theme": "professional",
                    "audience": "executives",
                    "slide_title": "Strategic Position Assessment"
                },
                "layout_id": "L25",
                "theme": "professional"
            }
        }


class IllustrationElement(BaseModel):
    """Individual element within an illustration"""

    element_id: str = Field(
        description="Element identifier (e.g., 'strengths', 'step_1')"
    )
    element_type: str = Field(
        description="Element type (e.g., 'quadrant', 'process_box', 'metric_card')"
    )
    generated_content: Dict[str, Any] = Field(
        description="Generated content for this element"
    )
    character_counts: Optional[Dict[str, int]] = Field(
        default=None,
        description="Character counts per field for validation"
    )


class ValidationResult(BaseModel):
    """Validation results for generated illustration"""

    valid: bool = Field(
        description="Whether illustration meets all constraints"
    )
    violations: List[str] = Field(
        default_factory=list,
        description="List of constraint violations (empty if valid)"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-critical warnings"
    )


class IllustrationResponse(BaseModel):
    """
    Response model for generated illustration.
    Matches Text Service v1.2 pattern.
    """

    success: bool = Field(
        description="Whether generation succeeded"
    )

    # Layout-specific content fields
    content: Dict[str, str] = Field(
        description="Layout-specific content fields (varies by L01/L02/L25)"
    )

    # Individual elements (for debugging/validation)
    elements: List[IllustrationElement] = Field(
        default_factory=list,
        description="Breakdown of individual elements"
    )

    # Generation metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata and diagnostics"
    )

    # Validation results
    validation: ValidationResult = Field(
        description="Constraint validation results"
    )

    # Performance tracking
    generation_time_ms: int = Field(
        description="Time taken to generate in milliseconds"
    )

    class Config:
        json_schema_extra = {
            "example_l25": {
                "success": True,
                "content": {
                    "slide_title": "SWOT Analysis",
                    "subtitle": "Strategic positioning assessment",
                    "rich_content": "<div style='width:100%; height:100%;'>[SWOT grid HTML]</div>"
                },
                "elements": [
                    {
                        "element_id": "strengths",
                        "element_type": "quadrant",
                        "generated_content": {
                            "items": ["Strong brand", "Market leader"]
                        },
                        "character_counts": {"items": 45}
                    }
                ],
                "metadata": {
                    "illustration_type": "swot_2x2",
                    "variant_id": "base",
                    "layout_id": "L25",
                    "diagram_dimensions": {"width": 1800, "height": 720},
                    "theme": "professional",
                    "template_path": "templates/swot_2x2/base_l25.html"
                },
                "validation": {
                    "valid": True,
                    "violations": [],
                    "warnings": []
                },
                "generation_time_ms": 42
            },
            "example_l01": {
                "success": True,
                "content": {
                    "slide_title": "Process Flow",
                    "element_1": "Customer onboarding in 5 steps",
                    "element_4": "<div style='display:flex;'>[Process boxes HTML]</div>",
                    "element_3": "Average completion time: 72 hours"
                },
                "elements": [],
                "metadata": {
                    "illustration_type": "process_flow_horizontal",
                    "layout_id": "L01",
                    "diagram_dimensions": {"width": 1800, "height": 600}
                },
                "validation": {
                    "valid": True,
                    "violations": [],
                    "warnings": []
                },
                "generation_time_ms": 35
            }
        }


# Backward compatibility aliases
class IllustrationRequestV1(BaseModel):
    """Legacy v1.0 request model - maps to v2.0"""
    illustration_type: str
    variant_id: str = "base"
    data: Dict[str, Any]
    theme: str = "professional"
    size: str = "medium"
    output_format: str = "html"


class IllustrationResponseV1(BaseModel):
    """Legacy v1.0 response model"""
    illustration_type: str
    variant_id: str
    format: str
    data: str
    metadata: Dict[str, Any]
    generation_time_ms: int
