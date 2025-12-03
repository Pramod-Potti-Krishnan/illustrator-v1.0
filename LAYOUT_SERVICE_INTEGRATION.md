# Layout Service Integration - Illustrator Service v1.1

## Overview

This document describes the unified infographic generation endpoint created for Layout Service integration. The endpoint supports **14 infographic types** with a dual output strategy: HTML templates for 6 types and dynamic SVG generation via Gemini 2.5 Pro for 8 types.

---

## Quick Start

### Endpoint URL
```
POST /api/ai/illustrator/generate
```

### Base URL (Local Development)
```
http://localhost:8000/api/ai/illustrator/generate
```

### Example Request
```bash
curl -X POST "http://localhost:8000/api/ai/illustrator/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show our company journey from startup to IPO",
    "type": "timeline",
    "presentationId": "pres-123",
    "slideId": "slide-456",
    "elementId": "elem-789",
    "constraints": {
      "gridWidth": 8,
      "gridHeight": 4
    }
  }'
```

---

## Supported Infographic Types

### Template-Based (HTML Output) - 6 Types
| Type | Min Grid | Aspect Ratio | Items |
|------|----------|--------------|-------|
| `pyramid` | 6x4 | 3:2 (fixed) | 3-6 |
| `funnel` | 6x4 | 3:2 (fixed) | 3-6 |
| `concentric_circles` | 6x6 | 1:1 (fixed) | 2-5 |
| `concept_spread` | 8x4 | 2:1 (fixed) | 3-6 |
| `venn` | 6x4 | 4:3 (fixed) | 2-4 |
| `comparison` | 8x4 | 2:1 (fixed) | 2 |

### Dynamic SVG (Gemini 2.5 Pro) - 8 Types
| Type | Min Grid | Aspect Ratio | Items |
|------|----------|--------------|-------|
| `timeline` | 8x3 | wide (flexible) | 3-10 |
| `process` | 6x3 | flexible | 3-8 |
| `statistics` | 4x3 | flexible | 2-8 |
| `hierarchy` | 6x4 | flexible | 3-15 |
| `list` | 4x4 | portrait (flexible) | 3-12 |
| `cycle` | 6x6 | 1:1 (fixed) | 3-8 |
| `matrix` | 6x6 | 1:1 (fixed) | 4 |
| `roadmap` | 8x4 | wide (flexible) | 3-8 |

---

## API Reference

### POST /api/ai/illustrator/generate

Generate an infographic based on the provided prompt and constraints.

#### Request Body

```typescript
{
  // Required fields
  "prompt": string,           // Content description (e.g., "Show our 5-year journey")
  "type": InfographicType,    // One of 14 supported types
  "presentationId": string,   // Parent presentation ID
  "slideId": string,          // Target slide ID
  "elementId": string,        // Target element ID

  // Required constraints
  "constraints": {
    "gridWidth": number,      // Width in grid units (1-12)
    "gridHeight": number      // Height in grid units (1-8)
  },

  // Optional context
  "context": {
    "presentationTitle": string,
    "slideTitle": string,
    "slideContent": string,
    "presentationTheme": string,
    "brandColors": string[]
  },

  // Optional style options
  "style": {
    "colorScheme": "professional" | "vibrant" | "minimal" | "corporate",
    "iconStyle": "emoji" | "outlined" | "filled" | "none",
    "density": "compact" | "balanced" | "spacious",
    "orientation": "horizontal" | "vertical" | "auto"
  },

  // Optional content options
  "contentOptions": {
    "itemCount": number,      // Override default item count
    "includeIcons": boolean,
    "includeDescriptions": boolean
  }
}
```

#### Response Body

