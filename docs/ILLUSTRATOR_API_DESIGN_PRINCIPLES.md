# Illustrator API Design Principles

**Purpose**: This document captures the core design principles, architectural patterns, and best practices extracted from the Pyramid API implementation. These principles should guide all future illustration endpoint development.

**Source**: Pyramid API (v1.0) - Production-ready LLM-powered illustration service
**Last Updated**: 2025-11-15

---

## Table of Contents

1. [Core Architecture Principles](#core-architecture-principles)
2. [LLM Integration Best Practices](#llm-integration-best-practices)
3. [API Contract Design](#api-contract-design)
4. [Validation & Quality Assurance](#validation--quality-assurance)
5. [Template Architecture](#template-architecture)
6. [Environment Configuration](#environment-configuration)
7. [Integration with Director](#integration-with-director)
8. [Error Handling & Resilience](#error-handling--resilience)

---

## Core Architecture Principles

### 1. Stateless Service Design

**Principle**: The Illustrator service maintains NO server-side session state. Director is the sole "source of truth" for presentation context.

**Implementation**:
```python
# Director passes context IN every request
request = {
    "topic": "Product Strategy",
    "presentation_id": "pres-001",  # Optional - for correlation
    "slide_id": "slide-3",          # Optional
    "slide_number": 3,              # Optional
    "context": {
        "presentation_title": "Q4 Strategic Plan",
        "previous_slides": [...]    # Narrative continuity
    }
}

# Illustrator echoes session fields in response
response = {
    "success": true,
    "html": "<div>...</div>",
    "presentation_id": "pres-001",  # Echoed back
    "slide_id": "slide-3",          # Echoed back
    "slide_number": 3               # Echoed back
}
```

**Benefits**:
- Horizontal scaling (no session affinity)
- Simplified deployment (no session storage)
- Clear responsibility boundaries
- Aligns with Text Service v1.2 architecture

**Reference**: `agents/illustrator/v1.0/TEXT_SERVICE_ALIGNMENT_COMPLETE.md`

---

### 2. Three-Layer Architecture

**Principle**: Clear separation of concerns across orchestration, generation, and validation layers.

**Layer Structure**:
```
┌──────────────────────────────────┐
│   API Routes Layer               │  FastAPI endpoints
│   - Request validation           │  pyramid_routes.py
│   - Session field echoing        │
│   - Response assembly            │
└─────────────┬────────────────────┘
              ↓
┌──────────────────────────────────┐
│   Generator Layer                │  Business logic
│   - Orchestration                │  pyramid_generator.py
│   - Retry logic                  │
│   - Metadata assembly            │
└─────────────┬────────────────────┘
              ↓
┌──────────────────────────────────┐
│   LLM Service Layer              │  AI integration
│   - Prompt construction          │  llm_service.py
│   - Vertex AI calls              │
│   - JSON parsing                 │
└─────────────┬────────────────────┘
              ↓
┌──────────────────────────────────┐
│   Validation Layer               │  Quality assurance
│   - Constraint checking          │  pyramid_validator.py
│   - Character counting           │
│   - Violation reporting          │
└──────────────────────────────────┘
```

**Benefits**:
- Testable components (each layer can be unit tested)
- Easy to extend (add new layers without modifying existing)
- Clear debugging path (errors localized to specific layer)

---

### 3. Template-First Philosophy

**Principle**: Templates are pre-built, human-validated, and APPROVED before deployment. Runtime is simple placeholder substitution.

**Workflow**:
```
1. Design template in HTML+CSS
   ↓
2. Human review & validation
   ↓
3. Approve for production
   ↓
4. Deploy template file
   ↓
5. Runtime: LLM generates content → Fill placeholders
```

**Template Structure**:
```html
<!-- Pre-validated, fixed layout -->
<div class="pyramid-container">
    <div class="pyramid-level level-4">
        <div class="level-number">4</div>
        <div class="level-label">{level_4_label}</div>  <!-- Placeholder -->
    </div>
    <div class="description-text">{level_4_description}</div>
</div>
```

**Runtime Filling** (simple string replacement):
```python
filled_html = template_html
for key, value in generated_content.items():
    placeholder = f"{{{key}}}"
    filled_html = filled_html.replace(placeholder, value)
```

**Benefits**:
- Guaranteed visual quality (human-approved layouts)
- Fast runtime (no layout computation)
- Easy iteration (modify template, re-approve, deploy)
- No risk of LLM-generated broken HTML

**Reference**: `agents/illustrator/v1.0/README.md`

---

## LLM Integration Best Practices

### 1. Constraint-Driven Prompting

**Principle**: Inject precise character limits and formatting rules directly into LLM prompts to ensure generated content fits the template.

**Implementation**:
```python
# Build constraints from JSON spec
constraints_str = "\n\nCharacter Constraints (MUST FOLLOW EXACTLY):"
constraints_str += f"\n- Level 4 label (TOP): 1-2 words ONLY, each word 5-9 chars"
constraints_str += f"\n  If 2 words, format as: Word1<br>Word2"
constraints_str += f"\n  Total length (excluding <br>): 5-18 characters"
constraints_str += f"\n- Level 4 description: 50-60 characters"

prompt = f"""Generate a 4-level pyramid for: "{topic}"

Instructions:
1. Create hierarchical progression from base to peak
2. Top level label: MUST be 1-2 words, each 5-9 chars
3. Use <strong> tags to emphasize 1-2 key words per description

{constraints_str}

Return ONLY valid JSON in this exact format:
{{
  "level_4_label": "...",
  "level_4_description": "..."
}}"""
```

**Benefits**:
- High success rate (LLM follows explicit constraints)
- Fewer retries needed
- Predictable output format

**Reference**: `agents/illustrator/v1.0/app/llm_services/llm_service.py` (lines 229-310)

---

### 2. Context Injection for Narrative Continuity

**Principle**: Inject `previous_slides` context into prompts to ensure illustrations build upon the presentation narrative.

**Implementation**:
```python
# Build previous slides context
if context.get("previous_slides"):
    previous_context_str = "\n\nPrevious slides in this presentation:"
    for slide in previous_slides:
        slide_num = slide.get("slide_number")
        slide_title = slide.get("slide_title")
        slide_summary = slide.get("summary", "")
        previous_context_str += f"\n- Slide {slide_num}: {slide_title}"
        if slide_summary:
            previous_context_str += f"\n  {slide_summary}"

    previous_context_str += "\n\nIMPORTANT: Ensure this pyramid builds upon and complements the narrative established in previous slides."

    prompt = f"{base_prompt}{previous_context_str}"
```

**Example Scenario**:
- Slide 2: Pyramid about "Organizational Structure" (CEO → Managers → Teams)
- Slide 4: Pyramid about "Skills Development" should use consistent terminology and build on the org structure

**Benefits**:
- Consistent terminology across slides
- Coherent narrative flow
- Avoids contradictions between slides

**Reference**: `agents/illustrator/v1.0/app/llm_services/llm_service.py` (lines 214-227)

---

### 3. Retry Logic with Validation Feedback

**Principle**: Automatically retry LLM generation (max 2 times) when validation fails. Return content even after all retries exhausted.

**Implementation**:
```python
max_retries = 2

for attempt in range(max_retries + 1):
    # Generate content with LLM
    result = await llm_service.generate_pyramid_content(
        topic=topic,
        num_levels=num_levels,
        constraints=constraints
    )

    if not result["success"]:
        return result  # LLM error, abort

    # Validate constraints (if enabled)
    if validate_constraints:
        is_valid, violations = validator.validate_content(
            generated_content=result["content"],
            constraints=constraints
        )

        if is_valid:
            break  # Success! Exit retry loop
        else:
            logger.warning(f"Attempt {attempt + 1} failed validation: {violations}")
            continue  # Retry with same prompt
    else:
        break  # Validation disabled, accept result

# Return result (even if invalid after all retries)
return {
    "success": True,
    "content": result["content"],
    "validation": {
        "valid": is_valid,
        "violations": violations  # Detailed violations for debugging
    },
    "metadata": {
        "attempts": attempt + 1
    }
}
```

**Benefits**:
- Graceful degradation (return content even if invalid)
- Transparency (violations reported to caller)
- Automatic recovery (most violations fixed on retry)

**Reference**: `agents/illustrator/v1.0/app/services/pyramid_generator.py`

---

### 4. Structured Output with JSON Schema

**Principle**: Enforce strict JSON schema in LLM responses for predictable parsing.

**Implementation**:
```python
# Build JSON example in prompt
json_fields = {}
for level_num in range(num_levels, 0, -1):
    json_fields[f"level_{level_num}_label"] = f"Level {level_num} label text"
    json_fields[f"level_{level_num}_description"] = f"Level {level_num} description"

json_example = json.dumps(json_fields, indent=2)

prompt += f"""
Return ONLY valid JSON in this exact format:
{json_example}

CRITICAL:
- Every field must meet its character constraints exactly
- Count characters carefully (spaces count!)
- HTML tags do NOT count toward character limits
"""

# Configure Gemini for JSON output
generation_config = GenerationConfig(
    temperature=0.7,
    max_output_tokens=2048,
    response_mime_type="application/json"
)
```

**Benefits**:
- Predictable parsing (no regex needed)
- Type safety (Pydantic validation)
- Easy error handling (JSON parse failures are clear)

---

### 5. Usage Metadata Tracking

**Principle**: Return token usage and model metadata for cost tracking and debugging.

**Implementation**:
```python
# Extract usage metadata from Gemini response
usage_metadata = {}
if hasattr(response, 'usage_metadata'):
    usage_metadata = {
        "prompt_token_count": response.usage_metadata.prompt_token_count,
        "candidates_token_count": response.usage_metadata.candidates_token_count,
        "total_token_count": response.usage_metadata.total_token_count
    }

return {
    "success": True,
    "content": generated_content,
    "usage_metadata": usage_metadata,
    "model": self.model_name  # e.g., "gemini-1.5-flash-002"
}
```

**Benefits**:
- Cost tracking (tokens → API costs)
- Performance optimization (identify expensive prompts)
- Model versioning (know which model generated content)

---

## API Contract Design

### 1. Request Schema Pattern

**Principle**: Required fields for core functionality, optional fields for context and session management.

**Schema** (Pydantic):
```python
class PyramidGenerationRequest(BaseModel):
    # REQUIRED: Core functionality
    num_levels: int = Field(..., ge=3, le=6, description="Number of pyramid levels")
    topic: str = Field(..., min_length=1, description="Pyramid topic/theme")

    # OPTIONAL: Context & customization
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    target_points: Optional[List[str]] = Field(None, description="Key points to include")
    tone: str = Field("professional", description="Writing tone")
    audience: str = Field("general", description="Target audience")
    theme: str = Field("professional", description="Color theme")

    # OPTIONAL: Session management (for Director integration)
    presentation_id: Optional[str] = Field(None, description="Presentation identifier")
    slide_id: Optional[str] = Field(None, description="Slide identifier")
    slide_number: Optional[int] = Field(None, description="Slide position in deck")

    # OPTIONAL: Configuration
    validate_constraints: bool = Field(True, description="Enforce character limits")
```

**Benefits**:
- Backward compatible (optional fields can be added)
- Clear validation (Pydantic enforces types and constraints)
- Self-documenting (field descriptions become API docs)

---

### 2. Response Schema Pattern

**Principle**: Consistent response structure with success flag, output, metadata, and validation results.

**Schema**:
```python
class PyramidGenerationResponse(BaseModel):
    success: bool
    html: str  # Complete rendered illustration

    # Generated content (for debugging)
    generated_content: Dict[str, str]

    # Validation results
    character_counts: Dict[str, Dict[str, int]]
    validation: Dict[str, Any]  # {"valid": bool, "violations": [...]}

    # Metadata
    metadata: Dict[str, Any]  # model, generation_time_ms, attempts
    generation_time_ms: int

    # Session fields (echoed from request)
    presentation_id: Optional[str] = None
    slide_id: Optional[str] = None
    slide_number: Optional[int] = None
```

**Benefits**:
- Complete transparency (validation results, violations, attempts)
- Debugging support (character counts, generated content)
- Session correlation (echoed IDs match requests)

---

### 3. Session Field Echoing

**Principle**: Echo `presentation_id`, `slide_id`, `slide_number` from request to response for stateless correlation.

**Implementation** (`pyramid_routes.py` lines 117-120):
```python
return PyramidGenerationResponse(
    success=True,
    html=filled_html,
    generated_content=generated_content,
    # ... other fields ...
    presentation_id=request.presentation_id,  # Echo from request
    slide_id=request.slide_id,                # Echo from request
    slide_number=request.slide_number         # Echo from request
)
```

**Director Usage**:
```python
# Director makes async call
response = await illustrator.generate_pyramid(request)

# Match response to request using echoed fields
assert response.presentation_id == request.presentation_id
assert response.slide_id == request.slide_id
```

**Benefits**:
- Stateless correlation (no session storage needed)
- Async request tracking (match responses to requests)
- Multi-slide handling (Director can track multiple concurrent requests)

---

## Validation & Quality Assurance

### 1. Constraint Definition Files

**Principle**: Define character limits per illustration variant in JSON files, separate from code.

**File Structure** (`app/variant_specs/pyramid_constraints.json`):
```json
{
  "pyramid_4": {
    "level_4": {
      "label": [5, 18],
      "description": [50, 60],
      "comment": "Top level: 1-2 words, each word 5-9 chars, separated by <br>"
    },
    "level_3": {
      "label": [8, 20],
      "description": [50, 60],
      "comment": "Second from top: max 20 chars total"
    },
    "level_2": {
      "label": [12, 20],
      "description": [50, 60]
    },
    "level_1": {
      "label": [12, 20],
      "description": [50, 60]
    },
    "overview": {
      "text": [200, 250],
      "comment": "Only overview text generated - no heading displayed"
    }
  }
}
```

**Benefits**:
- Separation of concerns (constraints not hardcoded)
- Easy updates (modify JSON, no code changes)
- Documentation (comments explain special rules)
- Reusability (shared across validator and LLM service)

---

### 2. HTML-Aware Character Counting

**Principle**: Strip HTML tags before counting characters, since tags don't consume visual space.

**Implementation** (`pyramid_validator.py`):
```python
import re

def count_characters(text: str) -> int:
    """Count characters excluding HTML tags"""
    # Remove HTML tags
    text_without_html = re.sub(r'<[^>]+>', '', text)
    return len(text_without_html)

# Validation
label = "Vision<br>Driven"  # User sees: "Vision\nDriven"
char_count = count_characters(label)  # 12 chars (excludes <br>)

description = "Develop the <strong>product vision</strong> and blueprint"
char_count = count_characters(description)  # 45 chars (excludes <strong>)
```

**Benefits**:
- Accurate counting (matches visual perception)
- Allows formatting (can use `<br>`, `<strong>`, etc.)
- Consistent validation (same logic in validator and LLM prompt)

---

### 3. Violation Reporting

**Principle**: Provide detailed, field-level violation information for debugging and retry optimization.

**Implementation**:
```python
violations = []

for field_name, value in generated_content.items():
    char_count = count_characters(value)
    min_chars, max_chars = constraints[field_name]

    if char_count < min_chars or char_count > max_chars:
        violations.append({
            "field": field_name,
            "value": value,
            "char_count": char_count,
            "min_allowed": min_chars,
            "max_allowed": max_chars,
            "violation_type": "too_short" if char_count < min_chars else "too_long"
        })

return {
    "valid": len(violations) == 0,
    "violations": violations
}
```

**Example Violation**:
```json
{
  "valid": false,
  "violations": [
    {
      "field": "level_4_label",
      "value": "Achieve Strategic Excellence Leadership",
      "char_count": 42,
      "min_allowed": 5,
      "max_allowed": 18,
      "violation_type": "too_long"
    }
  ]
}
```

**Benefits**:
- Precise debugging (know exactly which field failed)
- Optimization insights (identify problematic constraints)
- Transparency (caller sees exactly what went wrong)

---

### 4. Configurable Validation

**Principle**: Allow validation to be disabled via `validate_constraints` flag for flexibility.

**Use Cases**:
- **Production**: `validate_constraints=true` (enforce quality)
- **Testing**: `validate_constraints=false` (test LLM behavior without retries)
- **Debugging**: `validate_constraints=false` (see raw LLM output)

**Implementation**:
```python
if request.validate_constraints:
    is_valid, violations = validator.validate_content(...)
    if not is_valid and attempt < max_retries:
        continue  # Retry
else:
    is_valid = True
    violations = []
```

---

## Template Architecture

### 1. HTML+CSS First, SVG Only When Necessary

**Principle**: Use HTML+CSS for rectangular/box-based layouts. Use SVG only for curves, circles, and complex paths.

**When to Use HTML+CSS**:
- Rectangles, squares, boxes → `<div>` with width/height
- Trapezoids, triangles → `clip-path: polygon()`
- Gradients → `linear-gradient()`, `radial-gradient()`
- Flexbox layouts → rows, columns, centering
- Grid layouts → 2×2 matrices, dashboards

**When to Use SVG**:
- Circles (perfect circles) → `<circle>` element
- Curved arrows → `<path>` with bezier curves
- Complex shapes → arbitrary polygons
- Text on curves → `<textPath>`

**Pyramid Example** (HTML+CSS):
```html
<!-- Trapezoid using clip-path -->
<div style="
    width: 76.17%;
    clip-path: polygon(12.6% 0%, 87.4% 0%, 100% 100%, 0% 100%);
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
">
    <div>Level 3</div>
</div>

<!-- Triangle (top level) -->
<div style="
    width: 28.51%;
    clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
">
    <div>Level 4</div>
</div>
```

**Benefits**:
- Simpler code (no SVG path calculations)
- Better text rendering (HTML text vs SVG text)
- Easier maintenance (CSS is more familiar than SVG)

**Reference**: `agents/illustrator/v1.0/templates/pyramid/*.html`

---

### 2. Embedded Styles (No External CSS)

**Principle**: All styles embedded in `<style>` tag within template. No external CSS files.

**Rationale**:
- Self-contained templates (no dependencies)
- Easy deployment (single HTML file)
- No path resolution issues
- Faster loading (no additional HTTP requests)

**Structure**:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* All styles here */
        .pyramid-container { ... }
        .level-4 .pyramid-shape { ... }
    </style>
</head>
<body>
    <div class="pyramid-container">
        <!-- Content with placeholders -->
    </div>
</body>
</html>
```

---

### 3. Placeholder Pattern

**Principle**: Use `{field_name}` syntax for placeholders. Simple string replacement at runtime.

**Template**:
```html
<div class="level-label">{level_4_label}</div>
<div class="description-text">{level_4_description}</div>
<div class="details-text">{overview_text}</div>
```

**Filling**:
```python
generated_content = {
    "level_4_label": "Vision<br>Driven",
    "level_4_description": "Define strategic <strong>goals</strong> and vision",
    "overview_text": "This pyramid illustrates..."
}

filled_html = template_html
for key, value in generated_content.items():
    filled_html = filled_html.replace(f"{{{key}}}", value)
```

**Benefits**:
- Simple implementation (no templating engine)
- Fast execution (pure string replacement)
- Easy debugging (search for `{` to find unfilled placeholders)

---

### 4. Fixed Layouts (Pre-Calculated Geometry)

**Principle**: Template geometry (widths, heights, positions) is pre-calculated and hardcoded. No runtime layout computation.

**Example** (4-level pyramid):
```css
/* Mathematically calculated widths for perfect taper */
/* H_total = 281px, W_total = 100%, N = 4, C = 0.356 */

/* Level 1 (Bottom): B1=100%, T1=80.8% */
.pyramid-level:nth-child(4) .pyramid-shape {
    width: 100%;
    clip-path: polygon(9.6% 0%, 90.4% 0%, 100% 100%, 0% 100%);
}

/* Level 2: B2=76.17%, T2=56.97% */
.pyramid-level:nth-child(3) .pyramid-shape {
    width: 76.17%;
    clip-path: polygon(12.6% 0%, 87.4% 0%, 100% 100%, 0% 100%);
}

/* Level 3: B3=52.34%, T3=33.14% */
.pyramid-level:nth-child(2) .pyramid-shape {
    width: 52.34%;
    clip-path: polygon(18.4% 0%, 81.6% 0%, 100% 100%, 0% 100%);
}

/* Level 4 (Top TRIANGLE): B4=28.51%, Height=81px */
.pyramid-level:nth-child(1) .pyramid-shape {
    width: 28.51%;
    height: 81px;
    clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
}
```

**Benefits**:
- Guaranteed visual consistency (no runtime variations)
- Performance (no layout calculations)
- Simplicity (what you see in template is what renders)

---

## Environment Configuration

### 1. Service-Specific Model Selection

**Principle**: Each illustration type can specify its optimal LLM model via environment variable.

**Pattern**:
```bash
# .env file
LLM_PYRAMID=gemini-1.5-flash-002       # Optimized for pyramid generation
LLM_FUNNEL=gemini-2.0-flash-exp        # Future: optimized for funnel
LLM_PROCESS_FLOW=gemini-1.5-flash     # Future: simpler model for flows
```

**Implementation**:
```python
class GeminiService:
    def __init__(self, model_name: Optional[str] = None):
        # Service-specific model from env
        self.model_name = model_name or os.getenv("LLM_PYRAMID")

        if not self.model_name:
            raise ValueError("LLM_PYRAMID environment variable must be set")

        self.model = GenerativeModel(self.model_name)
```

**Benefits**:
- Optimization (different models for different complexity)
- Cost control (use cheaper models for simpler illustrations)
- Experimentation (A/B test models without code changes)

**Reference**: `agents/illustrator/v1.0/.env.example`

---

### 2. Vertex AI with Application Default Credentials (ADC)

**Principle**: Use ADC for Vertex AI authentication. No API keys in code or env files.

**Setup**:
```bash
# Authenticate once (credentials stored in ~/.config/gcloud/)
gcloud auth application-default login
```

**Implementation**:
```python
from google.cloud import aiplatform

# Initialize Vertex AI with project/location
aiplatform.init(
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GEMINI_LOCATION")
)

# Model uses ADC automatically (no explicit credentials)
model = GenerativeModel(model_name)
```

**Benefits**:
- Security (no API keys in code/env)
- Simplicity (gcloud CLI handles auth)
- Rotation (credentials auto-refresh)

**Reference**: `agents/illustrator/v1.0/app/llm_services/llm_service.py`

---

### 3. Configuration Validation at Startup

**Principle**: Validate all required environment variables when service starts. Fail fast if misconfigured.

**Implementation**:
```python
class GeminiService:
    def __init__(self):
        # Read required env vars
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GEMINI_LOCATION")
        self.model_name = os.getenv("LLM_PYRAMID")

        # Validate ALL required vars present
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID environment variable must be set")

        if not self.location:
            raise ValueError("GEMINI_LOCATION environment variable must be set")

        if not self.model_name:
            raise ValueError("LLM_PYRAMID environment variable must be set")
```

**Benefits**:
- Fail fast (errors at startup, not during request)
- Clear error messages (know exactly what's missing)
- Prevents silent failures (misconfiguration caught immediately)

---

## Integration with Director

### 1. Director as State Manager

**Principle**: Director manages ALL presentation state. Illustrator is a stateless content generator.

**Director Responsibilities**:
- Track presentation context (title, theme, target audience)
- Maintain `previous_slides` history with summaries
- Manage slide ordering and dependencies
- Coordinate multiple service calls (Text, Illustrator, Diagram)

**Illustrator Responsibilities**:
- Receive context in each request
- Generate illustration based on context
- Return HTML with echoed session fields
- NO session storage, NO state management

**Flow**:
```
Director (Stateful)
├── Creates slide specification
├── Builds previous_slides array from history
├── Calls Illustrator with full context
│
Illustrator (Stateless)
├── Receives: topic, context, previous_slides
├── Injects context into LLM prompt
├── Generates content with narrative continuity
├── Returns: HTML + echoed session fields
│
Director
├── Receives response
├── Stores illustration in slide
├── Updates previous_slides history with summary
└── Continues to next slide
```

---

### 2. Previous Slides Context Pattern

**Principle**: Director passes `previous_slides` array with slide summaries. Illustrator injects into LLM prompt for narrative continuity.

**Director Preparation**:
```python
# Director builds context before calling Illustrator
previous_slides = []
for completed_slide in presentation.slides[:current_slide_index]:
    previous_slides.append({
        "slide_number": completed_slide.slide_number,
        "slide_title": completed_slide.title,
        "summary": completed_slide.generate_summary()  # AI-generated summary
    })

# Call Illustrator with context
request = {
    "topic": "Skills Development Path",
    "context": {
        "previous_slides": previous_slides
    }
}
response = await illustrator.generate_pyramid(request)
```

**Illustrator Processing**:
```python
# Illustrator injects into LLM prompt
if context.get("previous_slides"):
    prompt += "\n\nPrevious slides in this presentation:"
    for slide in previous_slides:
        prompt += f"\n- Slide {slide['slide_number']}: {slide['slide_title']}"
        if slide.get("summary"):
            prompt += f"\n  {slide['summary']}"

    prompt += "\n\nIMPORTANT: Build upon the narrative established in previous slides."
```

**Benefits**:
- Consistent terminology (LLM sees previous content)
- Coherent storyline (builds on prior context)
- Avoids repetition (knows what was already covered)

**Reference**: `agents/illustrator/v1.0/PYRAMID_API.md` (lines 98-107, 315-369)

---

## Error Handling & Resilience

### 1. Graceful Degradation

**Principle**: Return content even if validation fails after all retries. Include violation details for debugging.

**Implementation**:
```python
# After max retries exhausted
return PyramidGenerationResponse(
    success=True,  # Still return success (content was generated)
    html=filled_html,  # HTML may not perfectly fit template
    generated_content=generated_content,
    validation={
        "valid": False,
        "violations": violations  # Detailed violations
    },
    metadata={
        "attempts": max_retries + 1,
        "note": "Content returned despite validation failure"
    }
)
```

**Benefits**:
- Availability (service doesn't fail due to validation)
- Transparency (caller knows content is sub-optimal)
- Debugging (violations help diagnose issue)

---

### 2. Placeholder Cleanup

**Principle**: Remove unfilled placeholders to avoid visible `{field_name}` in rendered HTML.

**Implementation** (`pyramid_routes.py` lines 90-93):
```python
# Remove any remaining placeholders
import re
filled_html = re.sub(r'\{overview_heading\}', '', filled_html)
filled_html = re.sub(r'\{overview_text\}', '', filled_html)
```

**Use Case**: If LLM fails to generate `overview_text`, don't show `{overview_text}` placeholder to user.

---

### 3. Comprehensive Logging

**Principle**: Log all key events (LLM calls, validation results, retries) for debugging and monitoring.

**Implementation**:
```python
logger.info(f"Initialized GeminiService: model={self.model_name}")
logger.warning(f"Attempt {attempt + 1} failed validation: {violations}")
logger.error(f"Error generating content with Gemini: {e}")
```

---

## Summary: Key Takeaways

### For Future Illustration Endpoints

1. **Follow Three-Layer Architecture**: Routes → Generator → LLM Service → Validator
2. **Use Constraint-Driven Prompting**: Inject limits into LLM prompts
3. **Implement Retry Logic**: Max 2 retries on validation failure
4. **Echo Session Fields**: Return `presentation_id`, `slide_id`, `slide_number`
5. **Support Previous Slides Context**: Inject into LLM for narrative continuity
6. **Pre-Build Templates**: Human-validate layouts before deployment
7. **Use HTML+CSS First**: SVG only when necessary
8. **Graceful Degradation**: Return content even if validation fails
9. **Service-Specific Models**: Optimize LLM model per illustration type
10. **Comprehensive Metadata**: Return usage stats, attempts, violations

### Architecture Checklist

- [ ] Stateless service (no session storage)
- [ ] Three-layer separation (Routes, Generator, LLM, Validator)
- [ ] Constraint definition file (JSON)
- [ ] HTML+CSS template (pre-validated)
- [ ] Pydantic request/response models
- [ ] LLM retry logic (max 2)
- [ ] Session field echoing
- [ ] Previous slides context support
- [ ] Character constraint validation
- [ ] Graceful degradation
- [ ] Comprehensive logging
- [ ] Environment variable validation

---

**End of Design Principles Document**

**Next Steps**: Apply these principles when building future illustration endpoints (Funnel, Process Flow, Timeline, etc.)
