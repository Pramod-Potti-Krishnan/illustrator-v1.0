# Pyramid Generation API Documentation

## Overview

The Pyramid Generation API provides LLM-powered content generation for hierarchical pyramid diagrams. It uses Gemini 2.5 Flash to generate level-specific text that meets character constraints and fills pre-validated HTML templates.

## Endpoint

```
POST /v1.0/pyramid/generate
```

## Features

- ✅ **LLM-Powered Content**: Uses Gemini 2.5 Flash for intelligent text generation
- ✅ **Character Constraints**: Enforces character limits per pyramid level
- ✅ **Validation & Retry**: Auto-retries if constraints are violated (max 2 attempts)
- ✅ **Template-Based**: Uses pre-validated, professionally designed HTML templates
- ✅ **4 Pyramid Variants**: Supports 3, 4, 5, and 6-level pyramids
- ✅ **Auto-Generated Overview**: 3 & 4 level pyramids automatically include overview section
- ✅ **Theme Support**: Compatible with existing theme system
- ✅ **Fast Generation**: <3 seconds typical response time

## Request Schema

### Basic Request (Backward Compatible)
```json
{
  "num_levels": 4,
  "topic": "Product Development Strategy",
  "tone": "professional",
  "audience": "executives"
}
```

### Full Request with Session Context (Aligns with Text Service v1.2)
```json
{
  "num_levels": 4,
  "topic": "Product Development Strategy",

  "presentation_id": "pres-abc-123",
  "slide_id": "slide-3",
  "slide_number": 3,

  "context": {
    "presentation_title": "Q4 Strategic Plan",
    "slide_purpose": "Show hierarchical development approach",
    "key_message": "Building from foundation to market leadership",
    "industry": "Technology",
    "previous_slides": [
      {
        "slide_number": 1,
        "slide_title": "Company Mission",
        "summary": "Our mission to revolutionize cloud infrastructure"
      },
      {
        "slide_number": 2,
        "slide_title": "Market Position",
        "summary": "Leading position in enterprise SaaS market"
      }
    ]
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
  "size": "medium",
  "validate_constraints": true,
  "generate_overview": true
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `num_levels` | int | ✅ | Number of pyramid levels (3-6) |
| `topic` | string | ✅ | Main topic/theme of pyramid |
| `presentation_id` | string | ❌ | **NEW** Presentation identifier for session tracking |
| `slide_id` | string | ❌ | **NEW** Unique slide identifier |
| `slide_number` | int | ❌ | **NEW** Slide position in deck |
| `context` | object | ❌ | Additional context (can include `previous_slides` array) |
| `context.previous_slides` | array | ❌ | **NEW** Previous slides for narrative continuity |
| `target_points` | array | ❌ | Key points to include in levels |
| `tone` | string | ❌ | Writing tone (default: "professional") |
| `audience` | string | ❌ | Target audience (default: "general") |
| `theme` | string | ❌ | Color theme (default: "professional") |
| `size` | string | ❌ | Size preset (default: "medium") |
| `validate_constraints` | boolean | ❌ | Enforce character limits (default: true) |
| `generate_overview` | boolean | ❌ | **DEPRECATED** - Overview automatically generated for 3 & 4 level pyramids |

#### Previous Slides Format
```json
"previous_slides": [
  {
    "slide_number": 1,
    "slide_title": "Introduction",
    "summary": "Brief summary of slide content"
  }
]
```

## Response Schema

```json
{
  "success": true,
  "html": "<div style='...'>...</div>",
  "metadata": {
    "num_levels": 4,
    "template_file": "4.html",
    "theme": "professional",
    "model": "gemini-2.0-flash-exp",
    "generation_time_ms": 2340,
    "attempts": 1
  },
  "generated_content": {
    "level_4_label": "Vision",
    "level_4_description": "Leadership defining organizational vision and strategic objectives",
    "level_3_label": "Strategy",
    "level_3_description": "Strategic planning and resource allocation for achieving vision",
    "level_2_label": "Operations",
    "level_2_description": "Operational management coordinating teams and processes",
    "level_1_label": "Execution",
    "level_1_description": "Day-to-day execution of tasks and delivery of results"
  },
  "character_counts": {
    "level_4": {"label": 6, "description": 68},
    "level_3": {"label": 8, "description": 71},
    "level_2": {"label": 10, "description": 62},
    "level_1": {"label": 9, "description": 56}
  },
  "validation": {
    "valid": true,
    "violations": []
  },
  "generation_time_ms": 2450,

  "presentation_id": "pres-abc-123",
  "slide_id": "slide-3",
  "slide_number": 3
}
```

**NEW Response Fields** (echoed from request):
- `presentation_id`: Presentation identifier (matches request)
- `slide_id`: Slide identifier (matches request)
- `slide_number`: Slide number (matches request)

## Character Constraints

Each pyramid level has specific character limits to ensure proper fit within the template:

### 3-Level Pyramid
- **Level 3** (top): label 15-20 chars, description 60-80 chars
- **Level 2**: label 18-25 chars, description 70-90 chars
- **Level 1** (base): label 20-28 chars, description 80-100 chars

### 4-Level Pyramid
- **Level 4** (top): label 15-18 chars, description 55-70 chars
- **Level 3**: label 16-22 chars, description 60-80 chars
- **Level 2**: label 18-24 chars, description 70-90 chars
- **Level 1** (base): label 20-28 chars, description 80-100 chars

### 5-Level Pyramid
- **Level 5** (top): label 12-16 chars, description 45-60 chars
- **Level 4**: label 14-18 chars, description 50-65 chars
- **Level 3**: label 16-20 chars, description 55-75 chars
- **Level 2**: label 18-24 chars, description 70-85 chars
- **Level 1** (base): label 20-28 chars, description 80-100 chars

### 6-Level Pyramid
- **Level 6** (top): label 10-14 chars, description 40-55 chars
- **Level 5**: label 12-16 chars, description 45-60 chars
- **Level 4**: label 14-18 chars, description 50-65 chars
- **Level 3**: label 16-20 chars, description 55-75 chars
- **Level 2**: label 18-24 chars, description 70-85 chars
- **Level 1** (base): label 20-28 chars, description 80-100 chars

## Example Usage

### Python (httpx)

```python
import httpx
import asyncio

