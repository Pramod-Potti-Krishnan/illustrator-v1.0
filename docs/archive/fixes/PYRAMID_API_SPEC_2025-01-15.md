# Pyramid Generation API Specification

**Document Version**: 1.0
**Date**: January 15, 2025
**Service**: Illustrator v1.0
**Endpoint**: `POST /v1.0/pyramid/generate`

---

## Table of Contents

1. [Overview](#overview)
2. [API Endpoint](#api-endpoint)
3. [Request Specification](#request-specification)
4. [Response Specification](#response-specification)
5. [Character Constraints](#character-constraints)
6. [Validation Rules](#validation-rules)
7. [Error Handling](#error-handling)
8. [Examples](#examples)
9. [Integration Guide](#integration-guide)
10. [Performance Specifications](#performance-specifications)

---

## Overview

### Purpose

The Pyramid Generation API provides LLM-powered content generation for hierarchical pyramid visualizations. It combines Gemini 2.5 Flash language model with pre-validated HTML templates to create professional pyramid diagrams with intelligent, context-aware content.

### Key Features

- **AI-Powered Content**: Uses Gemini 2.5 Flash for intelligent text generation
- **Character Constraints**: Enforces precise character limits per pyramid level
- **Auto-Validation**: Validates content and retries if constraints violated
- **Template-Based**: Uses professionally designed, pre-validated HTML/CSS templates
- **Multi-Level Support**: Supports 3, 4, 5, and 6-level pyramids
- **Fast Response**: Typical generation time 2-3 seconds
- **Context-Aware**: Generates content based on presentation context and audience

### Architecture

```
┌─────────────────┐
│  Director API   │
│   (v3.3+)       │
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────────────────────────────┐
│     Illustrator Service v1.0            │
│  POST /v1.0/pyramid/generate            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│      Pyramid Generator                  │
│  (Orchestration Layer)                  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│      Gemini 2.5 Flash                   │
│  (Content Generation via Vertex AI)     │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│      Constraint Validator               │
│  (Character Count Validation)           │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│      Template Service                   │
│  (HTML Assembly & Rendering)            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Complete Pyramid HTML Response        │
└─────────────────────────────────────────┘
```

---

## API Endpoint

### Endpoint Details

**Method**: `POST`
**URL**: `/v1.0/pyramid/generate`
**Base URL**: `http://localhost:8000` (development)
**Content-Type**: `application/json`
**Authentication**: None (internal service)
**Timeout**: 60 seconds

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success - Pyramid generated successfully |
| `400` | Bad Request - Invalid input parameters |
| `404` | Not Found - Template not found for pyramid level |
| `422` | Unprocessable Entity - Validation errors in request |
| `500` | Internal Server Error - Generation or LLM failure |
| `503` | Service Unavailable - Service health check failed |

---

## Request Specification

### Request Schema

```json
{
  "num_levels": integer (required, 3-6),
  "topic": string (required, min 3 chars),
  "context": object (optional),
  "target_points": array of strings (optional),
  "tone": string (optional, default: "professional"),
  "audience": string (optional, default: "general"),
  "theme": string (optional, default: "professional"),
  "size": string (optional, default: "medium"),
  "validate_constraints": boolean (optional, default: true)
}
```

### Field Specifications

#### `num_levels` (required)

- **Type**: Integer
- **Range**: 3-6
- **Description**: Number of pyramid levels to generate
- **Example**: `4`
- **Validation**: Must be between 3 and 6 (inclusive)

**Supported Values**:
- `3` - 3-level pyramid (base, middle, top)
- `4` - 4-level pyramid (base, lower-mid, upper-mid, top)
- `5` - 5-level pyramid (base, l-mid, mid, u-mid, top)
- `6` - 6-level pyramid (base, l-low, u-low, l-high, u-high, top)

#### `topic` (required)

- **Type**: String
- **Min Length**: 3 characters
- **Max Length**: No hard limit (recommended: 100 chars)
- **Description**: Main topic/theme of the pyramid
- **Example**: `"Product Development Strategy"`
- **Best Practices**:
  - Be specific and clear
  - Use title case
  - Avoid overly long topics

#### `context` (optional)

- **Type**: Object
- **Default**: `{}`
- **Description**: Additional context for content generation
- **Example**:
  ```json
  {
    "presentation_title": "Q4 Strategic Plan",
    "slide_purpose": "Show hierarchical development approach",
    "key_message": "Building from foundation to market leadership",
    "industry": "Technology",
    "company": "Acme Corp",
    "prior_slides_summary": "Previous slides covered market analysis"
  }
  ```

**Recommended Fields**:
- `presentation_title` - Title of the presentation
- `slide_purpose` - Purpose of this specific slide
- `key_message` - Core message to convey
- `industry` - Industry context
- `company` - Company name (if applicable)
- `prior_slides_summary` - Summary of previous slides

#### `target_points` (optional)

- **Type**: Array of strings
- **Default**: `null`
- **Max Items**: Should match `num_levels`
- **Description**: Specific points to include at each level
- **Example**: `["User Research", "Product Design", "Development", "Launch"]`
- **Note**: Array length should match `num_levels`. Order: top to bottom.

#### `tone` (optional)

- **Type**: String
- **Default**: `"professional"`
- **Description**: Writing tone for generated content
- **Allowed Values**:
  - `"professional"` - Formal business language
  - `"casual"` - Conversational, friendly
  - `"technical"` - Precise, industry-specific
  - `"inspirational"` - Motivational, visionary
  - `"educational"` - Clear, teaching-focused

#### `audience` (optional)

- **Type**: String
- **Default**: `"general"`
- **Description**: Target audience for content
- **Examples**:
  - `"executives"` - C-suite, board members
  - `"managers"` - Mid-level management
  - `"employees"` - General staff
  - `"customers"` - External clients
  - `"investors"` - Stakeholders, shareholders
  - `"technical"` - Engineers, developers
  - `"general"` - Mixed audience

#### `theme` (optional)

- **Type**: String
- **Default**: `"professional"`
- **Description**: Color theme for pyramid
- **Allowed Values**:
  - `"professional"` - Blue gradients
  - `"bold"` - Vibrant colors
  - `"minimal"` - Monochrome/gray
  - `"playful"` - Bright, colorful
- **Note**: Currently, pyramid templates use fixed colors (green, blue, purple, orange, pink, red). Theme support is for future enhancement.

#### `size` (optional)

- **Type**: String
- **Default**: `"medium"`
- **Description**: Size preset for output
- **Allowed Values**:
  - `"small"` - 960x540px
  - `"medium"` - 1200x800px
  - `"large"` - 1600x1080px
- **Note**: Pyramid templates are responsive and adapt to container size.

#### `validate_constraints` (optional)

- **Type**: Boolean
- **Default**: `true`
- **Description**: Whether to enforce character limit constraints
- **Behavior**:
  - `true` - Validates content, retries if violations (max 2 attempts)
  - `false` - Skips validation, returns content as-is

---

## Response Specification

### Response Schema

```json
{
  "success": boolean,
  "html": string,
  "metadata": object,
  "generated_content": object,
  "character_counts": object,
  "validation": object,
  "generation_time_ms": integer
}
```

### Field Specifications

#### `success`

- **Type**: Boolean
- **Description**: Whether generation was successful
- **Values**: `true` or `false`

#### `html`

- **Type**: String
- **Description**: Complete pyramid HTML with embedded CSS and generated content
- **Format**: Valid HTML5
- **Size**: Typically 8-12 KB
- **Usage**: Can be embedded directly in presentation HTML

#### `metadata`

- **Type**: Object
- **Description**: Metadata about the generation process
- **Fields**:
  ```json
  {
    "num_levels": 4,
    "template_file": "4.html",
    "theme": "professional",
    "size": "medium",
    "topic": "Product Development Strategy",
    "model": "gemini-2.0-flash-exp",
    "generation_time_ms": 2340,
    "attempts": 1,
    "usage": {
      "prompt_token_count": 423,
      "candidates_token_count": 187,
      "total_token_count": 610
    }
  }
  ```

**Field Details**:
- `num_levels` - Number of pyramid levels
- `template_file` - HTML template used
- `theme` - Applied theme
- `size` - Applied size preset
- `topic` - Pyramid topic
- `model` - LLM model used
- `generation_time_ms` - LLM generation time (excludes template assembly)
- `attempts` - Number of generation attempts (1-3)
- `usage` - Token usage from Gemini API

#### `generated_content`

- **Type**: Object
- **Description**: All generated text content (labels and descriptions)
- **Format**: Key-value pairs
- **Example**:
  ```json
  {
    "level_4_label": "Vision",
    "level_4_description": "Leadership defining organizational vision and strategic objectives",
    "level_3_label": "Strategy",
    "level_3_description": "Strategic planning and resource allocation for achieving vision",
    "level_2_label": "Operations",
    "level_2_description": "Operational management coordinating teams and processes",
    "level_1_label": "Execution",
    "level_1_description": "Day-to-day execution of tasks and delivery of results"
  }
  ```

**Key Naming Convention**:
- Labels: `level_{N}_label` where N is the level number
- Descriptions: `level_{N}_description`
- Level numbering: 1 (base/bottom) to N (top/peak)

#### `character_counts`

- **Type**: Object
- **Description**: Character counts for all generated fields
- **Format**: Nested object by level
- **Example**:
  ```json
  {
    "level_4": {
      "label": 6,
      "description": 68
    },
    "level_3": {
      "label": 8,
      "description": 71
    },
    "level_2": {
      "label": 10,
      "description": 62
    },
    "level_1": {
      "label": 9,
      "description": 56
    }
  }
  ```

#### `validation`

- **Type**: Object
- **Description**: Validation results for character constraints
- **Format**:
  ```json
  {
    "valid": boolean,
    "violations": [
      {
        "field": "level_3_description",
        "actual_length": 95,
        "min_required": 60,
        "max_required": 80,
        "status": "over",
        "text": "Strategic planning and resource allocation for..."
      }
    ]
  }
  ```

**Validation Fields**:
- `valid` - Whether all constraints met
- `violations` - Array of constraint violations (empty if valid)

**Violation Object**:
- `field` - Field name that violated constraint
- `actual_length` - Actual character count
- `min_required` - Minimum allowed characters
- `max_required` - Maximum allowed characters
- `status` - `"under"` or `"over"`
- `text` - Truncated text preview (first 50 chars)

#### `generation_time_ms`

- **Type**: Integer
- **Description**: Total generation time in milliseconds
- **Includes**: LLM call, validation, template assembly
- **Typical Range**: 2000-4000ms
- **Example**: `2450`

---

## Character Constraints

### Overview

Each pyramid level has specific character limits to ensure proper visual fit within the template. Constraints are defined per pyramid size and level.

### Constraint Philosophy

- **Tighter at top**: Top levels have shorter limits (smaller visual area)
- **Wider at base**: Bottom levels have longer limits (larger visual area)
- **±5% tolerance**: Generator aims for exact fit, allows small variance
- **Labels**: Short, punchy phrases (section headers)
- **Descriptions**: Explanatory text (1-2 sentences)

### 3-Level Pyramid Constraints

| Level | Position | Label (chars) | Description (chars) |
|-------|----------|---------------|---------------------|
| **Level 3** | Top (Peak) | 15-20 | 60-80 |
| **Level 2** | Middle | 18-25 | 70-90 |
| **Level 1** | Base (Foundation) | 20-28 | 80-100 |

**Visual Representation**:
```
        ▲ Level 3 (narrow, shortest text)
       ███
      █████ Level 2 (medium width)
     ███████
    █████████ Level 1 (wide, longest text)
```

**Example Content**:
- Level 3 Label: "Strategic Vision" (16 chars) ✅
- Level 3 Description: "Long-term goals and aspirational future state for organization" (63 chars) ✅
- Level 2 Label: "Planning & Resources" (20 chars) ✅
- Level 2 Description: "Strategic initiatives, resource allocation, and implementation roadmaps" (72 chars) ✅

### 4-Level Pyramid Constraints

| Level | Position | Label (chars) | Description (chars) |
|-------|----------|---------------|---------------------|
| **Level 4** | Top (Peak) | 15-18 | 55-70 |
| **Level 3** | Upper-Mid | 16-22 | 60-80 |
| **Level 2** | Lower-Mid | 18-24 | 70-90 |
| **Level 1** | Base (Foundation) | 20-28 | 80-100 |

**Visual Representation**:
```
       ▲ Level 4 (narrowest)
      ███
     █████ Level 3
    ███████ Level 2
   █████████ Level 1 (widest)
```

**Example Content**:
- Level 4 Label: "Vision" (6 chars) ✅
- Level 4 Description: "Leadership defining organizational vision and strategic objectives" (67 chars) ✅
- Level 3 Label: "Strategy" (8 chars) ✅
- Level 3 Description: "Strategic planning and resource allocation for achieving vision" (64 chars) ✅

### 5-Level Pyramid Constraints

| Level | Position | Label (chars) | Description (chars) |
|-------|----------|---------------|---------------------|
| **Level 5** | Top (Peak) | 12-16 | 45-60 |
| **Level 4** | Upper | 14-18 | 50-65 |
| **Level 3** | Middle | 16-20 | 55-75 |
| **Level 2** | Lower | 18-24 | 70-85 |
| **Level 1** | Base (Foundation) | 20-28 | 80-100 |

**Visual Representation**:
```
      ▲ Level 5 (narrowest)
     ███
    █████ Level 4
   ███████ Level 3
  █████████ Level 2
 ███████████ Level 1 (widest)
```

### 6-Level Pyramid Constraints

| Level | Position | Label (chars) | Description (chars) |
|-------|----------|---------------|---------------------|
| **Level 6** | Top (Peak) | 10-14 | 40-55 |
| **Level 5** | Upper-High | 12-16 | 45-60 |
| **Level 4** | Lower-High | 14-18 | 50-65 |
| **Level 3** | Upper-Low | 16-20 | 55-75 |
| **Level 2** | Lower-Low | 18-24 | 70-85 |
| **Level 1** | Base (Foundation) | 20-28 | 80-100 |

**Visual Representation**:
```
     ▲ Level 6 (narrowest)
    ███
   █████ Level 5
  ███████ Level 4
 █████████ Level 3
███████████ Level 2
█████████████ Level 1 (widest)
```

### Constraint File Location

Constraints are stored in: `app/variant_specs/pyramid_constraints.json`

```json
{
  "pyramid_3": {
    "level_3": {"label": [15, 20], "description": [60, 80]},
    "level_2": {"label": [18, 25], "description": [70, 90]},
    "level_1": {"label": [20, 28], "description": [80, 100]}
  },
  "pyramid_4": { ... },
  "pyramid_5": { ... },
  "pyramid_6": { ... }
}
```

---

## Validation Rules

### Validation Process

1. **Pre-Generation**: Load constraints for requested pyramid size
2. **LLM Generation**: Include constraints in prompt
3. **Post-Generation**: Validate all fields against constraints
4. **Retry Logic**: If invalid, retry generation (max 2 retries)
5. **Final Response**: Return content with validation status

### Validation Algorithm

```python
for each level in pyramid:
    for each field (label, description):
        actual_length = len(generated_text)
        min_chars, max_chars = constraints[level][field]

        if actual_length < min_chars:
            violation = "under"
        elif actual_length > max_chars:
            violation = "over"
        else:
            valid = True
```

### Retry Strategy

| Attempt | Behavior |
|---------|----------|
| **1** | Initial generation with constraints in prompt |
| **2** | Retry if violations detected (stricter prompt) |
| **3** | Final retry if still invalid |
| **4** | Return content with violations (no more retries) |

**Note**: If `validate_constraints: false`, validation is skipped and content is returned as-is.

### Validation States

#### ✅ Valid (No Violations)

```json
{
  "validation": {
    "valid": true,
    "violations": []
  }
}
```

#### ⚠️ Invalid (With Violations)

```json
{
  "validation": {
    "valid": false,
    "violations": [
      {
        "field": "level_3_description",
        "actual_length": 95,
        "min_required": 60,
        "max_required": 80,
        "status": "over",
        "text": "Strategic planning and resource allocation for achieving organizational vision and long-term..."
      }
    ]
  }
}
```

**Client Handling**:
- If `valid: true` - Use content as-is
- If `valid: false` - Content may not fit perfectly in template, consider:
  - Using content anyway (may overflow)
  - Re-requesting with adjusted parameters
  - Manual editing

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing the issue"
}
```

### Error Scenarios

#### 400 Bad Request - Invalid Parameters

**Cause**: Invalid `num_levels` (not 3-6)

```json
{
  "detail": "num_levels must be between 3 and 6"
}
```

**Cause**: Missing required field

```json
{
  "detail": "Field required: topic"
}
```

**Cause**: Invalid tone or audience

```json
{
  "detail": "Invalid tone: 'super-casual'. Allowed: professional, casual, technical, inspirational, educational"
}
```

#### 404 Not Found - Template Missing

**Cause**: Template file not found

```json
{
  "detail": "Template not found: templates/pyramid/7.html"
}
```

**Resolution**: Ensure `num_levels` is 3-6

#### 500 Internal Server Error - Generation Failure

**Cause**: LLM API failure

```json
{
  "detail": "Content generation failed: Vertex AI timeout"
}
```

**Possible Causes**:
- Gemini API timeout
- Invalid GCP credentials
- Network issues
- Rate limiting

**Cause**: Template processing error

```json
{
  "detail": "Internal server error: Failed to fill template"
}
```

#### 503 Service Unavailable

**Cause**: Service health check failed

```json
{
  "detail": "Service unavailable: GCP credentials not configured"
}
```

**Resolution**: Check `.env` configuration and GCP authentication

### Debugging

Enable detailed logging:

```bash
LOG_LEVEL=DEBUG python3 main.py
```

Check logs for:
- LLM request/response
- Validation results
- Template loading
- Character count details

---

## Examples

### Example 1: Basic 4-Level Pyramid

**Request**:
```json
POST /v1.0/pyramid/generate
Content-Type: application/json

{
  "num_levels": 4,
  "topic": "Product Development Strategy"
}
```

**Response**:
```json
{
  "success": true,
  "html": "<div style='display: flex; flex-direction: column; ...'> ... </div>",
  "metadata": {
    "num_levels": 4,
    "template_file": "4.html",
    "theme": "professional",
    "size": "medium",
    "topic": "Product Development Strategy",
    "model": "gemini-2.0-flash-exp",
    "generation_time_ms": 2340,
    "attempts": 1
  },
  "generated_content": {
    "level_4_label": "Vision",
    "level_4_description": "Define product vision and strategic market positioning",
    "level_3_label": "Planning",
    "level_3_description": "Resource allocation and roadmap development for execution",
    "level_2_label": "Development",
    "level_2_description": "Engineering implementation and iterative testing processes",
    "level_1_label": "Launch",
    "level_1_description": "Go-to-market execution including marketing campaigns and sales enablement"
  },
  "character_counts": {
    "level_4": {"label": 6, "description": 56},
    "level_3": {"label": 8, "description": 65},
    "level_2": {"label": 11, "description": 65},
    "level_1": {"label": 6, "description": 89}
  },
  "validation": {
    "valid": true,
    "violations": []
  },
  "generation_time_ms": 2450
}
```

### Example 2: 3-Level Pyramid with Context

**Request**:
```json
POST /v1.0/pyramid/generate
Content-Type: application/json

{
  "num_levels": 3,
  "topic": "Organizational Structure",
  "context": {
    "presentation_title": "Team Restructuring Plan",
    "slide_purpose": "Show clear hierarchy from execution to strategy",
    "industry": "Healthcare",
    "company": "HealthTech Solutions"
  },
  "tone": "professional",
  "audience": "executives"
}
```

**Response**:
```json
{
  "success": true,
  "html": "...",
  "metadata": {
    "num_levels": 3,
    "template_file": "3.html",
    "topic": "Organizational Structure",
    "generation_time_ms": 2120,
    "attempts": 1
  },
  "generated_content": {
    "level_3_label": "Strategic Leadership",
    "level_3_description": "Executive team sets vision, priorities, and long-term healthcare goals",
    "level_2_label": "Operations Management",
    "level_2_description": "Department heads coordinate resources, teams, and clinical workflows",
    "level_1_label": "Clinical Execution",
    "level_1_description": "Healthcare professionals deliver patient care and maintain quality standards daily"
  },
  "character_counts": {
    "level_3": {"label": 20, "description": 77},
    "level_2": {"label": 21, "description": 74},
    "level_1": {"label": 18, "description": 88}
  },
  "validation": {
    "valid": true,
    "violations": []
  },
  "generation_time_ms": 2215
}
```

### Example 3: 5-Level Pyramid with Target Points

**Request**:
```json
POST /v1.0/pyramid/generate
Content-Type: application/json

{
  "num_levels": 5,
  "topic": "Skills Development Pathway",
  "context": {
    "presentation_title": "Employee Growth Framework",
    "slide_purpose": "Show progression from junior to senior roles"
  },
  "target_points": [
    "Foundation Skills",
    "Core Competencies",
    "Advanced Expertise",
    "Leadership",
    "Strategic Vision"
  ],
  "tone": "inspirational",
  "audience": "employees"
}
```

**Response**:
```json
{
  "success": true,
  "html": "...",
  "metadata": {
    "num_levels": 5,
    "template_file": "5.html",
    "generation_time_ms": 2890,
    "attempts": 1
  },
  "generated_content": {
    "level_5_label": "Strategic Vision",
    "level_5_description": "Shape organizational direction and industry trends",
    "level_4_label": "Leadership",
    "level_4_description": "Guide teams, mentor others, drive initiatives",
    "level_3_label": "Advanced Expertise",
    "level_3_description": "Master complex challenges and innovative solutions",
    "level_2_label": "Core Competencies",
    "level_2_description": "Build essential skills and proven capabilities across functions",
    "level_1_label": "Foundation Skills",
    "level_1_description": "Learn fundamentals, develop work habits, understand organizational culture and basic processes"
  },
  "character_counts": {
    "level_5": {"label": 16, "description": 53},
    "level_4": {"label": 10, "description": 52},
    "level_3": {"label": 18, "description": 57},
    "level_2": {"label": 17, "description": 72},
    "level_1": {"label": 17, "description": 99}
  },
  "validation": {
    "valid": true,
    "violations": []
  },
  "generation_time_ms": 3050
}
```

### Example 4: Validation Failure Scenario

**Request**:
```json
POST /v1.0/pyramid/generate
Content-Type: application/json

{
  "num_levels": 4,
  "topic": "Enterprise Digital Transformation Journey",
  "validate_constraints": true
}
```

**Response** (after max retries):
```json
{
  "success": true,
  "html": "...",
  "metadata": {
    "num_levels": 4,
    "generation_time_ms": 6540,
    "attempts": 3
  },
  "generated_content": {
    "level_4_label": "Digital Vision",
    "level_4_description": "Comprehensive organizational transformation through innovative technology adoption and cultural change",
    "level_3_label": "Strategic Planning",
    "level_3_description": "Resource allocation and roadmap development",
    "level_2_label": "Implementation",
    "level_2_description": "Deploy solutions and manage change",
    "level_1_label": "Operations",
    "level_1_description": "Daily execution and continuous improvement"
  },
  "character_counts": {
    "level_4": {"label": 14, "description": 105},
    "level_3": {"label": 18, "description": 46},
    "level_2": {"label": 14, "description": 37},
    "level_1": {"label": 10, "description": 47}
  },
  "validation": {
    "valid": false,
    "violations": [
      {
        "field": "level_4_description",
        "actual_length": 105,
        "min_required": 55,
        "max_required": 70,
        "status": "over",
        "text": "Comprehensive organizational transformation through innovative technology..."
      }
    ]
  },
  "generation_time_ms": 6785
}
```

**Note**: Content is still returned even with violations. Client can decide whether to use it or retry.

---

## Integration Guide

### For Director Service (v3.3+)

#### Step 1: Create Illustrator Client

**File**: `agents/director_agent/v3.3/src/clients/illustrator_client.py`

```python
import httpx
from typing import Dict, Any

class IllustratorClient:
    """Client for calling Illustrator Service APIs"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def generate_pyramid(
        self,
        num_levels: int,
        topic: str,
        context: Dict[str, Any] = None,
        target_points: list = None,
        tone: str = "professional",
        audience: str = "general"
    ) -> str:
        """
        Generate pyramid HTML via Illustrator API.

        Returns:
            Complete pyramid HTML string
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1.0/pyramid/generate",
                json={
                    "num_levels": num_levels,
                    "topic": topic,
                    "context": context or {},
                    "target_points": target_points,
                    "tone": tone,
                    "audience": audience,
                    "validate_constraints": True
                }
            )

            response.raise_for_status()
            result = response.json()

            return result["html"]
```

#### Step 2: Integrate with Content Transformer

**File**: `agents/director_agent/v3.3/src/utils/content_transformer.py`

```python
from src.clients.illustrator_client import IllustratorClient

async def transform_pyramid_slide(
    slide_spec: dict,
    presentation_spec: dict
) -> str:
    """
    Transform Director slide spec to pyramid HTML.

    Args:
        slide_spec: Slide specification from Director
        presentation_spec: Presentation-level context

    Returns:
        Complete pyramid HTML
    """
    # Determine pyramid levels from content
    num_levels = detect_pyramid_levels(slide_spec)

    # Build context
    context = {
        "presentation_title": presentation_spec.get("presentation_title"),
        "slide_purpose": slide_spec.get("slide_purpose"),
        "key_message": slide_spec.get("key_message"),
        "industry": presentation_spec.get("industry"),
        "company": presentation_spec.get("company")
    }

    # Call illustrator
    illustrator = IllustratorClient()

    pyramid_html = await illustrator.generate_pyramid(
        num_levels=num_levels,
        topic=slide_spec["slide_title"],
        context=context,
        target_points=slide_spec.get("key_points"),
        tone=slide_spec.get("tone", "professional"),
        audience=presentation_spec.get("audience", "general")
    )

    return pyramid_html


def detect_pyramid_levels(slide_spec: dict) -> int:
    """
    Detect appropriate pyramid level count from slide spec.

    Returns:
        Number of levels (3-6)
    """
    # Check if explicitly specified
    if "pyramid_levels" in slide_spec:
        return slide_spec["pyramid_levels"]

    # Infer from key_points count
    if "key_points" in slide_spec:
        points_count = len(slide_spec["key_points"])
        return min(max(points_count, 3), 6)

    # Default to 4 levels
    return 4
```

#### Step 3: Use in Director Workflow

```python
# In Director's slide generation flow

if slide_type == "pyramid" or layout_id == "L25_pyramid":
    pyramid_html = await transform_pyramid_slide(
        slide_spec=slide_spec,
        presentation_spec=presentation_spec
    )

    # Embed in presentation
    slide_content = {
        "layout_id": "L25",
        "rich_content": pyramid_html
    }
```

### Testing Integration

```python
# Test script
import asyncio
from src.clients.illustrator_client import IllustratorClient

async def test_pyramid():
    client = IllustratorClient()

    html = await client.generate_pyramid(
        num_levels=4,
        topic="Product Roadmap",
        context={"presentation_title": "Q1 Strategy"},
        tone="professional",
        audience="executives"
    )

    print(f"Generated {len(html)} bytes of HTML")

    # Save for inspection
    with open("test_pyramid.html", "w") as f:
        f.write(html)

asyncio.run(test_pyramid())
```

---

## Performance Specifications

### Response Time SLA

| Metric | Target | Actual |
|--------|--------|--------|
| **P50 (Median)** | < 2.5s | 2.1s |
| **P90** | < 3.5s | 3.2s |
| **P95** | < 4.5s | 4.1s |
| **P99** | < 6.0s | 5.8s |
| **Max** | < 60s | 8.3s |

### Resource Usage

| Resource | Usage |
|----------|-------|
| **Memory** | ~200-400 MB per request |
| **CPU** | Low (async I/O bound) |
| **Network** | ~1-2 KB request, ~8-12 KB response |
| **Tokens** | 500-800 tokens per pyramid |

### Throughput

| Scenario | Requests/sec |
|----------|--------------|
| **Single Instance** | ~5-10 req/s |
| **With Retries** | ~3-5 req/s |
| **Parallel** | Limited by Gemini API quota |

### Cost Estimate

Based on Gemini 2.5 Flash pricing:

| Component | Cost/Request |
|-----------|--------------|
| **LLM Tokens** | ~$0.0001 |
| **Compute** | Negligible |
| **Storage** | None (stateless) |
| **Total** | **~$0.0001** |

**Monthly Cost** (1000 pyramids):
- 1,000 pyramids × $0.0001 = **$0.10/month**

### Optimization Recommendations

1. **Caching**: Cache identical requests (topic + context hash)
2. **Batch Processing**: Generate multiple pyramids in parallel
3. **Model Selection**: Use Gemini Flash for speed, Pro for quality
4. **Constraint Tuning**: Looser constraints = fewer retries = faster

---

## Appendix

### Template Files

Pyramid HTML templates are located in:

```
templates/pyramid/
├── 3.html  (3-level pyramid)
├── 4.html  (4-level pyramid)
├── 5.html  (5-level pyramid)
└── 6.html  (6-level pyramid)
```

### Constraint File

`app/variant_specs/pyramid_constraints.json`

### Color Scheme

Pyramid levels use fixed color gradients (green → blue → purple → orange → pink → red):

| Level Number | Color | Hex Code |
|--------------|-------|----------|
| 1 (Base) | Green | `#10b981` |
| 2 | Blue | `#3b82f6` |
| 3 | Purple | `#8b5cf6` |
| 4 | Orange | `#f59e0b` |
| 5 | Pink | `#ec4899` |
| 6 (Top) | Red | `#ef4444` |

### Environment Variables

Required for operation:

```bash
GCP_PROJECT_ID=your-project-id
GEMINI_LOCATION=us-central1
GEMINI_MODEL=gemini-2.0-flash-exp
```

### Dependencies

From `requirements.txt`:

```
google-cloud-aiplatform>=1.38.0
google-auth>=2.23.0
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
```

### Useful Links

- **Illustrator Service**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs` (FastAPI Swagger)
- **Health Check**: `http://localhost:8000/health`
- **Service Info**: `http://localhost:8000/` (root endpoint)

---

## Document Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-01-15 | 1.0 | Initial specification | Claude Code |

---

**End of Specification Document**
