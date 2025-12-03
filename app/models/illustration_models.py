"""
Pydantic models for request/response validation
"""

from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field


class IllustrationRequest(BaseModel):
    """Request model for generating an illustration"""

    illustration_type: str = Field(
        ...,
        description="Type of illustration (e.g., 'swot_2x2', 'process_flow_4step')",
        min_length=3,
        max_length=50
    )

    variant_id: str = Field(
        default="base",
        description="Template variant to use (e.g., 'base', 'rounded', 'minimal')"
    )

    data: Dict[str, Any] = Field(
        ...,
        description="Illustration-specific data (structure depends on illustration type)"
    )

    theme: str = Field(
        default="professional",
        description="Color theme: 'professional', 'bold', 'minimal', or 'playful'"
    )

    size: str = Field(
        default="medium",
        description="Size preset: 'small', 'medium', or 'large'"
    )

    custom_size: Optional[Tuple[int, int]] = Field(
        default=None,
        description="Custom size [width, height] for future use (Phase 2)"
    )

    output_format: str = Field(
        default="html",
        description="Output format: 'html' or 'png'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "illustration_type": "swot_2x2",
                "variant_id": "base",
                "data": {
                    "strengths": ["Strong brand", "Market leader"],
                    "weaknesses": ["High costs"],
                    "opportunities": ["New markets"],
                    "threats": ["Competition"]
                },
                "theme": "professional",
                "size": "medium",
                "output_format": "html"
            }
        }


class IllustrationResponse(BaseModel):
    """Response model for generated illustration"""

    illustration_type: str = Field(
        ...,
        description="Type of illustration that was generated"
    )

    variant_id: str = Field(
        ...,
        description="Template variant that was used"
    )

    format: str = Field(
        ...,
        description="Output format: 'html' or 'png'"
    )

    data: str = Field(
        ...,
        description="HTML string or PNG base64 data URL"
    )

    metadata: Dict[str, Any] = Field(
        ...,
        description="Metadata about the generated illustration"
    )

    generation_time_ms: int = Field(
        ...,
        description="Time taken to generate the illustration in milliseconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "illustration_type": "swot_2x2",
                "variant_id": "base",
                "format": "html",
                "data": "<div class='swot-container'>...</div>",
                "metadata": {
                    "width": 1200,
                    "height": 800,
                    "theme": "professional",
                    "rendering_method": "html_css"
                },
                "generation_time_ms": 145
            }
        }


class IllustrationError(BaseModel):
    """Error response model"""

    error_type: str = Field(
        ...,
        description="Type of error: 'validation_error', 'template_not_found', 'generation_error'"
    )

    message: str = Field(
        ...,
        description="Human-readable error message"
    )

    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )

    suggestions: Optional[list[str]] = Field(
        default=None,
        description="Suggestions for fixing the error"
    )


# ==================== PYRAMID-SPECIFIC MODELS ====================

class PyramidGenerationRequest(BaseModel):
    """Request model for LLM-powered pyramid generation"""

    num_levels: int = Field(
        ...,
        ge=3,
        le=6,
        description="Number of pyramid levels (3-6)"
    )

    topic: str = Field(
        ...,
        min_length=3,
        description="Main topic/theme of the pyramid"
    )

    # Session & Position (optional - aligns with Text Service v1.2)
    presentation_id: Optional[str] = Field(
        default=None,
        description="Presentation identifier for tracking (optional)"
    )

    slide_id: Optional[str] = Field(
        default=None,
        description="Slide identifier (optional)"
    )

    slide_number: Optional[int] = Field(
        default=None,
        description="Slide position in presentation (optional)"
    )

    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for content generation (can include 'previous_slides' array)"
    )

    target_points: Optional[List[str]] = Field(
        default=None,
        description="Key points to include in pyramid levels"
    )

    tone: str = Field(
        default="professional",
        description="Writing tone: professional, casual, technical, etc."
    )

    audience: str = Field(
        default="general",
        description="Target audience for the content"
    )

    theme: str = Field(
        default="professional",
        description="Color theme: professional, bold, minimal, playful"
    )

    size: str = Field(
        default="medium",
        description="Size preset: small, medium, large"
    )

    validate_constraints: bool = Field(
        default=True,
        description="Enforce character limit constraints"
    )

    generate_overview: bool = Field(
        default=False,
        description="Generate overview section (only for 3 and 4 level pyramids)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "num_levels": 4,
                "topic": "Product Development Strategy",
                "context": {
                    "presentation_title": "Q4 Strategic Plan",
                    "slide_purpose": "Show hierarchical development approach",
                    "key_message": "Building from foundation to market leadership",
                    "industry": "Technology"
                },
                "target_points": [
                    "User Research",
                    "Product Design",
                    "Development & Testing",
                    "Market Launch"
                ],
                "tone": "professional",
                "audience": "executives",
                "theme": "professional",
                "validate_constraints": True
            }
        }