```typescript
{
  "success": boolean,
  "data": {
    "generationId": string,
    "rendered": {
      "svg": string,          // Complete SVG content
      "html": string          // HTML-wrapped version
    },
    "infographicData": {
      "items": [
        {
          "id": string,
          "title": string,
          "description": string | null,
          "icon": string | null,
          "value": string | null,
          "color": string | null,
          "position": number
        }
      ],
      "metadata": object
    },
    "metadata": {
      "type": string,
      "itemCount": number,
      "dimensions": {
        "width": number,
        "height": number
      },
      "colorPalette": string[]
    },
    "editInfo": {
      "editableItems": string[],
      "reorderableItems": string[],
      "maxItems": number
    }
  },
  "presentationId": string,
  "slideId": string,
  "elementId": string,
  "generationTimeMs": number,
  "error": {                  // Only present if success=false
    "code": string,
    "message": string,
    "retryable": boolean,
    "suggestion": string | null
  }
}
```

### GET /api/ai/illustrator/types

List all supported infographic types with their constraints.

#### Response
```typescript
{
  "total_types": 14,
  "template_types": ["pyramid", "funnel", ...],
  "svg_types": ["timeline", "process", ...],
  "grid_unit_pixels": 150,
  "types": {
    "pyramid": {
      "description": string,
      "min_grid": [6, 4],
      "max_grid": [12, 8],
      "aspect_ratio_type": "fixed",
      "aspect_ratio_value": "3:2",
      "output_mode": "html",
      "item_limits": { "min": 3, "max": 6, "default": 4 }
    },
    // ... other types
  }
}
```

### GET /api/ai/illustrator/types/{type}

Get detailed constraints for a specific infographic type.

### GET /api/ai/illustrator/health

Health check endpoint.

---

## Layout Service Integration Guide

### Integration Blurb for Layout Service Orchestrator

```javascript
/**
 * Illustrator Service Integration
 *
 * The Illustrator Service provides AI-powered infographic generation
 * with support for 14 infographic types. It uses a dual-output strategy:
 * - HTML templates for structured types (pyramid, funnel, etc.)
 * - Dynamic SVG via Gemini 2.5 Pro for flexible types (timeline, process, etc.)
 *
 * Endpoint: POST /api/ai/illustrator/generate
 * Base URL: http://localhost:8000 (or configured service URL)
 *
 * Grid System:
 * - Canvas: 12x8 grid (1800x1200 pixels at 150px/unit)
 * - Each type has minimum grid requirements
 * - Aspect ratios are enforced per type
 *
 * Color Schemes: professional, vibrant, minimal, corporate
 * Icon Styles: emoji (recommended), outlined, filled, none
 */
```

### Sample Integration Code

```javascript
// Layout Service Orchestrator Integration

const ILLUSTRATOR_SERVICE_URL = process.env.ILLUSTRATOR_SERVICE_URL || 'http://localhost:8000';

async function generateInfographic(params) {
  const {
    prompt,
    type,
    presentationId,
    slideId,
    elementId,
    gridWidth,
    gridHeight,
    context = {},
    style = {}
  } = params;

  const response = await fetch(`${ILLUSTRATOR_SERVICE_URL}/api/ai/illustrator/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      type,
      presentationId,
      slideId,
      elementId,
      constraints: {
        gridWidth,
        gridHeight
      },
      context: {
        presentationTitle: context.presentationTitle,
        slideTitle: context.slideTitle,
        slideContent: context.slideContent,
        presentationTheme: context.theme,
        brandColors: context.brandColors
      },
      style: {
        colorScheme: style.colorScheme || 'professional',
        iconStyle: style.iconStyle || 'emoji',
        density: style.density || 'balanced',
        orientation: style.orientation || 'auto'
      }
    })
  });

  const result = await response.json();

  if (!result.success) {
    throw new Error(`Illustrator generation failed: ${result.error.message}`);
  }

  return {
    svg: result.data.rendered.svg,
    html: result.data.rendered.html,
    items: result.data.infographicData.items,
    metadata: result.data.metadata,
    generationId: result.data.generationId
  };
}

// Usage example
const infographic = await generateInfographic({
  prompt: "Show the 5-step software development lifecycle",
  type: "process",
  presentationId: "pres-abc123",
  slideId: "slide-def456",
  elementId: "elem-ghi789",
  gridWidth: 8,
  gridHeight: 4,
  context: {
    presentationTitle: "Engineering Best Practices",
    theme: "corporate"
  },
  style: {
    colorScheme: "professional",
    iconStyle: "emoji"
  }
});

