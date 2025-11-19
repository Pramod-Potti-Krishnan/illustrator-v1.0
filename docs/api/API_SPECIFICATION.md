# Illustrator Service v1.0 - API Specification

> **⚠️ UPDATED (November 17, 2025) - Template Conversion Complete**
> This document has been updated to reflect the template conversion to L25-compatible HTML fragments.
> **All templates now return inline-styled HTML fragments (no DOCTYPE, no wrappers) ready for Layout Service integration.**
> **Currently Supported**: Concentric Circles, Pyramid, Funnel - all with LLM-powered content generation
> **Output Format**: L25-compatible HTML fragments with inline styles

## Executive Summary

This document defines the complete REST API specification for the Illustrator Service v1.0, a FastAPI-based microservice providing professional PowerPoint illustrations through **LLM-powered content generation using pre-built, human-validated templates**. The service generates content using Gemini, fills templates with the generated data, and returns **L25-compatible HTML fragments** with inline styles—no post-processing required.

**Currently Supported Illustrations**:
- ✅ **Concentric Circles** (3-5 circles) - LLM-powered content generation, L25-ready fragments
- ✅ **Pyramid** (3-6 levels) - LLM-powered content generation, L25-ready fragments
- ✅ **Funnel** (3-5 stages) - LLM-powered content generation, L25-ready fragments with JavaScript