class PyramidGenerationResponse(BaseModel):
    """Response model for generated pyramid"""

    success: bool = Field(
        ...,
        description="Whether generation was successful"
    )

    html: str = Field(
        ...,
        description="Complete pyramid HTML with generated content"
    )

    metadata: Dict[str, Any] = Field(
        ...,
        description="Metadata about the generation process"
    )

    generated_content: Dict[str, str] = Field(
        ...,
        description="Generated level labels and descriptions"
    )

    character_counts: Dict[str, Dict[str, int]] = Field(
        ...,
        description="Character counts for all generated fields"
    )

    validation: Dict[str, Any] = Field(
        ...,
        description="Validation results for character constraints"
    )

    generation_time_ms: int = Field(
        ...,
        description="Total generation time in milliseconds"
    )

    # Session & Position (optional - echoed from request)
    presentation_id: Optional[str] = Field(
        default=None,
        description="Presentation identifier (echoed from request)"
    )

    slide_id: Optional[str] = Field(
        default=None,
        description="Slide identifier (echoed from request)"
    )

    slide_number: Optional[int] = Field(
        default=None,
        description="Slide number (echoed from request)"
    )


# ============================================================================
# Funnel Generation Models (NEW - Following Pyramid Pattern)
# ============================================================================

class FunnelGenerationRequest(BaseModel):
    """Request model for LLM-powered funnel generation"""

    num_stages: int = Field(
        ...,
        ge=3,
        le=5,
        description="Number of funnel stages (3-5)"
    )

    topic: str = Field(
        ...,
        min_length=3,
        description="Main topic/theme of the funnel (e.g., 'Sales Pipeline', 'Customer Journey')"
    )

    # Session & Position (optional - aligns with Text Service v1.2)
    presentation_id: Optional[str] = Field(
        default=None,
        description="Presentation identifier for tracking (optional)"
    )

    slide_id: Optional[str] = Field(
        default=None,
        description="Slide identifier (optional)"
    )

    slide_number: Optional[int] = Field(
        default=None,
        description="Slide position in presentation (optional)"
    )

    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for content generation (can include 'previous_slides' array)"
    )

    target_points: Optional[List[str]] = Field(
        default=None,
        description="Stage labels to include in funnel (e.g., ['Awareness', 'Interest', 'Decision'])"
    )

    tone: str = Field(
        default="professional",
        description="Writing tone: professional, casual, technical, etc."
    )

    audience: str = Field(
        default="general",
        description="Target audience for the content"
    )

    theme: str = Field(
        default="professional",
        description="Color theme: professional, bold, minimal, playful"
    )

    size: str = Field(
        default="medium",
        description="Size preset: small, medium, large"
    )

    validate_constraints: bool = Field(
        default=True,
        description="Enforce character limit constraints"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "num_stages": 4,
                "topic": "Sales Conversion Funnel",
                "context": {
                    "presentation_title": "Q4 Sales Strategy",
                    "slide_purpose": "Show our sales pipeline stages",
                    "key_message": "Systematic approach from lead to customer",
                    "industry": "B2B SaaS"
                },
                "target_points": [
                    "Lead Generation",
                    "Qualification",
                    "Proposal",
                    "Closed-Won"
                ],
                "tone": "professional",
                "audience": "sales team",
                "theme": "professional",
                "validate_constraints": True
            }
        }