console.log(infographic.svg); // Use SVG content
```

### Type Selection Logic

```javascript
function selectInfographicType(userIntent, constraints) {
  const typeMapping = {
    // Hierarchical data
    'hierarchy': ['pyramid', 'hierarchy'],
    'levels': ['pyramid', 'hierarchy'],
    'organization': ['hierarchy'],

    // Sequential/Process
    'steps': ['process', 'timeline'],
    'process': ['process'],
    'flow': ['process', 'funnel'],
    'journey': ['timeline', 'roadmap'],
    'timeline': ['timeline'],
    'roadmap': ['roadmap'],

    // Relationships
    'overlap': ['venn'],
    'intersection': ['venn'],
    'compare': ['comparison'],
    'versus': ['comparison'],

    // Cyclical
    'cycle': ['cycle'],
    'recurring': ['cycle'],
    'continuous': ['cycle'],

    // Data
    'statistics': ['statistics'],
    'numbers': ['statistics'],
    'metrics': ['statistics'],

    // Lists
    'list': ['list'],
    'items': ['list'],
    'points': ['list'],

    // Complex
    'matrix': ['matrix'],
    'quadrant': ['matrix'],

    // Core concepts
    'funnel': ['funnel'],
    'conversion': ['funnel'],
    'concentric': ['concentric_circles'],
    'layers': ['concentric_circles'],
    'spread': ['concept_spread']
  };

  // Find best matching type based on keywords in userIntent
  for (const [keyword, types] of Object.entries(typeMapping)) {
    if (userIntent.toLowerCase().includes(keyword)) {
      // Return first type that fits constraints
      for (const type of types) {
        if (fitsConstraints(type, constraints)) {
          return type;
        }
      }
    }
  }

  return 'process'; // Default fallback
}
```

---

## Files Created/Modified

### New Files Created

| File Path | Description |
|-----------|-------------|
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/models/__init__.py` | Model exports |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/models/layout_service_request.py` | Request models (InfographicGenerateRequest, GridConstraints, etc.) |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/models/layout_service_response.py` | Response models (InfographicGenerateResponse, ResponseData, etc.) |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/core/type_constraints.py` | Type constraints (INFOGRAPHIC_TYPE_CONSTRAINTS, COLOR_SCHEMES) |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/core/type_router.py` | Generator routing logic |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/core/svg_builder.py` | SVG utility functions |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/generators/base_generator.py` | Abstract base generator class |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/generators/template_generator.py` | HTML template generator (adapts existing generators) |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/generators/svg_generator.py` | Dynamic SVG generator |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/llm_services/svg_generation_service.py` | Gemini 2.5 Pro SVG generation service |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/app/api_routes/layout_service_routes.py` | Layout Service endpoint routes |

### Modified Files

| File Path | Changes |
|-----------|---------|
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/main.py` | Added layout_service_router import and registration |
| `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/illustrator/v1.0/.env.example` | Added LLM_SVG_GENERATOR configuration |

---

## Architecture Overview

```
Request Flow:
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Layout Service │────▶│ /api/ai/illustrator/ │────▶│   Type Router   │
│   Orchestrator  │     │      generate        │     │                 │
└─────────────────┘     └──────────────────────┘     └────────┬────────┘
                                                              │
                        ┌─────────────────────────────────────┴───────┐
                        │                                             │
                        ▼                                             ▼
              ┌─────────────────┐                         ┌───────────────────┐
              │ Template Types  │                         │   SVG Types       │
              │ (6 types)       │                         │   (8 types)       │
              └────────┬────────┘                         └─────────┬─────────┘
                       │                                            │
                       ▼                                            ▼
              ┌─────────────────┐                         ┌───────────────────┐
              │ Template        │                         │ SVG Generator     │
              │ Generator       │                         │                   │
              └────────┬────────┘                         └─────────┬─────────┘
                       │                                            │
                       ▼                                            ▼
              ┌─────────────────┐                         ┌───────────────────┐
              │ Existing        │                         │ Gemini 2.5 Pro    │
              │ Generators      │                         │ SVG Service       │
              │ (pyramid,       │                         │                   │
              │  funnel, etc.)  │                         │                   │
              └─────────────────┘                         └───────────────────┘
