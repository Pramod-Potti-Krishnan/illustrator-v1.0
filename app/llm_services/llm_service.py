"""
LLM Service for Gemini 2.5 Flash Integration

Provides async Gemini text generation for pyramid content creation.
Uses Vertex AI with Application Default Credentials (ADC).
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationConfig

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for generating content using Gemini models via Vertex AI"""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize Gemini service with Vertex AI.

        Args:
            project_id: GCP project ID (reads from GCP_PROJECT_ID env if not provided)
            location: GCP region for Vertex AI (reads from GEMINI_LOCATION env if not provided)
            model_name: Gemini model to use (reads from LLM_PYRAMID env if not provided)
        """
        # Read from environment variables
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location or os.getenv("GEMINI_LOCATION")
        self.model_name = model_name or os.getenv("LLM_PYRAMID")

        # Validate required configuration
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID environment variable must be set")

        if not self.location:
            raise ValueError("GEMINI_LOCATION environment variable must be set")

        if not self.model_name:
            raise ValueError("LLM_PYRAMID environment variable must be set")

        # Initialize Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)

        # Create generative model
        self.model = GenerativeModel(self.model_name)

        logger.info(
            f"Initialized GeminiService: "
            f"project={self.project_id}, "
            f"location={self.location}, "
            f"model={self.model_name}"
        )

    async def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate content using Gemini 2.5 Flash.

        Args:
            prompt: Text prompt for generation
            temperature: Creativity (0.0-1.0)
            max_tokens: Maximum tokens to generate
            response_format: Expected format ('json' or 'text')

        Returns:
            Dict with generated content or error
        """
        try:
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json" if response_format == "json" else "text/plain"
            )

            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Extract text
            generated_text = response.text.strip()

            # Parse JSON if requested
            if response_format == "json":
                try:
                    content = json.loads(generated_text)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Raw response: {generated_text}")
                    return {
                        "success": False,
                        "error": "Invalid JSON response from LLM",
                        "raw_response": generated_text
                    }
            else:
                content = {"text": generated_text}

            # Get usage metadata if available
            usage_metadata = {}
            if hasattr(response, 'usage_metadata'):
                usage_metadata = {
                    "prompt_token_count": response.usage_metadata.prompt_token_count,
                    "candidates_token_count": response.usage_metadata.candidates_token_count,
                    "total_token_count": response.usage_metadata.total_token_count
                }

            return {
                "success": True,
                "content": content,
                "usage_metadata": usage_metadata,
                "model": self.model_name
            }

        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_pyramid_content(
        self,
        topic: str,
        num_levels: int,
        context: Dict[str, Any],
        constraints: Dict[str, Dict[str, list]],
        target_points: Optional[list] = None,
        tone: str = "professional",
        audience: str = "general",
        generate_overview: bool = False
    ) -> Dict[str, Any]:
        """
        Generate pyramid level content with character constraints.

        Args:
            topic: Main topic/theme of pyramid
            num_levels: Number of pyramid levels (3-6)
            context: Additional context (presentation info, industry, etc.)
            constraints: Character limits per level
            target_points: Optional key points to include
            tone: Writing tone
            audience: Target audience
            generate_overview: Whether to generate overview section (3 & 4 levels only)

        Returns:
            Dict with generated level content
        """
        prompt = self._build_pyramid_prompt(
            topic=topic,
            num_levels=num_levels,
            context=context,
            constraints=constraints,
            target_points=target_points,
            tone=tone,
            audience=audience,
            generate_overview=generate_overview
        )

        result = await self.generate_content(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048,
            response_format="json"
        )

        return result

    def _build_pyramid_prompt(
        self,
        topic: str,
        num_levels: int,
        context: Dict[str, Any],
        constraints: Dict[str, Dict[str, list]],
        target_points: Optional[list],
        tone: str,
        audience: str,
        generate_overview: bool = False
    ) -> str:
        """Build comprehensive prompt for pyramid generation"""

        # Build context string
        context_str = ""
        if context.get("presentation_title"):
            context_str += f"\nPresentation: {context['presentation_title']}"
        if context.get("slide_purpose"):
            context_str += f"\nPurpose: {context['slide_purpose']}"
        if context.get("key_message"):
            context_str += f"\nKey Message: {context['key_message']}"
        if context.get("industry"):
            context_str += f"\nIndustry: {context['industry']}"

        # Build target points string
        points_str = ""
        if target_points:
            points_str = "\n\nKey Points to Include:\n" + "\n".join(
                f"- {point}" for point in target_points
            )

        # Build previous slides context (NEW - aligns with Text Service v1.2)
        previous_context_str = ""
        if context.get("previous_slides"):
            previous_slides = context["previous_slides"]
            if previous_slides:  # Check if list is not empty
                previous_context_str = "\n\nPrevious slides in this presentation:"
                for slide in previous_slides:
                    slide_num = slide.get("slide_number", "?")
                    slide_title = slide.get("slide_title", slide.get("title", "Untitled"))
                    slide_summary = slide.get("summary", "")
                    previous_context_str += f"\n- Slide {slide_num}: {slide_title}"
                    if slide_summary:
                        previous_context_str += f"\n  {slide_summary}"
                previous_context_str += "\n\nIMPORTANT: Ensure this pyramid builds upon and complements the narrative established in previous slides."

        # Build constraints string
        constraints_str = "\n\nCharacter Constraints (MUST FOLLOW EXACTLY):"

        # Top level (special constraints - 1-2 words with <br>)
        top_level_key = f"level_{num_levels}"
        second_level_key = f"level_{num_levels - 1}"

        if top_level_key in constraints:
            label_min, label_max = constraints[top_level_key]["label"]
            desc_min, desc_max = constraints[top_level_key]["description"]
            constraints_str += f"\n- Level {num_levels} label (TOP): 1-2 words ONLY, each word 5-9 chars"
            constraints_str += f"\n  If 2 words, format as: Word1<br>Word2 (e.g., 'Vision<br>Driven')"
            constraints_str += f"\n  Total length (excluding <br>): {label_min}-{label_max} characters"
            constraints_str += f"\n- Level {num_levels} description: {desc_min}-{desc_max} characters (use <strong> tags to emphasize 1-2 key words)"

        # Second from top (special - max 20 chars)
        if second_level_key in constraints:
            label_min, label_max = constraints[second_level_key]["label"]
            desc_min, desc_max = constraints[second_level_key]["description"]
            constraints_str += f"\n- Level {num_levels - 1} label (SECOND FROM TOP): MAX 20 characters total"
            constraints_str += f"\n- Level {num_levels - 1} description: {desc_min}-{desc_max} characters (use <strong> tags to emphasize 1-2 key words)"

        # Other levels (standard constraints)
        for level_num in range(num_levels - 2, 0, -1):
            level_key = f"level_{level_num}"
            if level_key in constraints:
                label_min, label_max = constraints[level_key]["label"]
                desc_min, desc_max = constraints[level_key]["description"]
                constraints_str += f"\n- Level {level_num} label: {label_min}-{label_max} characters"
                constraints_str += f"\n- Level {level_num} description: {desc_min}-{desc_max} characters (use <strong> tags to emphasize 1-2 key words)"

        # Overview constraints (if requested)
        if generate_overview and "overview" in constraints:
            text_min, text_max = constraints["overview"]["text"]
            constraints_str += f"\n- Overview text: {text_min}-{text_max} characters"

        # Build JSON structure
        json_fields = {}
        for level_num in range(num_levels, 0, -1):
            json_fields[f"level_{level_num}_label"] = f"Level {level_num} label text"
            json_fields[f"level_{level_num}_description"] = f"Level {level_num} description with <strong>key words</strong>"

        # Add overview fields if requested
        if generate_overview:
            json_fields["overview_text"] = "Overview section detailed text"

        json_example = json.dumps(json_fields, indent=2)

        prompt = f"""Generate a {num_levels}-level hierarchical pyramid for the topic: "{topic}"
{context_str}
{points_str}
{previous_context_str}

Instructions:
1. Create a hierarchical progression from Level 1 (base/foundation) to Level {num_levels} (peak/goal)
2. Level 1 should represent the foundation or basic elements
3. Each higher level should build upon the previous level
4. Level {num_levels} should represent the ultimate goal or peak achievement
5. Labels should be concise, impactful phrases (like section headers):
   - Level {num_levels} (TOP): MUST be 1-2 words ONLY, each word 5-9 chars
     * If 2 words, separate with <br> tag (e.g., "Vision<br>Driven")
     * If 1 word, no <br> needed (e.g., "Excellence")
   - Level {num_levels - 1} (SECOND FROM TOP): MAX 20 characters total
   - Other levels: Keep concise, 12-20 characters
6. Descriptions should provide clear, meaningful explanations
   - Use <strong> tags to emphasize 1-2 key words per description
   - Example: "Develop the <strong>product vision</strong> and create a detailed blueprint"
7. Maintain consistency and logical flow between levels
8. Use {tone} tone appropriate for {audience} audience
{"9. Generate overview section with detailed explanatory text (no heading needed)" if generate_overview else ""}

{constraints_str}

Return ONLY valid JSON in this exact format:
{json_example}

CRITICAL:
- Every field must meet its character constraints exactly
- Count characters carefully (spaces count!)
- Top level label MUST be 2 words maximum (e.g., "Market Leadership" NOT "Achieve Market Leadership")
- ALL descriptions MUST include <strong> tags around 1-2 key words
- HTML tags do NOT count toward character limits"""

        return prompt

    async def generate_funnel_content(
        self,
        topic: str,
        num_stages: int,
        context: Dict[str, Any],
        constraints: Dict[str, Dict[str, list]],
        target_points: Optional[list] = None,
        tone: str = "professional",
        audience: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate funnel stage content with character constraints.

        Args:
            topic: Main topic/theme of funnel (e.g., "Sales Pipeline", "Customer Journey")
            num_stages: Number of funnel stages (3-5)
            context: Additional context (presentation info, industry, etc.)
            constraints: Character limits per stage
            target_points: Optional stage labels to include
            tone: Writing tone
            audience: Target audience

        Returns:
            Dict with generated stage content
        """
        prompt = self._build_funnel_prompt(
            topic=topic,
            num_stages=num_stages,
            context=context,
            constraints=constraints,
            target_points=target_points,
            tone=tone,
            audience=audience
        )

        result = await self.generate_content(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048,
            response_format="json"
        )

        return result

    def _build_funnel_prompt(
        self,
        topic: str,
        num_stages: int,
        context: Dict[str, Any],
        constraints: Dict[str, Dict[str, list]],
        target_points: Optional[list],
        tone: str,
        audience: str
    ) -> str:
        """Build comprehensive prompt for funnel generation"""

        # Build context string
        context_str = ""
        if context.get("presentation_title"):
            context_str += f"\nPresentation: {context['presentation_title']}"
        if context.get("slide_purpose"):
            context_str += f"\nPurpose: {context['slide_purpose']}"
        if context.get("key_message"):
            context_str += f"\nKey Message: {context['key_message']}"
        if context.get("industry"):
            context_str += f"\nIndustry: {context['industry']}"

        # Build target points string
        points_str = ""
        if target_points:
            points_str = "\n\nStage Labels to Include:\n" + "\n".join(
                f"- Stage {i+1}: {point}" for i, point in enumerate(target_points)
            )

        # Build previous slides context (aligns with Text Service v1.2)
        previous_context_str = ""
        if context.get("previous_slides"):
            previous_slides = context["previous_slides"]
            if previous_slides:
                previous_context_str = "\n\nPrevious slides in this presentation:"
                for slide in previous_slides:
                    slide_num = slide.get("slide_number", "?")
                    slide_title = slide.get("slide_title", slide.get("title", "Untitled"))
                    slide_summary = slide.get("summary", "")
                    previous_context_str += f"\n- Slide {slide_num}: {slide_title}"
                    if slide_summary:
                        previous_context_str += f"\n  {slide_summary}"
                previous_context_str += "\n\nIMPORTANT: Ensure this funnel builds upon and complements the narrative established in previous slides."

        # Build constraints string
        constraints_str = "\n\nCharacter Constraints (MUST FOLLOW EXACTLY):"

        for stage_num in range(1, num_stages + 1):
            stage_key = f"stage_{stage_num}"
            if stage_key in constraints:
                name_min, name_max = constraints[stage_key]["name"]
                bullet_1_min, bullet_1_max = constraints[stage_key]["bullet_1"]
                bullet_2_min, bullet_2_max = constraints[stage_key]["bullet_2"]
                bullet_3_min, bullet_3_max = constraints[stage_key]["bullet_3"]

                constraints_str += f"\n\nStage {stage_num}:"
                constraints_str += f"\n  - Name: {name_min}-{name_max} characters"
                constraints_str += f"\n  - Bullet 1: {bullet_1_min}-{bullet_1_max} characters"
                constraints_str += f"\n  - Bullet 2: {bullet_2_min}-{bullet_2_max} characters"
                constraints_str += f"\n  - Bullet 3: {bullet_3_min}-{bullet_3_max} characters"

        # Build JSON structure
        json_fields = {}
        for stage_num in range(1, num_stages + 1):
            json_fields[f"stage_{stage_num}_name"] = f"Stage {stage_num} name"
            json_fields[f"stage_{stage_num}_bullet_1"] = f"First key action or characteristic"
            json_fields[f"stage_{stage_num}_bullet_2"] = f"Second key action or characteristic"
            json_fields[f"stage_{stage_num}_bullet_3"] = f"Third key action or characteristic"

        json_example = json.dumps(json_fields, indent=2)

        prompt = f"""Generate a {num_stages}-stage funnel diagram for the topic: "{topic}"
{context_str}
{points_str}
{previous_context_str}

Instructions:
1. Create a funnel flow representing progression through {num_stages} stages
2. Stage 1 (TOP/WIDEST) should represent the broadest or initial stage (e.g., Awareness, Leads)
3. Each subsequent stage should narrow/focus (e.g., Consideration → Decision → Purchase)
4. Stage {num_stages} (BOTTOM/NARROWEST) should represent the final outcome or conversion
5. Stage names should be concise, clear labels (8-25 characters)
   - Examples: "Awareness", "Lead Generation", "Qualification", "Conversion", "Retention"
6. Each stage should have exactly 3 bullet points that:
   - Describe key actions, characteristics, or metrics for that stage
   - Are concise but informative (30-60 characters each)
   - Use <strong> tags to emphasize 1-2 key words per bullet
   - Example: "Generate <strong>qualified leads</strong> through campaigns"
7. Maintain logical flow from top to bottom of the funnel
8. Use {tone} tone appropriate for {audience} audience

Common Funnel Types for Inspiration:
- Sales Funnel: Awareness → Interest → Decision → Action
- Marketing Funnel: Reach → Engage → Convert → Retain
- Customer Journey: Discovery → Evaluation → Purchase → Loyalty
- Conversion Funnel: Visit → Browse → Cart → Checkout

{constraints_str}

Return ONLY valid JSON in this exact format:
{json_example}

CRITICAL:
- Every field must meet its character constraints exactly
- Count characters carefully (spaces count!)
- ALL bullets MUST include <strong> tags around 1-2 key words
- HTML tags do NOT count toward character limits
- Stage names should be simple labels, not full sentences"""

        return prompt

    async def generate_concentric_circles_content(
        self,
        topic: str,
        num_circles: int,
        context: Dict[str, Any],
        constraints: Dict[str, Dict[str, list]],
        target_points: Optional[list] = None,
        tone: str = "professional",
        audience: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate concentric circles content with character constraints.

        Args:
            topic: Main topic/theme of concentric circles
            num_circles: Number of concentric circles (3-5)
            context: Additional context (presentation info, industry, etc.)
            constraints: Character limits per circle and legend
            target_points: Optional key points to include
            tone: Writing tone
            audience: Target audience

        Returns:
            Dict with generated circle labels and legend bullets
        """
        prompt = self._build_concentric_circles_prompt(
            topic=topic,
            num_circles=num_circles,
            context=context,
            constraints=constraints,
            target_points=target_points,
            tone=tone,
            audience=audience
        )

        result = await self.generate_content(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048,
            response_format="json"
        )

        return result

    def _build_concentric_circles_prompt(
        self,
        topic: str,
        num_circles: int,
        context: Dict[str, Any],
        constraints: Dict[str, Dict[str, list]],
        target_points: Optional[list],
        tone: str,
        audience: str
    ) -> str:
        """Build comprehensive prompt for concentric circles generation"""

        # Build context string
        context_str = ""
        if context:
            if "presentation_title" in context:
                context_str += f"\nPresentation: {context['presentation_title']}"
            if "slide_title" in context:
                context_str += f"\nSlide Title: {context['slide_title']}"
            if "industry" in context:
                context_str += f"\nIndustry: {context['industry']}"
            if "previous_slides" in context and context["previous_slides"]:
                context_str += "\n\nPrevious Slide Content (for narrative continuity):\n"
                for i, slide in enumerate(context["previous_slides"][-3:], 1):
                    context_str += f"Slide {i}: {slide.get('title', 'Untitled')}\n"
                    if "key_points" in slide:
                        context_str += f"  Key points: {', '.join(slide['key_points'][:3])}\n"

        # Build target points string
        target_points_str = ""
        if target_points:
            target_points_str = "\nKey Points to Include:\n" + "\n".join(f"- {point}" for point in target_points)

        # Build constraints string with examples
        bullets_per_legend = {3: 5, 4: 4, 5: 3}
        num_bullets = bullets_per_legend.get(num_circles, 3)

        constraints_str = "CHARACTER CONSTRAINTS (CRITICAL - MUST FOLLOW EXACTLY):\n\n"
        for i in range(1, num_circles + 1):
            circle_key = f"circle_{i}_label"
            if circle_key in constraints:
                min_c, max_c = constraints[circle_key]["min_chars"], constraints[circle_key]["max_chars"]
                constraints_str += f"Circle {i} Label: {min_c}-{max_c} characters\n"

        constraints_str += "\n"
        for i in range(1, num_circles + 1):
            constraints_str += f"Legend {i} Bullets ({num_bullets} bullets): 30-45 characters each\n"

        # Build JSON example
        json_example = "{\n"
        for i in range(1, num_circles + 1):
            circle_key = f"circle_{i}_label"
            json_example += f'  "{circle_key}": "Label Text",\n'

        for legend_num in range(1, num_circles + 1):
            for bullet_num in range(1, num_bullets + 1):
                bullet_key = f"legend_{legend_num}_bullet_{bullet_num}"
                json_example += f'  "{bullet_key}": "Bullet point text here",\n'

        json_example = json_example.rstrip(',\n') + "\n}"

        prompt = f"""You are an expert presentation content creator specializing in concentric circles diagrams.

TASK: Generate content for a {num_circles}-circle concentric circles diagram about: {topic}

AUDIENCE: {audience}
TONE: {tone}
{context_str}
{target_points_str}

CONCENTRIC CIRCLES STRUCTURE:
- Circle 1 (Core/Center): The innermost circle - fundamental concept or core value
- Circle 2-{num_circles-1} (Middle Layers): Progressive layers building outward
- Circle {num_circles} (Outermost): The broadest or most encompassing concept

Each circle has:
1. A SHORT LABEL (displayed on the circle itself)
2. A LEGEND BOX with {num_bullets} bullet points (detailed explanations)

CONTENT REQUIREMENTS:

1. Circle Labels:
   - VERY CONCISE (max {constraints[f'circle_1_label']['max_chars']} chars for inner circles)
   - Can use <br> tag for 2-line labels in core circle ONLY if needed
   - Should be simple, impactful phrases
   - Progress from specific (core) to general (outer)

2. Legend Bullets:
   - Each legend has exactly {num_bullets} bullets
   - 30-45 characters per bullet
   - Provide detailed explanations and examples
   - Must be substantive and informative
   - NO generic fluff or filler

3. Content Flow:
   - Core circle: Most fundamental/essential concept
   - Middle circles: Building blocks and supporting elements
   - Outer circle: Broader context and applications

{constraints_str}

Common Concentric Circles Examples for Inspiration:
- Product Levels: Core → Generic → Expected → Augmented → Potential
- Business Strategy: Mission → Execution → Growth → Expansion
- Influence Circles: Control → Influence → Concern
- Learning Zones: Comfort → Stretch → Panic

Return ONLY valid JSON in this exact format:
{json_example}

CRITICAL:
- Every field must meet its character constraints exactly
- Count characters carefully (spaces count!)
- Circle labels should be SHORT and impactful
- Legend bullets should be detailed and substantive
- HTML tags (<br>) do NOT count toward character limits
- Maintain logical progression from core to outer circles"""

        return prompt


# Global service instances
_gemini_service: Optional[GeminiService] = None
_funnel_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create the global Gemini service instance for pyramid"""
    global _gemini_service

    if _gemini_service is None:
        _gemini_service = GeminiService()

    return _gemini_service


def get_funnel_service() -> GeminiService:
    """Get or create the Gemini service instance specifically for funnel generation"""
    global _funnel_service

    if _funnel_service is None:
        # Create service with LLM_FUNNEL model
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GEMINI_LOCATION")
        model_name = os.getenv("LLM_FUNNEL", "gemini-2.0-flash-exp")
        _funnel_service = GeminiService(
            project_id=project_id,
            location=location,
            model_name=model_name
        )

    return _funnel_service


# Concentric Circles service
_concentric_circles_service: Optional[GeminiService] = None


def get_concentric_circles_service() -> GeminiService:
    """Get or create the Gemini service instance specifically for concentric circles generation"""
    global _concentric_circles_service

    if _concentric_circles_service is None:
        # Create service with LLM_CONCENTRIC_CIRCLES model
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GEMINI_LOCATION")
        model_name = os.getenv("LLM_CONCENTRIC_CIRCLES", "gemini-2.0-flash-exp")
        _concentric_circles_service = GeminiService(
            project_id=project_id,
            location=location,
            model_name=model_name
        )

    return _concentric_circles_service
