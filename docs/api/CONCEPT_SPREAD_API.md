# Concept Spread Generation API Documentation

## Overview

The Concept Spread Generation API provides LLM-powered content generation for hexagonal concept-spread illustrations. It uses Gemini to generate hexagon labels, Unicode icons, and description bullets that meet character constraints and fills a pre-validated HTML template with interactive hover animations.

## Endpoint

```
POST /concept-spread/generate
```

## Features

- ✅ **LLM-Powered Content**: Uses Gemini for intelligent hexagon content generation
- ✅ **Character Constraints**: Enforces character limits for labels, icons, and bullets
- ✅ **Validation & Retry**: Auto-retries if constraints are violated (max 2 attempts)
- ✅ **Template-Based**: Uses pre-validated, professionally designed HTML template
- ✅ **6-Hexagon Layout**: Honeycomb arrangement with central framework name
- ✅ **Unicode Icons**: Simple Unicode pictographs for cross-platform compatibility
- ✅ **Interactive Hover**: Two-way hover animation between hexagons and description boxes
- ✅ **Previous Slides Context**: Maintains narrative continuity in presentations
- ✅ **Session Tracking**: Echoes presentation_id, slide_id, slide_number for stateless operation
- ✅ **Fast Generation**: <5 seconds typical response time

## Request Schema

### Basic Request
```json
{
  "topic": "Digital Transformation Strategy",
  "num_hexagons": 6
}
```