async def generate_pyramid():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1.0/pyramid/generate",
            json={
                "num_levels": 4,
                "topic": "Growth Strategy",
                "tone": "professional",
                "audience": "executives"
            }
        )

        result = response.json()

        # Save HTML
        with open("pyramid.html", "w") as f:
            f.write(result["html"])

        print(f"Generated in {result['generation_time_ms']}ms")

asyncio.run(generate_pyramid())
```

### cURL

```bash
curl -X POST "http://localhost:8000/v1.0/pyramid/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_levels": 4,
    "topic": "Product Development Strategy",
    "context": {
      "presentation_title": "Q4 Strategic Plan"
    },
    "tone": "professional",
    "audience": "executives"
  }'
```

## Setup & Configuration

### 1. Install Dependencies

```bash
cd agents/illustrator/v1.0
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
GCP_PROJECT_ID=your-project-id
GEMINI_LOCATION=us-central1
LLM_PYRAMID=gemini-2.0-flash-exp
```

**Model Options**:
- `gemini-2.0-flash-exp` - Latest experimental model (fast, cutting-edge)
- `gemini-1.5-flash` - Stable fast model
- `gemini-1.5-flash-002` - Specific version of 1.5 Flash
- `gemini-1.5-pro` - More capable, slower model

### 3. Authenticate with GCP

```bash
gcloud auth application-default login
```

### 4. Start Service

```bash
python3 main.py
```

Service will start on `http://localhost:8000`

## Testing

Run the test script:

```bash
python3 test_pyramid_api.py
```

This will:
- Test 3, 4, and 5-level pyramids
- Validate character counts
- Save generated HTML to `test_pyramid_outputs/`
- Display generation times and validation results

## Integration with Director Service

The Director service can call this endpoint to generate pyramid slides:

```python
# In Director v3.3
from src.clients.illustrator_client import IllustratorClient

illustrator = IllustratorClient()

pyramid_html = await illustrator.generate_pyramid({
    "num_levels": 4,
    "topic": slide_spec["slide_title"],
    "presentation_id": presentation_id,
    "slide_id": slide_id,
    "slide_number": slide_number,
    "context": {
        "presentation_title": presentation_spec["presentation_title"],
        "slide_purpose": slide_spec["slide_purpose"],
        "previous_slides": previous_slides_context  # Pass from Director's session
    },
    "tone": slide_spec.get("tone", "professional")
})
```

## Multi-Pyramid Presentations (NEW)

When a presentation contains multiple pyramids, use the `previous_slides` context to maintain narrative continuity.

### Example: Two Pyramids in One Presentation

**Slide 2 - First Pyramid:**
```json
{
  "num_levels": 3,
  "topic": "Organizational Structure",
  "presentation_id": "pres-001",
  "slide_id": "slide-2",
  "slide_number": 2,
  "context": {
    "presentation_title": "Company Overview",
    "previous_slides": [
      {
        "slide_number": 1,
        "slide_title": "Introduction",
        "summary": "Company mission and vision overview"
      }
    ]
  }
}
```

**Slide 4 - Second Pyramid (knows about first pyramid):**
```json
{
  "num_levels": 4,
  "topic": "Skills Development Path",
  "presentation_id": "pres-001",
  "slide_id": "slide-4",
  "slide_number": 4,
  "context": {
    "presentation_title": "Company Overview",
    "previous_slides": [
      {
        "slide_number": 2,
        "slide_title": "Organizational Structure",
        "summary": "3-level pyramid showing CEO, Management, Teams hierarchy"
      },
      {
        "slide_number": 3,
        "slide_title": "Career Progression",
        "summary": "Overview of growth opportunities within the organization"
      }
    ]
  }
}
```

The LLM will ensure the second pyramid complements the first, maintaining consistent terminology and narrative flow.

## Error Handling

### Validation Failures

If generated content violates character constraints, the API will:
1. Retry generation (max 2 attempts)
2. Return violations in the `validation` field
3. Still return HTML (may not fit perfectly in template)

### LLM Failures

```json
{
  "detail": "Content generation failed: LLM timeout"
}
```

### Template Not Found

```json
{
  "detail": "Template not found: templates/pyramid/7.html"
}
```

## Performance

- **Typical generation time**: 2-3 seconds
- **Max retries on validation failure**: 2
- **Timeout**: 60 seconds
- **Token usage**: ~500-800 tokens per pyramid

## Architecture

```
Request → PyramidGenerator
            ↓
         Gemini 2.5 Flash (LLM)
            ↓
         PyramidValidator (constraints)
            ↓
         TemplateService (HTML assembly)
            ↓
         Response (HTML)
```

## Files Created

- `app/services/llm_service.py` - Gemini integration
- `app/services/pyramid_generator.py` - Content generation orchestrator
- `app/core/pyramid_validator.py` - Character constraint validation
- `app/routes/pyramid_routes.py` - API endpoint
- `app/variant_specs/pyramid_constraints.json` - Character limits
- `app/models.py` - Request/response models (extended)
- `test_pyramid_api.py` - Testing script
- `.env.example` - Configuration template

## Next Steps

1. Add Director integration client
2. Create comprehensive test suite
3. Add performance monitoring
4. Consider caching for identical requests
5. Add support for custom color themes per level