class FunnelGenerationResponse(BaseModel):
    """Response model for generated funnel"""

    success: bool = Field(
        ...,
        description="Whether generation was successful"
    )

    html: str = Field(
        ...,
        description="Complete funnel HTML with generated content"
    )

    metadata: Dict[str, Any] = Field(
        ...,
        description="Metadata about the generation process"
    )

    generated_content: Dict[str, str] = Field(
        ...,
        description="Generated stage names and bullet points"
    )

    character_counts: Dict[str, Dict[str, int]] = Field(
        ...,
        description="Character counts for all generated fields"
    )

    validation: Dict[str, Any] = Field(
        ...,
        description="Validation results for character constraints"
    )

    generation_time_ms: int = Field(
        ...,
        description="Total generation time in milliseconds"
    )

    # Session & Position (optional - echoed from request)
    presentation_id: Optional[str] = Field(
        default=None,
        description="Presentation identifier (echoed from request)"
    )

    slide_id: Optional[str] = Field(
        default=None,
        description="Slide identifier (echoed from request)"
    )

    slide_number: Optional[int] = Field(
        default=None,
        description="Slide number (echoed from request)"
    )


# ===== Concentric Circles Models =====

class ConcentricCirclesGenerationRequest(BaseModel):
    """Request model for LLM-powered concentric circles generation"""

    num_circles: int = Field(
        ...,
        ge=3,
        le=5,
        description="Number of concentric circles (3-5)"
    )

    topic: str = Field(
        ...,
        min_length=3,
        description="Main topic/theme of the concentric circles (e.g., 'Product Strategy', 'Influence Zones')"
    )

    # Session & Position (optional - aligns with Text Service v1.2)
    presentation_id: Optional[str] = Field(
        default=None,
        description="Presentation identifier for tracking (optional)"
    )

    slide_id: Optional[str] = Field(
        default=None,
        description="Slide identifier (optional)"
    )

    slide_number: Optional[int] = Field(
        default=None,
        description="Slide position in presentation (optional)"
    )

    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for content generation (can include 'previous_slides' array)"
    )

    target_points: Optional[List[str]] = Field(
        default=None,
        description="Circle labels to include (e.g., ['Core', 'Extended', 'Potential'])"
    )

    tone: str = Field(
        default="professional",
        description="Writing tone: professional, casual, technical, etc."
    )

    audience: str = Field(
        default="general",
        description="Target audience for the content"
    )

    theme: str = Field(
        default="professional",
        description="Visual theme (for future expansion)"
    )

    size: str = Field(
        default="medium",
        description="Size variant (for future expansion)"
    )

    validate_constraints: bool = Field(
        default=True,
        description="Whether to validate character constraints"
    )


class ConcentricCirclesGenerationResponse(BaseModel):
    """Response model for LLM-powered concentric circles generation"""

    success: bool = Field(
        ...,
        description="Whether generation was successful"
    )

    html: str = Field(
        ...,
        description="Complete concentric circles HTML with generated content"
    )

    metadata: Dict[str, Any] = Field(
        ...,
        description="Metadata about the generation process"
    )

    generated_content: Dict[str, str] = Field(
        ...,
        description="Generated circle labels and legend bullets"
    )

    character_counts: Dict[str, int] = Field(
        ...,
        description="Character counts for all generated fields"
    )

    validation: Dict[str, Any] = Field(
        ...,
        description="Validation results for character constraints"
    )

    generation_time_ms: int = Field(
        ...,
        description="Total generation time in milliseconds"
    )

    # Session & Position (optional - echoed from request)
    presentation_id: Optional[str] = Field(
        default=None,
        description="Presentation identifier (echoed from request)"
    )

    slide_id: Optional[str] = Field(
        default=None,
        description="Slide identifier (echoed from request)"
    )

    slide_number: Optional[int] = Field(
        default=None,
        description="Slide number (echoed from request)"
    )