**Base URL**: `https://illustrator-v10-production.up.railway.app` (production)
**API Version**: v1.0
**Authentication**: GCP credentials required for LLM generation endpoints
**Content Type**: `application/json`
**Output Format**: L25-compatible HTML fragments (inline styles, no DOCTYPE/wrappers)

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [LLM-Powered Illustration Endpoints](#2-llm-powered-illustration-endpoints)
   - 2.1 [Concentric Circles Generation](#21-concentric-circles-generation)
   - 2.2 [Pyramid Generation](#22-pyramid-generation)
   - 2.3 [Funnel Generation](#23-funnel-generation)
3. [Utility Endpoints](#3-utility-endpoints)
   - 3.1 [Service Information](#31-service-information)
   - 3.2 [Health Check](#32-health-check)
   - 3.3 [List Illustrations](#33-list-illustrations)
   - 3.4 [List Themes](#34-list-themes)
   - 3.5 [List Sizes](#35-list-sizes)
4. [Request/Response Models](#4-requestresponse-models)
5. [Error Handling](#5-error-handling)
6. [Integration Examples](#6-integration-examples)
7. [L25 Integration Guide](#7-l25-integration-guide)

---

## 1. API Overview

### 1.0 How the Service Works

**Modern Workflow**: This service combines **LLM-powered content generation** with **pre-built, human-validated HTML templates**. At runtime, the service:

1. **Receives topic/context** from the user
2. **Generates contextual content** using Gemini LLM (labels, descriptions, bullets)
3. **Validates character limits** to ensure content fits layout constraints
4. **Loads template** from disk with inline styles (e.g., `templates/concentric_circles/3.html`)
5. **Fills placeholders** with generated content (e.g., `{{circle_1_label}}` → "IaaS")
6. **Returns L25-compatible HTML fragment** with inline styles—no DOCTYPE, no wrappers

**Key Innovation**: **L25-Compatible Output** - All HTML is returned as fragments with inline styles, ready for direct use in Layout Service without any post-processing.

**Template Format**:
- ❌ Before: Complete HTML documents (`<!DOCTYPE html><html><head><style>...</style></head><body>...</body></html>`)
- ✅ Now: Pure HTML fragments (`<div class="container" style="margin: 0 auto; padding: 20px;">...</div>`)

**Character Validation**: Every generated field is validated against character limits to ensure perfect fit within layout constraints.

### 1.1 Endpoint Summary

| Endpoint | Method | Purpose | Response Time (P95) |
|----------|--------|---------|---------------------|
| `/` | GET | Service information and API overview | <100ms |
| `/health` | GET | Health check and status | <100ms |
| `/v1.0/illustrations` | GET | List all supported illustration types | <200ms |
| `/v1.0/concentric_circles/generate` | POST | **LLM-powered concentric circles generation** | <3000ms |
| `/v1.0/pyramid/generate` | POST | **LLM-powered pyramid generation** | <3000ms |
| `/v1.0/funnel/generate` | POST | **LLM-powered funnel generation** | <3000ms |
| `/v1.0/themes` | GET | List available color themes | <100ms |
| `/v1.0/sizes` | GET | List size presets | <100ms |

**Note**: All LLM generation endpoints require GCP credentials to be configured in Railway environment variables.

### 1.2 API Versioning

**Current Version**: v1.0
**Version Strategy**: URL-based versioning (`/v1.0/`, `/v2.0/`, etc.)
**Deprecation Policy**: 6 months notice before deprecating versions

### 1.3 Rate Limits

**Per IP Address**:
- LLM generation endpoints: 20 requests/minute
- Utility endpoints: 200 requests/minute

**Response Headers**:
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 18
X-RateLimit-Reset: 1679529600
```

---

## 2. LLM-Powered Illustration Endpoints

All illustration generation endpoints use Gemini LLM to generate contextual, relevant content based on the topic and context you provide. The service validates character limits, fills templates, and returns **L25-compatible HTML fragments** ready for direct integration with Layout Service.

---

### 2.1 Concentric Circles Generation

**Endpoint**: `POST /v1.0/concentric_circles/generate`

**Description**: Generate a concentric circles diagram with 3-5 circles using LLM-powered content generation. Returns an L25-compatible HTML fragment with inline styles.

**Request Body**:
```json
{
  "num_circles": 3,
  "topic": "Cloud Infrastructure Layers",
  "context": "Enterprise cloud architecture with IaaS, PaaS, and SaaS layers",
  "presentation_id": "pres-123",
  "slide_id": "slide-456",
  "slide_number": 5,
  "theme": "professional",
  "size": "medium"
}
```

**Request Schema**:
```typescript
{
  num_circles: number,          // Required: 3-5 circles
  topic: string,                // Required: Main topic for content generation
  context?: string,             // Optional: Additional context for LLM
  presentation_id?: string,     // Optional: For tracking
  slide_id?: string,            // Optional: For tracking
  slide_number?: number,        // Optional: For tracking
  theme?: string,               // Optional: "professional" (default), "minimal"
  size?: string                 // Optional: "small", "medium" (default), "large"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "html": "<div class=\"concentric-container\" style=\"margin: 0 auto; padding: 20px; box-sizing: border-box; display: flex; gap: 40px; max-width: 1200px; align-items: center\"><div class=\"circles-wrapper\" style=\"flex: 1; position: relative; height: 600px;\">...</div></div>",
  "metadata": {
    "illustration_type": "concentric_circles",
    "num_circles": 3,
    "variant": "3",
    "theme": "professional",
    "size": "medium",
    "template_path": "templates/concentric_circles/3.html",
    "has_javascript": false
  },
  "generated_content": {
    "circle_1_label": "IaaS",
    "circle_2_label": "PaaS",
    "circle_3_label": "SaaS",
    "legend_1_bullet_1": "Virtual machines and compute resources",
    "legend_1_bullet_2": "Storage and networking infrastructure",
    "legend_2_bullet_1": "Application deployment platforms",
    "legend_2_bullet_2": "Development tools and frameworks",
    "legend_3_bullet_1": "Ready-to-use software applications",
    "legend_3_bullet_2": "No infrastructure management required"
  },
  "character_counts": {
    "circle_1_label": 4,
    "circle_2_label": 4,
    "circle_3_label": 4,
    "legend_1_bullet_1": 37,
    "legend_1_bullet_2": 33
  },
  "validation": {
    "passed": true,
    "all_within_limits": true,
    "details": {
      "circle_1_label": {"limit": 30, "actual": 4, "within_limit": true},
      "circle_2_label": {"limit": 30, "actual": 4, "within_limit": true}
    }
  }
}
```

**Key Response Fields**:
- `success`: Boolean indicating generation success
- `html`: **L25-compatible HTML fragment** (no DOCTYPE, inline styles) - ready for `rich_content` field
- `metadata`: Template and configuration information
- `generated_content`: All LLM-generated text content
- `character_counts`: Character count for each field
- `validation`: Validation results showing all fields meet character limits

**Example cURL**:
```bash
curl -X POST "https://illustrator-v10-production.up.railway.app/v1.0/concentric_circles/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_circles": 3,
    "topic": "Market Segmentation Strategy",
    "context": "Enterprise B2B segmentation with three key market tiers",
    "presentation_id": "demo-001",
    "slide_id": "slide-05"
  }'
```

**Character Limits** (3 circles):
- Circle labels: 30 characters each
- Legend bullets: 80 characters each (2 bullets per circle)

**Character Limits** (4 circles):
- Circle labels: 25 characters each
- Legend bullets: 70 characters each (2 bullets per circle)

**Character Limits** (5 circles):
- Circle labels: 20 characters each
- Legend bullets: 60 characters each (2 bullets per circle)

---

### 2.2 Pyramid Generation

**Endpoint**: `POST /v1.0/pyramid/generate`

**Description**: Generate a pyramid diagram with 3-6 levels using LLM-powered content generation. Returns an L25-compatible HTML fragment with inline styles.

**Request Body**:
```json
{
  "num_levels": 4,
  "topic": "Business Growth Strategy",
  "context": "Strategic framework for scaling a SaaS company from startup to enterprise",
  "presentation_id": "pres-123",
  "slide_id": "slide-457",
  "slide_number": 6,
  "theme": "professional",
  "size": "medium"
}
```

**Request Schema**:
```typescript
{
  num_levels: number,           // Required: 3-6 levels
  topic: string,                // Required: Main topic for content generation
  context?: string,             // Optional: Additional context for LLM
  presentation_id?: string,     // Optional: For tracking
  slide_id?: string,            // Optional: For tracking
  slide_number?: number,        // Optional: For tracking
  theme?: string,               // Optional: "professional" (default), "minimal"
  size?: string                 // Optional: "small", "medium" (default), "large"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "html": "<div class=\"pyramid-container\" style=\"margin: 0 auto; padding: 20px; max-width: 1200px; box-sizing: border-box;\"><div class=\"pyramid\" style=\"position: relative; width: 100%; height: 600px;\">...</div></div>",
  "metadata": {
    "illustration_type": "pyramid",
    "num_levels": 4,
    "variant": "4",
    "theme": "professional",
    "size": "medium",
    "template_path": "templates/pyramid/4.html",
    "has_javascript": false
  },
  "generated_content": {
    "level_1_label": "Foundation",
    "level_1_description": "Build strong <strong>operational processes</strong> and team culture",
    "level_2_label": "Growth",
    "level_2_description": "Scale customer acquisition and <strong>revenue streams</strong>",
    "level_3_label": "Expansion",
    "level_3_description": "Enter new markets and develop <strong>strategic partnerships</strong>",
    "level_4_label": "Leadership",
    "level_4_description": "Achieve market dominance through <strong>innovation</strong>"
  },
  "character_counts": {
    "level_1_label": 10,
    "level_1_description": 61,
    "level_2_label": 6,
    "level_2_description": 56
  },
  "validation": {
    "passed": true,
    "all_within_limits": true,
    "details": {
      "level_1_label": {"limit": 25, "actual": 10, "within_limit": true},
      "level_1_description": {"limit": 100, "actual": 61, "within_limit": true}
    }
  }
}
```

**Example cURL**:
```bash
curl -X POST "https://illustrator-v10-production.up.railway.app/v1.0/pyramid/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_levels": 4,
    "topic": "Organizational Hierarchy",
    "context": "Corporate structure from executives to operations teams",
    "presentation_id": "corp-001",
    "slide_id": "slide-12"
  }'
```

**Character Limits** (all pyramid variants):
- Level labels: 25 characters each
- Level descriptions: 100 characters each (can include `<strong>` tags for emphasis)

**Note on HTML in Descriptions**: The LLM can use `<strong>` tags to emphasize key phrases in level descriptions. These are rendered correctly in the final HTML.

---

### 2.3 Funnel Generation

**Endpoint**: `POST /v1.0/funnel/generate`

**Description**: Generate a funnel diagram with 3-5 stages using LLM-powered content generation. Returns an L25-compatible HTML fragment with inline styles **and JavaScript** for interactive stage highlighting.

**Request Body**:
```json
{
  "num_stages": 4,
  "topic": "Sales Pipeline",
  "context": "B2B enterprise sales process from lead generation to closing",
  "presentation_id": "pres-123",
  "slide_id": "slide-458",
  "slide_number": 7,
  "theme": "professional",
  "size": "medium"
}
```

**Request Schema**:
```typescript
{
  num_stages: number,           // Required: 3-5 stages
  topic: string,                // Required: Main topic for content generation
  context?: string,             // Optional: Additional context for LLM
  presentation_id?: string,     // Optional: For tracking
  slide_id?: string,            // Optional: For tracking
  slide_number?: number,        // Optional: For tracking
  theme?: string,               // Optional: "professional" (default), "minimal"
  size?: string                 // Optional: "small", "medium" (default), "large"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "html": "<div class=\"funnel-container\" style=\"margin: 0 auto; padding: 20px; max-width: 1200px;\"><div class=\"funnel\" style=\"position: relative; width: 100%; height: 700px;\">...</div><script>/* Interactive JavaScript for click handlers */</script></div>",
  "metadata": {
    "illustration_type": "funnel",
    "num_stages": 4,
    "variant": "4",
    "theme": "professional",
    "size": "medium",
    "template_path": "templates/funnel/4.html",
    "has_javascript": true
  },
  "generated_content": {
    "stage_1_name": "Awareness",
    "stage_1_bullet_1": "Generate <strong>qualified leads</strong> through targeted campaigns",
    "stage_1_bullet_2": "Build brand recognition in target market",
    "stage_2_name": "Interest",
    "stage_2_bullet_1": "Nurture prospects with <strong>relevant content</strong>",
    "stage_2_bullet_2": "Demonstrate clear value proposition",
    "stage_3_name": "Decision",
    "stage_3_bullet_1": "Present customized <strong>solution proposals</strong>",
    "stage_3_bullet_2": "Address objections and concerns",
    "stage_4_name": "Action",
    "stage_4_bullet_1": "Close deals with <strong>favorable terms</strong>",
    "stage_4_bullet_2": "Onboard new customers successfully"
  },
  "character_counts": {
    "stage_1_name": 9,
    "stage_1_bullet_1": 63,
    "stage_1_bullet_2": 39
  },
  "validation": {
    "passed": true,
    "all_within_limits": true,
    "details": {
      "stage_1_name": {"limit": 20, "actual": 9, "within_limit": true},
      "stage_1_bullet_1": {"limit": 100, "actual": 63, "within_limit": true}
    }
  }
}
```

**Example cURL**:
```bash
curl -X POST "https://illustrator-v10-production.up.railway.app/v1.0/funnel/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_stages": 4,
    "topic": "Customer Conversion Process",
    "context": "E-commerce funnel from visitor to customer",
    "presentation_id": "ecom-001",
    "slide_id": "slide-08"
  }'
```

**Character Limits** (all funnel variants):
- Stage names: 20 characters each
- Stage bullets: 100 characters each (2 bullets per stage, can include `<strong>` tags)

**Interactive Features**:
- The funnel template includes JavaScript for click interactions
- Users can click on funnel stages to highlight them
- JavaScript is embedded within the HTML fragment (`<script>` tag at end)
- The JavaScript is self-contained and requires no external dependencies

**Note on JavaScript**: The funnel templates include inline JavaScript for interactivity. This is preserved in the fragment and will work correctly when rendered in the Layout Service.

---

## 3. Utility Endpoints

These endpoints provide service information and configuration details.

---

### 3.1 Service Information

**Endpoint**: `GET /`

**Description**: Get service overview, version, and available endpoints.

**Response** (200 OK):
```json
{
  "service": "Illustrator Service",
  "version": "1.0.0",
  "description": "LLM-powered illustration generation with L25-compatible HTML fragments",
  "endpoints": {
    "concentric_circles": "POST /v1.0/concentric_circles/generate",
    "pyramid": "POST /v1.0/pyramid/generate",
    "funnel": "POST /v1.0/funnel/generate",
    "list_illustrations": "GET /v1.0/illustrations",
    "list_themes": "GET /v1.0/themes",
    "list_sizes": "GET /v1.0/sizes",
    "health_check": "GET /health"
  },
  "features": {
    "total_illustrations": 3,
    "llm_powered": true,
    "l25_compatible": true,
    "inline_styles": true,
    "themes": 2,
    "size_presets": 3
  },
  "documentation": "https://illustrator-v10-production.up.railway.app/docs"
}
```

**Example cURL**:
```bash
curl https://illustrator-v10-production.up.railway.app/
```

---

### 3.2 Health Check

**Endpoint**: `GET /health`

**Description**: Service health and status check.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3456789,
  "gemini": {
    "status": "connected",
    "model_concentric_circles": "gemini-2.5-flash-lite",
    "model_pyramid": "gemini-2.5-flash-lite",
    "model_funnel": "gemini-2.5-flash-lite"
  },
  "templates": {
    "loaded": 17,
    "concentric_circles": 3,
    "pyramid": 6,
    "funnel": 6
  },
  "performance": {
    "avg_generation_time_ms": 2487,
    "p95_generation_time_ms": 2923
  }
}
```

**Response** (503 Service Unavailable) - when unhealthy:
```json
{
  "status": "unhealthy",
  "error": "GCP credentials not configured",
  "details": {
    "gemini": "disconnected",
    "gcp_project_id": "not_set"
  }
}
```

**Example cURL**:
```bash
curl https://illustrator-v10-production.up.railway.app/health
```

---

### 3.3 List Illustrations

**Endpoint**: `GET /v1.0/illustrations`

**Description**: Get catalog of all supported illustration types with variants.

**Response** (200 OK):
```json
{
  "total_count": 3,
  "illustrations": [
    {
      "type": "concentric_circles",
      "name": "Concentric Circles",
      "description": "Nested circular diagram with legend bullets",
      "variants": [3, 4, 5],
      "llm_powered": true,
      "has_javascript": false
    },
    {
      "type": "pyramid",
      "name": "Pyramid Diagram",
      "description": "Hierarchical pyramid with levels and descriptions",
      "variants": [3, 4, 5, 6],
      "llm_powered": true,
      "has_javascript": false
    },
    {
      "type": "funnel",
      "name": "Funnel Diagram",
      "description": "Conversion funnel with interactive stages",
      "variants": [3, 4, 5],
      "llm_powered": true,
      "has_javascript": true
    }
  ]
}
```

**Example cURL**:
```bash
curl https://illustrator-v10-production.up.railway.app/v1.0/illustrations
```

---

### 3.4 List Themes

**Endpoint**: `GET /v1.0/themes`

**Description**: Get all available color themes with palette details.

**Response** (200 OK):
```json
{
  "themes": [
    {
      "name": "professional",
      "description": "Corporate and professional color scheme",
      "palette": {
        "primary": "#0066CC",
        "secondary": "#FF6B35",
        "background": "#FFFFFF",
        "text": "#1A1A1A"
      }
    },
    {
      "name": "minimal",
      "description": "Clean and understated design",
      "palette": {
        "primary": "#2C3E50",
        "secondary": "#95A5A6",
        "background": "#FFFFFF",
        "text": "#34495E"
      }
    }
  ]
}
```

**Example cURL**:
```bash
curl https://illustrator-v10-production.up.railway.app/v1.0/themes
```

---

### 3.5 List Sizes

**Endpoint**: `GET /v1.0/sizes`

**Description**: Get all predefined size presets.

**Response** (200 OK):
```json
{
  "presets": [
    {
      "name": "small",
      "width": 600,
      "height": 400,
      "aspect_ratio": "3:2",
      "use_case": "Thumbnail previews"
    },
    {
      "name": "medium",
      "width": 1200,
      "height": 800,
      "aspect_ratio": "3:2",
      "use_case": "Standard slides (default)"
    },
    {
      "name": "large",
      "width": 1800,
      "height": 720,
      "aspect_ratio": "2.5:1",
      "use_case": "Widescreen presentations"
    }
  ]
}
```

**Example cURL**:
```bash
curl https://illustrator-v10-production.up.railway.app/v1.0/sizes
```

---

## 4. Request/Response Models

### 4.1 Common Request Model

All LLM generation endpoints share this base structure:

```typescript
interface IllustrationRequest {
  // Required
  num_circles?: number;         // For concentric_circles: 3-5
  num_levels?: number;          // For pyramid: 3-6
  num_stages?: number;          // For funnel: 3-5
  topic: string;                // Main topic for LLM generation

  // Optional
  context?: string;             // Additional context for LLM
  presentation_id?: string;     // For tracking
  slide_id?: string;            // For tracking
  slide_number?: number;        // For tracking
  theme?: string;               // "professional" (default) or "minimal"
  size?: string;                // "small", "medium" (default), or "large"
}
```

### 4.2 Common Response Model

All LLM generation endpoints return this structure:

```typescript
interface IllustrationResponse {
  success: boolean;
  html: string;                 // L25-compatible HTML fragment
  metadata: {
    illustration_type: string;
    num_circles?: number;       // For concentric_circles
    num_levels?: number;        // For pyramid
    num_stages?: number;        // For funnel
    variant: string;
    theme: string;
    size: string;
    template_path: string;
    has_javascript: boolean;
  };
  generated_content: Record<string, string>;  // All LLM-generated text
  character_counts: Record<string, number>;   // Character counts
  validation: {
    passed: boolean;
    all_within_limits: boolean;
    details: Record<string, {
      limit: number;
      actual: number;
      within_limit: boolean;
    }>;
  };
}
```

---

## 5. Error Handling

### 5.1 Error Response Format

All errors follow this structure:

```typescript
interface ErrorResponse {
  detail: string | object;      // Error message or validation details
  error_type?: string;          // Optional error category
  timestamp?: string;           // Optional error timestamp
}
```

### 5.2 HTTP Status Codes

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid request parameters |
| 422 | Unprocessable Entity | Validation error (e.g., invalid num_circles) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Content generation failed or server error |
| 503 | Service Unavailable | GCP credentials not configured |

### 5.3 Common Errors

**422 - Invalid Parameter**:
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["body", "num_circles"],
      "msg": "Input should be a valid integer",
      "input": "abc"
    }
  ]
}
```

**500 - Content Generation Failed**:
```json
{
  "detail": "Content generation failed: 403 Permission denied on resource project your-gcp-project-id"
}
```

**503 - GCP Credentials Not Configured**:
```json
{
  "detail": "GCP_PROJECT_ID environment variable must be set"
}
```

---

## 6. Integration Examples

### 6.1 Python Integration (Director Agent v3.4)

```python
import httpx
import asyncio

class IllustratorClient:
    def __init__(self, base_url: str = "https://illustrator-v10-production.up.railway.app"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def generate_concentric_circles(
        self,
        num_circles: int,
        topic: str,
        context: str = None,
        presentation_id: str = None,
        slide_id: str = None
    ) -> dict:
        """Generate concentric circles illustration"""
        request = {
            "num_circles": num_circles,
            "topic": topic,
            "context": context,
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "theme": "professional"
        }

        response = await self.client.post(
            f"{self.base_url}/v1.0/concentric_circles/generate",
            json=request
        )
        response.raise_for_status()
        return response.json()

    async def generate_pyramid(
        self,
        num_levels: int,
        topic: str,
        context: str = None
    ) -> dict:
        """Generate pyramid illustration"""
        request = {
            "num_levels": num_levels,
            "topic": topic,
            "context": context,
            "theme": "professional"
        }

        response = await self.client.post(
            f"{self.base_url}/v1.0/pyramid/generate",
            json=request
        )
        response.raise_for_status()
        return response.json()

# Usage example
async def main():
    client = IllustratorClient()

    # Generate concentric circles
    circles_result = await client.generate_concentric_circles(
        num_circles=3,
        topic="Cloud Infrastructure Layers",
        context="Enterprise cloud architecture"
    )

    # Use directly in L25 Layout Service
    layout_payload = {
        "layout_type": "L25",
        "rich_content": circles_result["html"]  # ✅ No post-processing needed!
    }

asyncio.run(main())
```

### 6.2 cURL Examples

**Generate Concentric Circles**:
```bash
curl -X POST "https://illustrator-v10-production.up.railway.app/v1.0/concentric_circles/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_circles": 3,
    "topic": "Market Segmentation",
    "context": "Enterprise B2B market analysis"
  }'
```

**Generate Pyramid**:
```bash
curl -X POST "https://illustrator-v10-production.up.railway.app/v1.0/pyramid/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_levels": 4,
    "topic": "Organizational Structure"
  }'
```

**Generate Funnel**:
```bash
curl -X POST "https://illustrator-v10-production.up.railway.app/v1.0/funnel/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "num_stages": 4,
    "topic": "Sales Pipeline"
  }'
```

---

## 7. L25 Integration Guide

### 7.1 Why L25-Compatible Fragments?

**Before Template Conversion**:
```python
# ❌ OLD: Complex post-processing required
response = await illustrator_service.generate(...)

# Extract body content
body_html = extract_body_content(response.html)

# Inline CSS
fragment = inline_css(body_html)

# Remove wrappers
clean_fragment = remove_wrappers(fragment)

# Finally use in L25
layout_payload = {"rich_content": clean_fragment}
```

**After Template Conversion**:
```python
# ✅ NEW: Direct use, one line!
response = await illustrator_service.generate(...)

# Use directly - it's already a fragment!
layout_payload = {"rich_content": response["html"]}
```

### 7.2 Integration with Layout Service

The Illustrator Service now returns HTML that can be used **directly** in Layout Service L25's `rich_content` field:

```python
# Director Agent v3.4 Integration
async def create_slide_with_illustration(
    layout_service,
    illustrator_service,
    presentation_id: str,
    slide_id: str
):
    # Step 1: Generate illustration
    illustration = await illustrator_service.generate_concentric_circles(
        num_circles=3,
        topic="Market Segmentation",
        presentation_id=presentation_id,
        slide_id=slide_id
    )

    # Step 2: Use directly in L25 layout
    layout_request = {
        "layout_type": "L25",
        "rich_content": illustration["html"],  # ✅ Fragment ready!
        "metadata": illustration["metadata"]
    }

    # Step 3: Generate slide
    slide = await layout_service.generate_slide(layout_request)

    return slide
```

### 7.3 Benefits for Director Integration

**Simplified Integration**:
- ✅ No CSS extraction needed
- ✅ No wrapper removal needed
- ✅ No HTML manipulation needed
- ✅ Direct use: `rich_content = response.html`

**Fewer Failure Points**:
- 🚀 3 fewer processing steps
- 🚀 Simpler error handling
- 🚀 Faster execution
- 🚀 More reliable

**Better Performance**:
- ⚡ Reduced latency (no post-processing)
- ⚡ Lower complexity
- ⚡ Less code to maintain

---

## 8. Railway Deployment

### 8.1 Current Status

**URL**: https://illustrator-v10-production.up.railway.app

**Working Endpoints**:
- ✅ `GET /` - Service info
- ✅ `GET /health` - Health check
- ✅ `GET /v1.0/illustrations` - List illustrations
- ✅ `GET /v1.0/themes` - List themes
- ✅ `GET /v1.0/sizes` - List sizes

**LLM Endpoints** (require GCP credentials):
- ⏳ `POST /v1.0/concentric_circles/generate` - Needs GCP config
- ⏳ `POST /v1.0/pyramid/generate` - Needs GCP config
- ⏳ `POST /v1.0/funnel/generate` - Needs GCP config

### 8.2 Required Environment Variables

In Railway, set these environment variables:

```bash
# GCP Configuration (REQUIRED)
GCP_PROJECT_ID=your-actual-gcp-project-id
GCP_CREDENTIALS_JSON={"type":"service_account",...}  # Paste entire JSON

# LLM Models (REQUIRED)
LLM_PYRAMID=gemini-2.5-flash-lite
LLM_FUNNEL=gemini-2.5-flash-lite
LLM_CONCENTRIC_CIRCLES=gemini-2.5-flash-lite

# Vertex AI Region (OPTIONAL, defaults to us-central1)
GEMINI_LOCATION=us-central1
```

**See**: `DIRECTOR_INTEGRATION_SUMMARY.md` for detailed Railway configuration guide.

---

**End of API Specification**

**Last Updated**: November 17, 2025
**Version**: 1.0.0
**Service URL**: https://illustrator-v10-production.up.railway.app
**GitHub**: https://github.com/Pramod-Potti-Krishnan/illustrator-v1.0