```

---

## Configuration

### Required Environment Variables

```bash
# GCP/Vertex AI Configuration
GCP_PROJECT_ID=your-project-id

# Gemini Configuration
GEMINI_LOCATION=us-central1

# SVG Generation Model (for dynamic types)
LLM_SVG_GENERATOR=gemini-2.5-pro-preview-05-06

# Template-based generators (existing)
LLM_PYRAMID=gemini-2.0-flash-exp
LLM_FUNNEL=gemini-2.0-flash-exp
LLM_CONCENTRIC_CIRCLES=gemini-2.0-flash-exp
LLM_CONCEPT_SPREAD=gemini-2.0-flash-exp
```

### Grid System

- **Grid Canvas**: 12 columns x 8 rows
- **Pixel Size**: 150px per grid unit
- **Maximum Dimensions**: 1800px x 1200px (12x8 grid)
- **Minimum varies by type** (see type table above)

---

## Error Handling

### Error Codes

| Code | Description | Retryable |
|------|-------------|-----------|
| `INVALID_TYPE` | Unknown infographic type | No |
| `CONSTRAINT_VIOLATION` | Grid size doesn't meet requirements | No |
| `GENERATION_FAILED` | LLM generation failed | Yes |
| `SVG_VALIDATION_FAILED` | Generated SVG is invalid | Yes |
| `INTERNAL_ERROR` | Unexpected server error | Yes |
| `INVALID_REQUEST` | Malformed request | No |

### Error Response Example

```json
{
  "success": false,
  "error": {
    "code": "CONSTRAINT_VIOLATION",
    "message": "Grid size 4x4 is too small for timeline. Minimum: 8x3",
    "retryable": false,
    "suggestion": "Increase gridWidth to at least 8 and gridHeight to at least 3"
  },
  "presentationId": "pres-123",
  "slideId": "slide-456",
  "elementId": "elem-789",
  "generationTimeMs": 12
}
```

---

## Testing

### Health Check

```bash
curl http://localhost:8000/api/ai/illustrator/health
```

### List Available Types

```bash
curl http://localhost:8000/api/ai/illustrator/types
```

### Generate Timeline

```bash
curl -X POST "http://localhost:8000/api/ai/illustrator/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show our company milestones from 2020 to 2025",
    "type": "timeline",
    "presentationId": "pres-123",
    "slideId": "slide-456",
    "elementId": "elem-789",
    "constraints": {"gridWidth": 10, "gridHeight": 4},
    "style": {"colorScheme": "professional", "iconStyle": "emoji"}
  }'
```

### Generate Pyramid

```bash
curl -X POST "http://localhost:8000/api/ai/illustrator/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a pyramid showing organizational hierarchy",
    "type": "pyramid",
    "presentationId": "pres-123",
    "slideId": "slide-456",
    "elementId": "elem-789",
    "constraints": {"gridWidth": 6, "gridHeight": 4}
  }'
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Initial | Original illustrator service with pyramid, funnel, concentric_circles, concept_spread |
| 1.1.0 | Current | Added Layout Service integration endpoint with 14 infographic types |

---

## Notes

1. **Venn and Comparison Templates**: These types are defined in constraints but templates need to be created. Currently will return generation errors until templates are added.

2. **Dynamic SVG Types**: Uses Gemini 2.5 Pro for generation. Quality depends on prompt clarity and context provided.

3. **Performance**: Template-based types are faster (~1-2s). SVG types may take 3-8 seconds depending on complexity.

4. **Backward Compatibility**: Original endpoints (`/v1.0/pyramid/generate`, etc.) remain fully functional.
