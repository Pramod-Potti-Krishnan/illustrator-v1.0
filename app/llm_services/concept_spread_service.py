"""
Concept Spread LLM Service

Generates hexagon labels, icons, and description bullets for concept-spread illustrations.
Uses Vertex AI Gemini to create structured content with Unicode icons.

Supports two authentication methods:
1. GCP_CREDENTIALS_JSON environment variable (JSON string pasted directly)
2. GOOGLE_APPLICATION_CREDENTIALS environment variable (file path)
"""

import os
import json
import logging
import tempfile
from typing import Dict, Any, Optional
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationConfig

logger = logging.getLogger(__name__)


def _setup_gcp_credentials():
    """
    Set up GCP credentials from environment variables.

    Supports two methods:
    1. GCP_CREDENTIALS_JSON: JSON credentials pasted directly as string
    2. GOOGLE_APPLICATION_CREDENTIALS: Path to credentials file

    If GCP_CREDENTIALS_JSON is set, creates a temporary file and sets
    GOOGLE_APPLICATION_CREDENTIALS to point to it.
    """
    # Check if credentials JSON is provided directly
    credentials_json = os.getenv("GCP_CREDENTIALS_JSON")

    if credentials_json:
        try:
            # Validate it's valid JSON
            json.loads(credentials_json)

            # Create a temporary file for the credentials
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False,
                prefix='gcp_credentials_'
            )

            # Write credentials to temp file
            temp_file.write(credentials_json)
            temp_file.flush()
            temp_file.close()

            # Set GOOGLE_APPLICATION_CREDENTIALS to the temp file path
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file.name

            logger.info(f"GCP credentials loaded from GCP_CREDENTIALS_JSON environment variable")
            logger.debug(f"Temporary credentials file created at: {temp_file.name}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in GCP_CREDENTIALS_JSON: {e}")
            raise ValueError(
                "GCP_CREDENTIALS_JSON contains invalid JSON. "
                "Please ensure you've pasted the complete service account key."
            )
        except Exception as e:
            logger.error(f"Error setting up GCP credentials from JSON: {e}")
            raise

    elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        # File-based credentials already configured
        logger.info(f"Using GCP credentials from file: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

    else:
        # No credentials configured - will attempt to use ADC
        logger.warning(
            "No GCP credentials found in GCP_CREDENTIALS_JSON or GOOGLE_APPLICATION_CREDENTIALS. "
            "Will attempt to use Application Default Credentials (ADC)."
        )


class ConceptSpreadService:
    """LLM service for generating concept-spread content"""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize Concept Spread service with Vertex AI Gemini

        Args:
            model_name: Gemini model name (defaults to LLM_CONCEPT_SPREAD env var)
        """
        # Set up GCP credentials
        _setup_gcp_credentials()

        # Read environment variables
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GEMINI_LOCATION")
        self.model_name = model_name or os.getenv("LLM_CONCEPT_SPREAD", "gemini-1.5-flash-002")

        # Validate required env vars
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID environment variable must be set")
        if not self.location:
            raise ValueError("GEMINI_LOCATION environment variable must be set")

        # Initialize Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)

        # Initialize Gemini model
        self.model = GenerativeModel(self.model_name)

        logger.info(f"Initialized ConceptSpreadService: model={self.model_name}")

    async def generate_concept_spread_content(
        self,
        topic: str,
        constraints: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate concept-spread content with hexagon labels, icons, and description bullets

        Args:
            topic: Main topic for the concept spread
            constraints: Character limits for each field
            context: Optional context (presentation history, etc.)

        Returns:
            {
                "success": bool,
                "content": {
                    "hex_1_label": str,
                    "hex_1_icon": str (unicode character),
                    "box_1_bullet_1": str,
                    ...
                },
                "usage_metadata": {...},
                "model": str
            }
        """
        try:
            # Build constraints string for prompt
            constraints_str = self._build_constraints_string(constraints)

            # Build previous slides context (if provided)
            previous_context_str = ""
            if context and context.get("previous_slides"):
                previous_context_str = self._build_previous_slides_context(context["previous_slides"])

            # Build complete prompt
            prompt = self._build_prompt(topic, constraints_str, previous_context_str)

            # Configure generation
            generation_config = GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )

            # Generate content with Gemini
            logger.info(f"Generating concept-spread content for topic: {topic}")
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Parse JSON response
            generated_content = json.loads(response.text)

            # Extract usage metadata
            usage_metadata = {}
            if hasattr(response, 'usage_metadata'):
                usage_metadata = {
                    "prompt_token_count": response.usage_metadata.prompt_token_count,
                    "candidates_token_count": response.usage_metadata.candidates_token_count,
                    "total_token_count": response.usage_metadata.total_token_count
                }

            logger.info(f"Successfully generated concept-spread content")
            return {
                "success": True,
                "content": generated_content,
                "usage_metadata": usage_metadata,
                "model": self.model_name
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            return {
                "success": False,
                "error": f"JSON parsing error: {str(e)}",
                "model": self.model_name
            }
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name
            }

    def _build_constraints_string(self, constraints: Dict[str, Any]) -> str:
        """Build constraints section for prompt"""
        constraints_str = "\n\nCharacter Constraints (MUST FOLLOW EXACTLY):"

        # Hexagon constraints
        constraints_str += "\n\nHEXAGONS (6 total):"
        for i in range(1, 7):
            hex_key = f"hex_{i}"
            if hex_key in constraints:
                label_min, label_max = constraints[hex_key]["label"]
                icon_count = constraints[hex_key]["icon"][0]
                constraints_str += f"\n- Hexagon {i} label: {label_min}-{label_max} characters, 1 word, Title Case (e.g., 'Strategy', 'Data')"
                constraints_str += f"\n- Hexagon {i} icon: EXACTLY {icon_count} Unicode emoji/pictograph (appropriate to concept)"

        # Description box constraints
        constraints_str += "\n\nDESCRIPTION BOXES (6 total, 3 bullets each):"
        for i in range(1, 7):
            box_key = f"box_{i}"
            if box_key in constraints:
                bullet_min, bullet_max = constraints[box_key]["bullet_1"]
                constraints_str += f"\n- Box {i}: 3 bullets, each {bullet_min}-{bullet_max} chars"
                constraints_str += f"\n  Use <strong> tags to emphasize 1-2 keywords per bullet"

        return constraints_str

    def _build_previous_slides_context(self, previous_slides: list) -> str:
        """Build previous slides context string"""
        context_str = "\n\nPrevious slides in this presentation:"
        for slide in previous_slides:
            slide_num = slide.get("slide_number")
            slide_title = slide.get("slide_title")
            slide_summary = slide.get("summary", "")
            context_str += f"\n- Slide {slide_num}: {slide_title}"
            if slide_summary:
                context_str += f"\n  {slide_summary}"

        context_str += "\n\nIMPORTANT: Ensure this concept-spread builds upon and complements the narrative established in previous slides."
        return context_str

    def _build_prompt(self, topic: str, constraints_str: str, previous_context_str: str) -> str:
        """Build complete LLM prompt"""
        prompt = f"""Generate a 6-hexagon concept-spread illustration for: "{topic}"

TASK: Create 6 related concepts arranged in hexagons with detailed description bullets.

HEXAGON REQUIREMENTS:
- Each hexagon has a 1-word LABEL in Title Case (e.g., "Strategy", "Data", "Growth" - NOT uppercase)
- Each label should be 4-12 characters
- Each hexagon has a UNICODE ICON (single emoji/pictograph, appropriate to the concept)
- 6 hexagons should represent different aspects/facets of the topic
- Concepts should be logically connected and comprehensive

UNICODE ICON SELECTION:
- Use COLORFUL, REPRESENTATIVE Unicode glyphs that visually match concepts
- PREFER colorful pictographs and symbols with visual impact
- Geometric shapes: ● ■ ▲ ▶ ◆ ★ ☆ ◉ ◈ ◊ ▣ ▢ ▧ ▨
- Arrows and directional: → ➜ ➤ ➔ ➡ ⇒ ⇨ ⇾ ↑ ↗ ↓ ↘
- Math and special: ∑ ∏ √ ∫ ∞ ≈ ± ∆ Φ Ω Σ
- Pictographs: ☀ ☁ ☂ ☃ ☄ ♠ ♣ ♥ ♦ ♪ ♫ ☎ ✈ ⚡ ⚙ ⚛
- Representative symbols: Choose icons that VISUALLY represent the concept
- Icons should be colorful, distinctive, and cross-platform compatible
- MUST be single character glyphs (not compound emojis like 🚀)
- Prioritize visual representation over simplicity

DESCRIPTION BOX REQUIREMENTS:
- Each hexagon has a corresponding description box
- Each box contains 3 bullets (36-63 characters each)
- Use <strong> tags to emphasize 1-2 key words per bullet
- Bullets should explain/expand on the hexagon concept
- NO title/heading in description box (bullets only)

{constraints_str}

{previous_context_str}

Return ONLY valid JSON in this exact format:
{{
  "hex_1_label": "Concept",
  "hex_1_icon": "●",
  "box_1_bullet_1": "First bullet with <strong>emphasis</strong> on keywords",
  "box_1_bullet_2": "Second bullet explaining the <strong>concept</strong>",
  "box_1_bullet_3": "Third bullet with actionable <strong>insight</strong>",
  "hex_2_label": "Strategy",
  "hex_2_icon": "▲",
  "box_2_bullet_1": "...",
  "box_2_bullet_2": "...",
  "box_2_bullet_3": "...",
  ... (continue for all 6 hexagons)
}}

CRITICAL RULES:
1. Each field must meet its character constraints EXACTLY
2. Count characters carefully (spaces count, HTML tags do NOT count)
3. Unicode icons must be single characters (not compound emojis)
4. Labels must be single words in Title Case (e.g., "Strategy", NOT "STRATEGY" or "strategy")
5. Use <strong> strategically (1-2 words per bullet)
6. Ensure 6 distinct, complementary concepts
"""
        return prompt