### Full Request with Session Context
```json
{
  "topic": "Digital Transformation Strategy",
  "num_hexagons": 6,
  
  "presentation_id": "pres-abc-123",
  "slide_id": "slide-5",
  "slide_number": 5,
  
  "context": {
    "previous_slides": [
      {
        "slide_number": 1,
        "slide_title": "Introduction to Digital Transformation",
        "summary": "Overview of digital transformation journey"
      },
      {
        "slide_number": 2,
        "slide_title": "Market Analysis",
        "summary": "Current market trends and competitive landscape"
      }
    ]
  },
  "tone": "professional",
  "audience": "executives",
  "validate_constraints": true
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `topic` | string | ✅ | Main topic for the concept spread framework |
| `num_hexagons` | int | ❌ | Number of hexagons (currently only 6 supported, default: 6) |
| `presentation_id` | string | ❌ | Presentation identifier for session tracking (echoed in response) |
| `slide_id` | string | ❌ | Unique slide identifier (echoed in response) |
| `slide_number` | int | ❌ | Slide position in deck (echoed in response) |
| `context` | object | ❌ | Additional context for generation |
| `context.previous_slides` | array | ❌ | Previous slides for narrative continuity |
| `tone` | string | ❌ | Writing tone (default: "professional") |
| `audience` | string | ❌ | Target audience (default: "general") |
| `validate_constraints` | boolean | ❌ | Enforce character limits (default: true) |

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

**Purpose**: Ensures generated hexagon concepts build upon and complement the narrative established in previous slides.

---

## Response Schema

### Success Response
```json
{
  "success": true,
  "html": "<div class='concept-spread-container'>...</div>",
  "generated_content": {
    "central_text": "<strong>DIGITAL TRANSFORMATION</strong>",
    "hex_1_label": "VISION",
    "hex_1_icon": "★",
    "box_1_bullet_1": "Define a clear <strong>future state</strong> for digital integration",
    "box_1_bullet_2": "Align leadership on <strong>strategic objectives</strong> and goals",
    "box_1_bullet_3": "Create a compelling <strong>vision statement</strong> for change",
    "hex_2_label": "ASSESS",
    "hex_2_icon": "∑",
    "box_2_bullet_1": "Evaluate current <strong>digital capabilities</strong> and gaps",
    "box_2_bullet_2": "Analyze <strong>technology infrastructure</strong> readiness",
    "box_2_bullet_3": "Identify key <strong>improvement areas</strong> and priorities",
    ...
  },
  "character_counts": {
    "central_text": {
      "char_count": 23,
      "with_html": 38
    },
    "hex_1_label": {
      "char_count": 6,
      "with_html": 6
    },
    ...
  },
  "validation": {
    "valid": true,
    "violations": []
  },
  "metadata": {
    "model": "gemini-2.5-flash-lite",
    "usage_metadata": {
      "prompt_token_count": 892,
      "candidates_token_count": 458,
      "total_token_count": 1350
    },
    "generation_time_ms": 4091,
    "attempts": 1
  },
  "generation_time_ms": 4091,
  "presentation_id": "pres-abc-123",
  "slide_id": "slide-5",
  "slide_number": 5
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Generation success status |
| `html` | string | Complete HTML fragment ready for insertion |
| `generated_content` | object | All LLM-generated field values (central_text, hex_labels, icons, bullets) |
| `character_counts` | object | Character count for each field (excluding HTML tags) |
| `validation` | object | Constraint validation results |
| `validation.valid` | boolean | Whether all constraints were met |
| `validation.violations` | array | List of constraint violations (if any) |
| `metadata` | object | Generation metadata |
| `metadata.model` | string | Gemini model used |
| `metadata.usage_metadata` | object | Token usage statistics |
| `metadata.generation_time_ms` | int | LLM generation time |
| `metadata.attempts` | int | Number of generation attempts (1-3) |
| `generation_time_ms` | int | Total API response time |
| `presentation_id` | string | Echoed from request (for session tracking) |
| `slide_id` | string | Echoed from request (for session tracking) |
| `slide_number` | int | Echoed from request (for session tracking) |

### Error Response
```json
{
  "success": false,
  "error": "Only 6-hexagon variant supported currently",
  "presentation_id": "pres-abc-123",
  "slide_id": "slide-5",
  "slide_number": 5
}
```

---

## Content Structure

### Central Text
- **Character Limit**: 5-30 characters
- **Format**: Bold uppercase text (can include `<strong>` tags)
- **Purpose**: Framework or topic name displayed in center
- **Example**: `<strong>DIGITAL TRANSFORMATION</strong>`

### Hexagons (6 total)
Each hexagon contains:

#### Label
- **Character Limit**: 4-12 characters
- **Format**: Single word, uppercase
- **Purpose**: Concept identifier
- **Examples**: `VISION`, `STRATEGY`, `GROWTH`, `EXECUTION`

#### Icon
- **Character Limit**: Exactly 1 Unicode character
- **Format**: Simple Unicode pictograph/symbol
- **Purpose**: Visual representation of concept
- **Recommended**: Geometric shapes, arrows, mathematical symbols, Greek letters
- **Examples**: `★ ● ■ ▲ ► → ∑ Δ Ω ∞`
- **Avoid**: Complex emojis (🚀💡📊) for cross-platform compatibility

### Description Boxes (6 total)
Each box contains 3 bullets:

#### Bullets
- **Character Limit**: 40-70 characters per bullet (excluding HTML tags)
- **Format**: Use `<strong>` tags to emphasize 1-2 keywords
- **Purpose**: Explain and expand on the hexagon concept
- **Examples**:
  - `Define a clear <strong>future state</strong> for digital integration`
  - `Align leadership on <strong>strategic objectives</strong> and goals`
  - `Create a compelling <strong>vision statement</strong> for change`

---

## Layout & Visual Design

### Hexagon Arrangement
- **Pattern**: Honeycomb (6 hexagons in circle around central text)
- **Mathematical Positioning**: Polar coordinates with 60° spacing
- **Dimensions**: 141px × 167px per hexagon
- **Color Gradients**: Each hexagon has unique gradient background

### Description Boxes
- **Layout**: 3 boxes on left, 3 boxes on right
- **Alignment**: Vertically distributed, aligned with corresponding hexagons
- **Color Matching**: Each box matches its hexagon's gradient
- **Content**: 3 bullets per box with `<strong>` emphasis

### Interactive Behavior
- **Two-Way Hover**: Hovering hexagon highlights corresponding box (and vice versa)
- **Animation**: Scale + translateY + box-shadow effect
- **Mobile**: Click interaction with 2-second auto-dismiss

### Colors
- **Innovation** (hex_1, box_5): Red-orange gradient (#c85a3d → #b54935)
- **Strategy** (hex_2, box_6): Pink gradient (#ec4899 → #db2777)
- **Growth** (hex_3, box_3): Amber gradient (#f59e0b → #d97706)
- **Execution** (hex_4, box_2): Blue gradient (#3b82f6 → #2563eb)
- **Market** (hex_5, box_1): Green gradient (#10b981 → #059669)
- **Future** (hex_6, box_4): Purple gradient (#8b5cf6 → #7c3aed)

---

## Character Constraints

### Full Constraints Specification
```json
{
  "concept_spread_6": {
    "central_text": {
      "text": [5, 30],
      "comment": "Central framework name, bold uppercase text"
    },
    "hex_1": {
      "label": [4, 12],
      "icon": [1, 1],
      "comment": "Label: 1 word, uppercase. Icon: single Unicode character/emoji"
    },
    "hex_2": { "label": [4, 12], "icon": [1, 1] },
    "hex_3": { "label": [4, 12], "icon": [1, 1] },
    "hex_4": { "label": [4, 12], "icon": [1, 1] },
    "hex_5": { "label": [4, 12], "icon": [1, 1] },
    "hex_6": { "label": [4, 12], "icon": [1, 1] },
    "box_1": {
      "bullet_1": [40, 70],
      "bullet_2": [40, 70],
      "bullet_3": [40, 70],
      "comment": "3 bullets per box, use <strong> for 1-2 keywords"
    },
    "box_2": { "bullet_1": [40, 70], "bullet_2": [40, 70], "bullet_3": [40, 70] },
    "box_3": { "bullet_1": [40, 70], "bullet_2": [40, 70], "bullet_3": [40, 70] },
    "box_4": { "bullet_1": [40, 70], "bullet_2": [40, 70], "bullet_3": [40, 70] },
    "box_5": { "bullet_1": [40, 70], "bullet_2": [40, 70], "bullet_3": [40, 70] },
    "box_6": { "bullet_1": [40, 70], "bullet_2": [40, 70], "bullet_3": [40, 70] }
  }
}
```

### Validation & Retry Logic
1. **First Attempt**: Generate content with character constraints in prompt
2. **Validation**: Check all fields against constraints
3. **If Valid**: Return HTML immediately
4. **If Invalid**: Retry up to 2 more times (max 3 attempts total)
5. **After Max Retries**: Return content anyway (graceful degradation)

---

## Usage Examples

### cURL
```bash
curl -X POST http://localhost:8000/concept-spread/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Digital Transformation Strategy",
    "num_hexagons": 6,
    "presentation_id": "pres-123",
    "slide_number": 5,
    "context": {
      "previous_slides": [
        {
          "slide_number": 1,
          "slide_title": "Introduction",
          "summary": "Overview of our digital journey"
        }
      ]
    },
    "tone": "professional",
    "audience": "executives"
  }'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/concept-spread/generate",
    json={
        "topic": "Digital Transformation Strategy",
        "num_hexagons": 6,
        "presentation_id": "pres-123",
        "slide_number": 5,
        "context": {
            "previous_slides": [
                {
                    "slide_number": 1,
                    "slide_title": "Introduction",
                    "summary": "Overview of our digital journey"
                }
            ]
        },
        "tone": "professional",
        "audience": "executives"
    }
)

data = response.json()
if data["success"]:
    print("Generated HTML:", data["html"][:100])
    print("Central Text:", data["generated_content"]["central_text"])
    print("Validation:", data["validation"]["valid"])
```

### JavaScript/TypeScript
```javascript
const response = await fetch('http://localhost:8000/concept-spread/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: 'Digital Transformation Strategy',
    num_hexagons: 6,
    presentation_id: 'pres-123',
    slide_number: 5,
    context: {
      previous_slides: [
        {
          slide_number: 1,
          slide_title: 'Introduction',
          summary: 'Overview of our digital journey'
        }
      ]
    },
    tone: 'professional',
    audience: 'executives'
  })
});

const data = await response.json();
if (data.success) {
  console.log('Generated HTML:', data.html.substring(0, 100));
  console.log('Central Text:', data.generated_content.central_text);
  console.log('Validation:', data.validation.valid);
}
```

---

## Integration with Director Agent

The Concept Spread API follows the **Illustrator API Design Principles** for seamless Director Agent integration:

### 1. Stateless Operation
- Director manages all state (presentation_id, slide_id, etc.)
- Illustrator echoes session fields without storing them
- Each request is independent and self-contained

### 2. Session Field Echoing
```json
// Request from Director
{
  "topic": "...",
  "presentation_id": "pres-123",
  "slide_id": "slide-5",
  "slide_number": 5
}

// Response from Illustrator
{
  "success": true,
  "html": "...",
  "presentation_id": "pres-123",  // Echoed
  "slide_id": "slide-5",           // Echoed
  "slide_number": 5                // Echoed
}
```

### 3. Previous Slides Context
```json
{
  "topic": "Digital Transformation",
  "context": {
    "previous_slides": [
      {
        "slide_number": 1,
        "slide_title": "Introduction",
        "summary": "Company digital transformation overview"
      },
      {
        "slide_number": 2,
        "slide_title": "Current State Assessment",
        "summary": "Analysis of existing digital capabilities"
      }
    ]
  }
}
```

**Benefit**: LLM generates hexagon concepts that complement and build upon previous slide narratives.

### 4. Graceful Degradation
- Returns content even if validation fails
- Provides detailed violation reports for debugging
- Never blocks slide generation due to constraint issues

---

## Health Check

```
GET /concept-spread/health
```

### Response
```json
{
  "status": "healthy",
  "service": "concept-spread",
  "supported_variants": [6]
}
```

---

## Technical Architecture

### Three-Layer Architecture
1. **Routes Layer** (`concept_spread_routes.py`): FastAPI endpoints, request/response validation
2. **Generator Layer** (`concept_spread_generator.py`): Orchestration, retry logic, template filling
3. **LLM Service Layer** (`concept_spread_service.py`): Gemini API, prompt construction

### Key Components
- **Template**: `templates/concept_spread/6.html` - HTML fragment with placeholders
- **Constraints**: `app/variant_specs/concept_spread_constraints.json` - Character limits
- **Validator**: `app/validators/constraint_validator.py` - Constraint validation
- **LLM Service**: `app/llm_services/concept_spread_service.py` - Gemini integration
- **Generator**: `app/generators/concept_spread_generator.py` - Orchestration layer
- **Routes**: `app/routes/concept_spread_routes.py` - FastAPI endpoints

### Environment Variables
```bash
GCP_PROJECT_ID=your-project-id
GEMINI_LOCATION=us-central1
LLM_CONCEPT_SPREAD=gemini-2.5-flash-lite
```

---

## Best Practices

### 1. Use Previous Slides Context
✅ **DO**: Provide previous_slides for narrative continuity
```json
{
  "context": {
    "previous_slides": [
      {"slide_number": 1, "slide_title": "...", "summary": "..."}
    ]
  }
}
```

❌ **DON'T**: Generate concept spreads in isolation without context

### 2. Echo Session Fields
✅ **DO**: Always pass presentation_id, slide_id, slide_number from Director
```json
{
  "presentation_id": "pres-123",
  "slide_id": "slide-5",
  "slide_number": 5
}
```

❌ **DON'T**: Store or manage state in Illustrator

### 3. Trust Validation with Graceful Degradation
✅ **DO**: Accept content even if `validation.valid: false`
```python
if data["success"]:
    html = data["html"]  # Use even if validation failed
    if not data["validation"]["valid"]:
        logger.warning(f"Validation issues: {data['validation']['violations']}")
```

❌ **DON'T**: Reject responses due to constraint violations

### 4. Monitor Generation Attempts
✅ **DO**: Track `metadata.attempts` for LLM performance monitoring
```python
if data["metadata"]["attempts"] > 1:
    logger.info(f"Required {data['metadata']['attempts']} attempts")
```

### 5. Use Simple Unicode Icons
✅ **DO**: Use simple geometric symbols: `★ ● ■ ▲ ► → ∑ Δ Ω ∞`

❌ **DON'T**: Request complex emojis (🚀💡📊) - they may render inconsistently

---

## Error Handling

### Common Errors

#### 1. Invalid Number of Hexagons
```json
// Request
{"topic": "Test", "num_hexagons": 8}

// Response
{
  "success": false,
  "error": "Only 6-hexagon variant supported currently"
}
```

#### 2. Missing Topic
```json
// Request
{"num_hexagons": 6}

// Response (422 Validation Error)
{
  "detail": [
    {
      "loc": ["body", "topic"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 3. LLM Generation Failure
```json
{
  "success": false,
  "error": "LLM generation failed: <error details>"
}
```

### Error Codes
- **200**: Success (even if validation failed - check `validation.valid`)
- **422**: Request validation error (missing/invalid fields)
- **500**: Internal server error (LLM failure, template not found, etc.)

---

## Performance

### Typical Response Times
- **Average**: 4-5 seconds
- **With Retry**: 8-12 seconds (if initial validation fails)
- **Token Usage**: ~1,300 tokens per generation

### Optimization Tips
1. Use `gemini-2.5-flash-lite` for speed
2. Enable `validate_constraints: true` to catch issues early
3. Provide clear, specific topics to reduce retry probability
4. Cache results by topic if generating multiple times

---

## Changelog

### v1.0.0 (2025-01-20)
- ✨ Initial release
- ✅ 6-hexagon concept spread variant
- ✅ LLM-powered content generation with Gemini
- ✅ Character constraint validation with retry logic
- ✅ Previous slides context support
- ✅ Session field echoing for Director integration
- ✅ Interactive two-way hover animations
- ✅ Simple Unicode icon generation

---

## Support & Contact

For issues or questions:
- Check `/concept-spread/health` endpoint for service status
- Review generated `character_counts` for constraint debugging
- Inspect `validation.violations` for specific constraint failures
- Monitor `metadata.attempts` for retry frequency

---

## See Also

- [Illustrator API Design Principles](../architecture/ILLUSTRATOR_API_DESIGN_PRINCIPLES.md)
- [Director Integration Guide](../guides/DIRECTOR_INTEGRATION_SUMMARY.md)
- [Pyramid API Documentation](./PYRAMID_API.md)
- [Funnel API Documentation](../guides/FUNNEL_DIRECTOR_INTEGRATION_GUIDE.md)
- [Concentric Circles API Documentation](../guides/CONCENTRIC_CIRCLES_DIRECTOR_INTEGRATION_GUIDE.md)
