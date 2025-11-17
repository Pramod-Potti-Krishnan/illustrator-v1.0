# Illustrator Service v1.0 - API Specification

> **⚠️ UPDATED (November 16, 2025)**
> This document has been updated to reflect current supported illustrations.
> **Currently Supported**: Pyramid (approved), Funnel (work in progress)
> **Archived**: 15 illustration types have been archived. See `ARCHIVED_TEMPLATES.md`.

## Executive Summary

This document defines the complete REST API specification for the Illustrator Service v1.0, a FastAPI-based microservice providing professional PowerPoint illustrations through **pre-built, human-validated templates**. The service loads templates, fills them with provided text data, applies theme colors, and returns HTML or PNG. The API follows RESTful principles and integrates seamlessly with Director Agent v3.4 and Text Service v1.2.

**Currently Supported Illustrations**:
- ✅ **Pyramid** (3-6 levels) - Approved, LLM-powered content generation
- 🚧 **Funnel** - Work in progress

**Base URL**: `https://illustrator-service.railway.app` (production)
**API Version**: v1.0
**Authentication**: None required for Phase 1-2 (GCP auth only for custom endpoint in Phase 3)
**Content Type**: `application/json`

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Standard Illustration Endpoints](#2-standard-illustration-endpoints)
3. [Custom Illustration Endpoint](#3-custom-illustration-endpoint)
4. [Utility Endpoints](#4-utility-endpoints)
5. [Request/Response Models](#5-requestresponse-models)
6. [Error Handling](#6-error-handling)
7. [Integration Examples](#7-integration-examples)

---

## 1. API Overview

### 1.0 How the Service Works

**Simple Philosophy**: This service uses **pre-built, human-validated templates** stored as HTML/CSS files with placeholders. At runtime, the service:

1. **Loads template** from disk (e.g., `templates/swot_2x2/base.html`)
2. **Fills placeholders** with your data (e.g., `{strength_1}` → "Strong brand")
3. **Applies theme** colors (e.g., `{theme.primary}` → "#0066CC")
4. **Returns HTML** or converts to PNG

**NOT**: Programmatic generation, complex algorithms, or LLM-generated layouts
**YES**: Simple text substitution in pre-approved templates

**Variants**: Each illustration type has 2-3 approved visual variants (e.g., "base", "rounded", "minimal"). All variants use the same data structure.

### 1.1 Endpoint Summary

| Endpoint | Method | Purpose | Response Time (P95) |
|----------|--------|---------|---------------------|
| `/` | GET | Service info | <100ms |
| `/health` | GET | Health check | <100ms |
| `/v1.0/illustrations` | GET | List supported types (pyramid, funnel) | <200ms |
| `/v1.0/illustration/{type}` | GET | Get illustration details | <200ms |
| `/v1.0/generate` | POST | Generate from template (HTML) | <300ms |
| `/v1.0/pyramid/generate` | POST | **LLM-powered pyramid generation** | <3000ms |
| `/v1.0/themes` | GET | List available themes | <100ms |
| `/v1.0/sizes` | GET | List size presets | <100ms |

**Note**: Archived illustration types (SWOT, BCG Matrix, etc.) are no longer accessible via the API.

### 1.2 API Versioning

**Current Version**: v1.0
**Version Strategy**: URL-based versioning (`/v1.0/`, `/v2.0/`, etc.)
**Deprecation Policy**: 6 months notice before deprecating versions

### 1.3 Rate Limits

**Per IP Address**:
- Standard endpoints: 100 requests/minute
- Custom endpoint: 20 requests/minute
- Utility endpoints: 200 requests/minute

**Response Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1679529600
```

---

## 2. Standard Illustration Endpoints

### 2.1 Generate Standard Illustration

**Endpoint**: `POST /v1.0/generate`

**Description**: Generate an illustration by loading a pre-built template, filling it with provided data, and applying theme colors. Returns HTML or PNG.

**Request Body**:
```json
{
  "illustration_type": "pyramid",
  "variant_id": "4",
  "data": {
    "level_4_label": "Vision",
    "level_4_description": "Long-term strategic objectives and organizational vision",
    "level_3_label": "Strategy",
    "level_3_description": "Strategic planning and resource allocation",
    "level_2_label": "Operations",
    "level_2_description": "Operational management and team coordination",
    "level_1_label": "Execution",
    "level_1_description": "Day-to-day task execution and delivery"
  },
  "theme": "professional",
  "size": "medium",
  "output_format": "html"
}
```

**Request Schema**:
```typescript
{
  illustration_type: string,      // Required: One of 87 illustration types
  variant_id?: string,            // Optional: Template variant ("base", "rounded", "minimal", etc.), defaults to "base"
  data: object,                   // Required: Illustration-specific data
  theme?: string,                 // Optional: "professional" (default), "bold", "minimal", "playful"
  size?: string,                  // Optional: "small", "medium" (default), "large", "custom" (Phase 2)
  custom_size?: [number, number], // Optional: [width, height] if size="custom" (Phase 2 only)
  output_format?: string          // Optional: "html" (default), "png"
}
```

**Response** (200 OK):
```json
{
  "illustration_type": "swot_2x2",
  "variant_id": "base",
  "format": "html",
  "data": "<div class=\"swot-container\" style=\"width: 1200px; height: 800px;\">...</div>",
  "metadata": {
    "width": 1200,
    "height": 800,
    "theme": "professional",
    "rendering_method": "html_css"
  },
  "generation_time_ms": 145
}
```

**Response Schema**:
```typescript
{
  illustration_type: string,
  variant_id: string,          // Which template variant was used
  format: string,              // "html" or "png"
  data: string,                // HTML string or PNG base64 data URL
  metadata: {
    width: number,
    height: number,
    theme: string,
    rendering_method: string   // "html_css" or "svg" (method used for this illustration)
  },
  generation_time_ms: number
}
```

**Example cURL**:
```bash
curl -X POST https://illustrator-service.railway.app/v1.0/generate \
  -H "Content-Type: application/json" \
  -d '{
    "illustration_type": "swot_2x2",
    "variant_id": "base",
    "data": {
      "strengths": ["Strong brand", "Market leader"],
      "weaknesses": ["High costs"],
      "opportunities": ["New markets"],
      "threats": ["Competition"]
    },
    "theme": "professional",
    "output_format": "html"
  }'
```

---

### 2.2 Category 1: Process & Flow Diagrams

#### 2.2.1 Linear Process Flow

**Illustration Type**: `process_flow_3step`, `process_flow_4step`, `process_flow_5step`

**Data Schema**:
```json
{
  "steps": [
    {
      "number": 1,
      "title": "Research",
      "description": "Market analysis and user research"
    },
    {
      "number": 2,
      "title": "Design",
      "description": "Create wireframes and prototypes"
    },
    {
      "number": 3,
      "title": "Build",
      "description": "Develop and test the product"
    }
  ]
}
```

**Example Request**:
```json
{
  "illustration_type": "process_flow_3step",
  "data": {
    "steps": [
      {"number": 1, "title": "Research", "description": "Gather requirements"},
      {"number": 2, "title": "Design", "description": "Create mockups"},
      {"number": 3, "title": "Build", "description": "Implement solution"}
    ]
  },
  "theme": "bold"
}
```

#### 2.2.2 Vertical Flowchart

**Illustration Type**: `flowchart_4step`, `flowchart_6step`

**Data Schema**:
```json
{
  "nodes": [
    {
      "type": "start",
      "label": "Start Process"
    },
    {
      "type": "process",
      "label": "Step 1: Validate Input"
    },
    {
      "type": "decision",
      "label": "Valid?",
      "yes_path": "Continue",
      "no_path": "Error"
    },
    {
      "type": "end",
      "label": "Complete"
    }
  ]
}
```

#### 2.2.3 Circular Process Diagram

**Illustration Type**: `circular_process_4step`, `circular_process_6step`

**Data Schema**:
```json
{
  "center_label": "Continuous Improvement",
  "segments": [
    {"label": "Plan", "description": "Define objectives"},
    {"label": "Do", "description": "Implement changes"},
    {"label": "Check", "description": "Measure results"},
    {"label": "Act", "description": "Standardize or adjust"}
  ]
}
```

#### 2.2.4 Funnel Diagram

**Illustration Type**: `funnel_3stage`, `funnel_4stage`, `funnel_5stage`

**Data Schema**:
```json
{
  "stages": [
    {"label": "Awareness", "value": 10000, "percentage": 100},
    {"label": "Interest", "value": 5000, "percentage": 50},
    {"label": "Consideration", "value": 2000, "percentage": 20},
    {"label": "Conversion", "value": 500, "percentage": 5}
  ]
}
```

#### 2.2.5 Timeline

**Illustration Type**: `timeline_horizontal_5point`, `timeline_horizontal_7point`

**Data Schema**:
```json
{
  "milestones": [
    {"date": "Q1 2024", "label": "Launch MVP", "description": "Initial product release"},
    {"date": "Q2 2024", "label": "User Feedback", "description": "Gather insights"},
    {"date": "Q3 2024", "label": "Version 2.0", "description": "Major update"},
    {"date": "Q4 2024", "label": "Scale", "description": "Expand to new markets"}
  ]
}
```

---

### 2.3 Category 2: Strategic Frameworks & Matrices

#### 2.3.1 SWOT Analysis

**Illustration Type**: `swot_2x2`

**Data Schema**:
```json
{
  "strengths": [
    "Strong brand recognition",
    "Experienced team",
    "Market leader in segment"
  ],
  "weaknesses": [
    "High operational costs",
    "Limited geographic presence"
  ],
  "opportunities": [
    "Emerging markets",
    "Digital transformation",
    "Strategic partnerships"
  ],
  "threats": [
    "Intense competition",
    "Economic uncertainty",
    "Regulatory changes"
  ]
}
```

#### 2.3.2 BCG Matrix

**Illustration Type**: `bcg_matrix`

**Data Schema**:
```json
{
  "products": [
    {
      "name": "Product A",
      "quadrant": "star",
      "market_share": 0.35,
      "market_growth": 0.25
    },
    {
      "name": "Product B",
      "quadrant": "cash_cow",
      "market_share": 0.45,
      "market_growth": 0.05
    },
    {
      "name": "Product C",
      "quadrant": "question_mark",
      "market_share": 0.10,
      "market_growth": 0.30
    },
    {
      "name": "Product D",
      "quadrant": "dog",
      "market_share": 0.08,
      "market_growth": 0.02
    }
  ]
}
```

#### 2.3.3 Ansoff Matrix

**Illustration Type**: `ansoff_matrix`

**Data Schema**:
```json
{
  "market_penetration": {
    "title": "Market Penetration",
    "strategies": ["Increase market share", "Promote existing products"]
  },
  "market_development": {
    "title": "Market Development",
    "strategies": ["Enter new markets", "Target new segments"]
  },
  "product_development": {
    "title": "Product Development",
    "strategies": ["New features", "Product line extensions"]
  },
  "diversification": {
    "title": "Diversification",
    "strategies": ["New products", "New markets"]
  }
}
```

#### 2.3.4 Porter's Five Forces

**Illustration Type**: `porters_five_forces`

**Data Schema**:
```json
{
  "competitive_rivalry": {
    "intensity": "high",
    "factors": ["Many competitors", "Price wars"]
  },
  "supplier_power": {
    "intensity": "medium",
    "factors": ["Limited suppliers", "High switching costs"]
  },
  "buyer_power": {
    "intensity": "high",
    "factors": ["Price sensitive", "Many alternatives"]
  },
  "threat_of_substitutes": {
    "intensity": "medium",
    "factors": ["Alternative solutions available"]
  },
  "threat_of_new_entrants": {
    "intensity": "low",
    "factors": ["High barriers to entry", "Economies of scale"]
  }
}
```

#### 2.3.5 Value Chain

**Illustration Type**: `value_chain`

**Data Schema**:
```json
{
  "primary_activities": [
    {"name": "Inbound Logistics", "description": "Material handling"},
    {"name": "Operations", "description": "Manufacturing"},
    {"name": "Outbound Logistics", "description": "Distribution"},
    {"name": "Marketing & Sales", "description": "Promotion"},
    {"name": "Service", "description": "Customer support"}
  ],
  "support_activities": [
    {"name": "Infrastructure", "description": "Management, finance"},
    {"name": "HR Management", "description": "Recruitment, training"},
    {"name": "Technology", "description": "R&D, automation"},
    {"name": "Procurement", "description": "Purchasing"}
  ]
}
```

---

### 2.4 Category 3: Organizational Charts

#### 2.4.1 Hierarchical Org Chart

**Illustration Type**: `org_chart_hierarchical_3level`

**Data Schema**:
```json
{
  "levels": [
    {
      "level": 1,
      "roles": [{"title": "CEO", "name": "John Smith"}]
    },
    {
      "level": 2,
      "roles": [
        {"title": "CTO", "name": "Jane Doe"},
        {"title": "CFO", "name": "Bob Johnson"},
        {"title": "CMO", "name": "Alice Williams"}
      ]
    },
    {
      "level": 3,
      "roles": [
        {"title": "Engineering Lead", "reports_to": "CTO"},
        {"title": "Product Lead", "reports_to": "CTO"},
        {"title": "Accounting Lead", "reports_to": "CFO"}
      ]
    }
  ]
}
```

#### 2.4.2 Matrix Organization

**Illustration Type**: `org_chart_matrix`

**Data Schema**:
```json
{
  "functional_managers": ["Engineering", "Marketing", "Sales"],
  "product_managers": ["Product A", "Product B", "Product C"],
  "dual_reporting": [
    {
      "employee": "Engineer 1",
      "functional_manager": "Engineering",
      "product_manager": "Product A"
    }
  ]
}
```

---

### 2.5 Category 4: Comparison & Analysis

#### 2.5.1 Venn Diagrams

**Illustration Type**: `venn_2circle`, `venn_3circle`

**Data Schema (2-circle)**:
```json
{
  "circle_1": {
    "label": "Set A",
    "unique_items": ["Item 1", "Item 2"]
  },
  "circle_2": {
    "label": "Set B",
    "unique_items": ["Item 3", "Item 4"]
  },
  "intersection": {
    "items": ["Shared Item 1", "Shared Item 2"]
  }
}
```

**Data Schema (3-circle)**:
```json
{
  "circles": [
    {"label": "A", "unique": ["A1", "A2"]},
    {"label": "B", "unique": ["B1", "B2"]},
    {"label": "C", "unique": ["C1", "C2"]}
  ],
  "intersections": {
    "A_B": ["AB1"],
    "B_C": ["BC1"],
    "A_C": ["AC1"],
    "A_B_C": ["Common"]
  }
}
```

#### 2.5.2 Pros vs Cons

**Illustration Type**: `pros_vs_cons`

**Data Schema**:
```json
{
  "pros": [
    "Cost effective",
    "Easy to implement",
    "Scalable solution"
  ],
  "cons": [
    "Limited features",
    "Longer timeline",
    "Requires training"
  ]
}
```

#### 2.5.3 Before vs After

**Illustration Type**: `before_vs_after`

**Data Schema**:
```json
{
  "before": {
    "title": "Before Implementation",
    "points": [
      "Manual processes",
      "High error rate",
      "Slow turnaround"
    ]
  },
  "after": {
    "title": "After Implementation",
    "points": [
      "Automated workflows",
      "95% accuracy",
      "50% faster"
    ]
  }
}
```

---

### 2.6 Category 5: Data Visualization

#### 2.6.1 Pyramid Diagram

**Illustration Type**: `pyramid_3level`, `pyramid_4level`, `pyramid_5level`

**Data Schema**:
```json
{
  "levels": [
    {"label": "Vision", "description": "Long-term goals", "width_percentage": 30},
    {"label": "Strategy", "description": "3-year plan", "width_percentage": 50},
    {"label": "Tactics", "description": "Annual initiatives", "width_percentage": 70},
    {"label": "Operations", "description": "Daily execution", "width_percentage": 100}
  ]
}
```

#### 2.6.2 Gauge/Meter

**Illustration Type**: `gauge_meter`

**Data Schema**:
```json
{
  "title": "Customer Satisfaction",
  "current_value": 82,
  "min_value": 0,
  "max_value": 100,
  "target_value": 85,
  "zones": [
    {"range": [0, 50], "color": "#DC3545", "label": "Low"},
    {"range": [50, 75], "color": "#FFC107", "label": "Medium"},
    {"range": [75, 100], "color": "#28A745", "label": "High"}
  ]
}
```

#### 2.6.3 KPI Dashboard Grid

**Illustration Type**: `kpi_dashboard_2x2`, `kpi_dashboard_3x2`

**Data Schema**:
```json
{
  "kpis": [
    {
      "title": "Revenue",
      "value": "$2.4M",
      "change": "+12%",
      "trend": "up",
      "comparison": "vs last quarter"
    },
    {
      "title": "Customers",
      "value": "1,250",
      "change": "+8%",
      "trend": "up"
    },
    {
      "title": "Satisfaction",
      "value": "4.6/5",
      "change": "-0.1",
      "trend": "down"
    },
    {
      "title": "Churn Rate",
      "value": "2.3%",
      "change": "-0.5%",
      "trend": "down"
    }
  ]
}
```

---

## 3. Custom Illustration Endpoint

### 3.1 Generate Custom Illustration

**Endpoint**: `POST /v1.0/generate/custom`

**Description**: Generate an illustration from a natural language description using Gemini LLM for intent parsing.

**Request Body**:
```json
{
  "description": "Create a 4-step horizontal process flow showing Research, Design, Build, and Launch phases with arrows connecting them",
  "theme": "professional",
  "size": "medium",
  "output_format": "svg"
}
```

**Request Schema**:
```typescript
{
  description: string,            // Required: Natural language description
  theme?: string,                 // Optional: "professional" (default), "bold", "minimal", "playful"
  size?: string,                  // Optional: "small", "medium" (default), "large", "custom"
  custom_size?: [number, number], // Optional: [width, height] if size="custom"
  output_format?: string          // Optional: "svg" (default), "png", "data_url"
}
```

**Response** (200 OK):
```json
{
  "description": "Create a 4-step horizontal process flow showing Research, Design, Build, and Launch phases with arrows connecting them",
  "inferred_type": "process_flow_4step",
  "confidence_score": 0.92,
  "format": "svg",
  "data": "<svg width=\"1200\" height=\"800\">...</svg>",
  "suggestions": [
    "Try 'vertical flowchart' for top-down layout",
    "Consider 'circular process' for cyclical workflows"
  ],
  "metadata": {
    "width": 1200,
    "height": 800,
    "theme": "professional",
    "element_count": 9,
    "generation_method": "llm_guided"
  },
  "generation_time_ms": 2147
}
```

**Response Schema**:
```typescript
{
  description: string,
  inferred_type: string,           // Best-match illustration type
  confidence_score: number,        // 0.0-1.0
  format: string,
  data: string,
  suggestions: string[],           // Alternative interpretations
  metadata: object,
  generation_time_ms: number
}
```

**Example Descriptions**:

**Good Descriptions** (high confidence):
```
"Create a SWOT analysis with 4 quadrants showing strengths, weaknesses, opportunities, and threats"
→ Inferred type: swot_2x2, confidence: 0.95

"Make a 5-step horizontal process flow: Research → Design → Build → Test → Deploy"
→ Inferred type: process_flow_5step, confidence: 0.93

"Generate a BCG matrix with products plotted in star, cash cow, question mark, and dog quadrants"
→ Inferred type: bcg_matrix, confidence: 0.91
```

**Ambiguous Descriptions** (medium confidence):
```
"Show a comparison between two options"
→ Inferred type: pros_vs_cons OR before_vs_after OR venn_2circle, confidence: 0.65
→ Suggestions provided for disambiguation

"Create a hierarchy diagram"
→ Inferred type: org_chart_hierarchical_3level OR pyramid_4level, confidence: 0.58
→ Asks for clarification: organizational or conceptual hierarchy?
```

**Poor Descriptions** (low confidence):
```
"Make a nice looking chart"
→ Error: Too vague, cannot infer type
→ Suggestions: "Specify diagram type (flowchart, matrix, pyramid, etc.) and key elements"

"Draw something with circles and arrows"
→ Error: Insufficient detail
→ Suggestions: "Describe the purpose: process flow, network graph, relationship diagram?"
```

---

## 4. Utility Endpoints

### 4.1 List All Illustrations

**Endpoint**: `GET /v1.0/illustrations`

**Description**: Get catalog of all 87 illustration types with metadata.

**Query Parameters**:
- `category` (optional): Filter by category (e.g., `process`, `strategic`, `organizational`)
- `tier` (optional): Filter by tier (`1`, `2`, `3`)

**Response** (200 OK):
```json
{
  "total_count": 87,
  "categories": 10,
  "illustrations": [
    {
      "illustration_type": "swot_2x2",
      "category": "strategic_frameworks",
      "tier": 1,
      "name": "SWOT Analysis",
      "description": "2x2 matrix for strengths, weaknesses, opportunities, threats",
      "business_value_score": 30,
      "sample_data_schema": {
        "strengths": ["string"],
        "weaknesses": ["string"],
        "opportunities": ["string"],
        "threats": ["string"]
      }
    },
    {
      "illustration_type": "process_flow_4step",
      "category": "process_flow",
      "tier": 1,
      "name": "4-Step Process Flow",
      "description": "Horizontal process with 4 sequential steps",
      "business_value_score": 28,
      "sample_data_schema": {
        "steps": [
          {"number": "int", "title": "string", "description": "string"}
        ]
      }
    }
  ]
}
```

**Example cURL**:
```bash
# Get all Tier 1 illustrations
curl https://illustrator-service.railway.app/v1.0/illustrations?tier=1

# Get all strategic framework illustrations
curl https://illustrator-service.railway.app/v1.0/illustrations?category=strategic_frameworks
```

---

### 4.2 Get Illustration Details

**Endpoint**: `GET /v1.0/illustration/{illustration_type}`

**Description**: Get detailed information about a specific illustration type.

**Path Parameters**:
- `illustration_type`: Illustration type ID (e.g., `swot_2x2`)

**Response** (200 OK):
```json
{
  "illustration_type": "swot_2x2",
  "name": "SWOT Analysis",
  "description": "2x2 matrix for strategic planning",
  "category": "strategic_frameworks",
  "tier": 1,
  "business_value_score": 30,
  "industries": ["consulting", "finance", "tech", "marketing"],
  "frequency_score": 10,
  "applicability_score": 10,
  "importance_score": 10,
  "data_schema": {
    "type": "object",
    "required": ["strengths", "weaknesses", "opportunities", "threats"],
    "properties": {
      "strengths": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "maxItems": 6
      },
      "weaknesses": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "maxItems": 6
      },
      "opportunities": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "maxItems": 6
      },
      "threats": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "maxItems": 6
      }
    }
  },
  "example_request": {
    "illustration_type": "swot_2x2",
    "data": {
      "strengths": ["Strong brand", "Market leader"],
      "weaknesses": ["High costs"],
      "opportunities": ["New markets"],
      "threats": ["Competition"]
    }
  },
  "supported_themes": ["professional", "bold", "minimal", "playful"],
  "supported_sizes": ["small", "medium", "large", "custom"]
}
```

---

### 4.3 List Themes

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
        "text": "#1A1A1A",
        "text_on_primary": "#FFFFFF",
        "border": "#CCCCCC",
        "success": "#28A745",
        "warning": "#FFC107",
        "danger": "#DC3545"
      }
    },
    {
      "name": "bold",
      "description": "Vibrant and attention-grabbing colors",
      "palette": {
        "primary": "#E31E24",
        "secondary": "#FFD700",
        "background": "#F5F5F5",
        "text": "#000000",
        "text_on_primary": "#FFFFFF",
        "border": "#333333",
        "success": "#00C853",
        "warning": "#FF9100",
        "danger": "#D50000"
      }
    },
    {
      "name": "minimal",
      "description": "Clean and understated design",
      "palette": {
        "primary": "#2C3E50",
        "secondary": "#95A5A6",
        "background": "#FFFFFF",
        "text": "#34495E",
        "text_on_primary": "#FFFFFF",
        "border": "#BDC3C7",
        "success": "#27AE60",
        "warning": "#F39C12",
        "danger": "#E74C3C"
      }
    },
    {
      "name": "playful",
      "description": "Energetic and creative colors",
      "palette": {
        "primary": "#9C27B0",
        "secondary": "#00BCD4",
        "background": "#FFFDE7",
        "text": "#424242",
        "text_on_primary": "#FFFFFF",
        "border": "#9E9E9E",
        "success": "#8BC34A",
        "warning": "#FF9800",
        "danger": "#F44336"
      }
    }
  ]
}
```

---

### 4.4 List Size Presets

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
      "use_case": "Thumbnail previews, small slides"
    },
    {
      "name": "medium",
      "width": 1200,
      "height": 800,
      "aspect_ratio": "3:2",
      "use_case": "Standard PowerPoint slides (default)"
    },
    {
      "name": "large",
      "width": 1800,
      "height": 720,
      "aspect_ratio": "2.5:1",
      "use_case": "Widescreen presentations, banners"
    },
    {
      "name": "custom",
      "description": "Custom dimensions",
      "constraints": {
        "min_width": 400,
        "min_height": 300,
        "max_width": 4000,
        "max_height": 3000,
        "aspect_ratio_range": "1:3 to 3:1"
      }
    }
  ]
}
```

---

### 4.5 Health Check

**Endpoint**: `GET /health`

**Description**: Service health and status check.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3456789,
  "vertex_ai": {
    "status": "connected",
    "model_flash": "gemini-2.5-flash",
    "model_pro": "gemini-2.5-pro"
  },
  "templates": {
    "loaded": 87,
    "cache_hit_rate": 0.94
  },
  "performance": {
    "avg_generation_time_ms": 487,
    "p95_generation_time_ms": 823,
    "requests_per_minute": 42
  }
}
```

**Response** (503 Service Unavailable) - when unhealthy:
```json
{
  "status": "unhealthy",
  "error": "Vertex AI connection failed",
  "details": {
    "vertex_ai": "disconnected",
    "last_successful_connection": "2024-03-15T10:30:00Z"
  }
}
```

---

### 4.6 Service Information

**Endpoint**: `GET /`

**Description**: Root endpoint with service overview.

**Response** (200 OK):
```json
{
  "service": "Illustrator Service",
  "version": "1.0.0",
  "description": "Professional PowerPoint illustration generation via programmatic SVG",
  "endpoints": {
    "generate_standard": "POST /v1.0/generate",
    "generate_custom": "POST /v1.0/generate/custom",
    "list_illustrations": "GET /v1.0/illustrations",
    "illustration_details": "GET /v1.0/illustration/{type}",
    "list_themes": "GET /v1.0/themes",
    "list_sizes": "GET /v1.0/sizes",
    "health_check": "GET /health"
  },
  "features": {
    "total_illustrations": 87,
    "categories": 10,
    "themes": 4,
    "size_presets": 3,
    "custom_endpoint": true,
    "llm_integration": "Gemini 2.5 Flash/Pro"
  },
  "documentation": "https://illustrator-service.railway.app/docs"
}
```

---

## 5. Request/Response Models

### 5.1 Common Models

**Theme**:
```typescript
type Theme = "professional" | "bold" | "minimal" | "playful"
```

**Size**:
```typescript
type Size = "small" | "medium" | "large" | "custom"
```

**OutputFormat**:
```typescript
type OutputFormat = "svg" | "png" | "data_url"
```

**CustomSize**:
```typescript
type CustomSize = [number, number]  // [width, height]
```

### 5.2 Standard Illustration Models

**StandardIllustrationRequest**:
```typescript
interface StandardIllustrationRequest {
  illustration_type: string
  data: Record<string, any>
  theme?: Theme
  size?: Size
  custom_size?: CustomSize
  output_format?: OutputFormat
}
```

**StandardIllustrationResponse**:
```typescript
interface StandardIllustrationResponse {
  illustration_type: string
  format: OutputFormat
  data: string
  metadata: {
    width: number
    height: number
    theme: string
    element_count: number
    generation_method: "template" | "programmatic" | "llm_guided"
  }
  generation_time_ms: number
}
```

### 5.3 Custom Illustration Models

**CustomIllustrationRequest**:
```typescript
interface CustomIllustrationRequest {
  description: string
  theme?: Theme
  size?: Size
  custom_size?: CustomSize
  output_format?: OutputFormat
}
```

**CustomIllustrationResponse**:
```typescript
interface CustomIllustrationResponse {
  description: string
  inferred_type: string
  confidence_score: number
  format: OutputFormat
  data: string
  suggestions: string[]
  metadata: {
    width: number
    height: number
    theme: string
    element_count: number
    generation_method: "llm_guided"
  }
  generation_time_ms: number
}
```

---

## 6. Error Handling

### 6.1 Error Response Format

**Standard Error Response**:
```typescript
interface ErrorResponse {
  error_type: string
  message: string
  details?: Record<string, any>
  suggestions?: string[]
  timestamp: string
  request_id: string
}
```

### 6.2 HTTP Status Codes

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid request body or parameters |
| 404 | Not Found | Illustration type not found |
| 422 | Unprocessable Entity | Validation error in data schema |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service unhealthy (e.g., Vertex AI down) |

### 6.3 Common Errors

**400 - Invalid Illustration Type**:
```json
{
  "error_type": "validation_error",
  "message": "Invalid illustration type: 'invalid_swot'",
  "details": {
    "received": "invalid_swot",
    "valid_types": ["swot_2x2", "bcg_matrix", "process_flow_4step"]
  },
  "suggestions": [
    "Use GET /v1.0/illustrations to see all valid types",
    "Did you mean 'swot_2x2'?"
  ],
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_abc123def456"
}
```

**422 - Data Validation Error**:
```json
{
  "error_type": "validation_error",
  "message": "Missing required field: 'strengths' for SWOT analysis",
  "details": {
    "illustration_type": "swot_2x2",
    "required_fields": ["strengths", "weaknesses", "opportunities", "threats"],
    "provided_fields": ["weaknesses", "opportunities", "threats"]
  },
  "suggestions": [
    "Add 'strengths' array to data object",
    "Use GET /v1.0/illustration/swot_2x2 to see full schema"
  ],
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_xyz789ghi012"
}
```

**422 - Invalid Data Format**:
```json
{
  "error_type": "validation_error",
  "message": "Invalid data format for 'steps' field",
  "details": {
    "field": "steps",
    "expected_type": "array",
    "received_type": "string",
    "constraint": "Must be array of objects with 'number', 'title', 'description'"
  },
  "suggestions": [
    "Format: {\"steps\": [{\"number\": 1, \"title\": \"...\", \"description\": \"...\"}]}",
    "See example request in GET /v1.0/illustration/process_flow_4step"
  ],
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_pqr345stu678"
}
```

**429 - Rate Limit Exceeded**:
```json
{
  "error_type": "rate_limit_error",
  "message": "Rate limit exceeded: 100 requests per minute",
  "details": {
    "limit": 100,
    "window": "60 seconds",
    "retry_after": 42
  },
  "suggestions": [
    "Wait 42 seconds before retrying",
    "Consider batching requests or caching results"
  ],
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_mno901vwx234"
}
```

**500 - LLM Error (Custom Endpoint)**:
```json
{
  "error_type": "llm_error",
  "message": "Failed to parse illustration intent from description",
  "details": {
    "description": "make something nice",
    "error": "Description too vague for intent extraction"
  },
  "suggestions": [
    "Be more specific about diagram type (flowchart, matrix, pyramid, etc.)",
    "Include key elements: 'Create a 4-step process flow with...'",
    "Specify layout: horizontal, vertical, circular, grid"
  ],
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_jkl567bcd890"
}
```

**503 - Service Unavailable**:
```json
{
  "error_type": "service_error",
  "message": "Vertex AI connection unavailable",
  "details": {
    "component": "vertex_ai",
    "status": "disconnected",
    "last_successful_connection": "2024-03-15T09:00:00Z"
  },
  "suggestions": [
    "Try again in a few moments",
    "Check service status at /health"
  ],
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_efg123hij456"
}
```

---

## 7. Integration Examples

### 7.1 Python Integration (Director Agent v3.4)

```python
import httpx
import asyncio

class IllustratorClient:
    def __init__(self, base_url: str = "https://illustrator-service.railway.app"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def generate_swot(self, strengths: list, weaknesses: list,
                           opportunities: list, threats: list,
                           theme: str = "professional") -> dict:
        """Generate SWOT analysis illustration"""
        request = {
            "illustration_type": "swot_2x2",
            "data": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "opportunities": opportunities,
                "threats": threats
            },
            "theme": theme,
            "size": "medium",
            "output_format": "svg"
        }

        response = await self.client.post(
            f"{self.base_url}/v1.0/generate",
            json=request
        )
        response.raise_for_status()
        return response.json()

    async def generate_custom(self, description: str,
                             theme: str = "professional") -> dict:
        """Generate custom illustration from description"""
        request = {
            "description": description,
            "theme": theme,
            "size": "medium"
        }

        response = await self.client.post(
            f"{self.base_url}/v1.0/generate/custom",
            json=request
        )
        response.raise_for_status()
        return response.json()

# Usage example
async def main():
    client = IllustratorClient()

    # Generate SWOT
    swot_result = await client.generate_swot(
        strengths=["Strong brand", "Market leader"],
        weaknesses=["High costs"],
        opportunities=["New markets"],
        threats=["Competition"]
    )
    print(f"SWOT SVG: {swot_result['data'][:100]}...")

    # Generate custom
    custom_result = await client.generate_custom(
        "Create a 4-step process flow: Research, Design, Build, Launch"
    )
    print(f"Custom type: {custom_result['inferred_type']}")
    print(f"Confidence: {custom_result['confidence_score']}")

asyncio.run(main())
```

### 7.2 TypeScript Integration

```typescript
import axios, { AxiosInstance } from 'axios';

interface IllustrationRequest {
  illustration_type: string;
  data: Record<string, any>;
  theme?: string;
  size?: string;
  output_format?: string;
}

interface IllustrationResponse {
  illustration_type: string;
  format: string;
  data: string;
  metadata: Record<string, any>;
  generation_time_ms: number;
}

class IllustratorClient {
  private client: AxiosInstance;

  constructor(baseURL = 'https://illustrator-service.railway.app') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  async generateProcessFlow(
    steps: Array<{ number: number; title: string; description: string }>,
    theme = 'professional'
  ): Promise<IllustrationResponse> {
    const stepCount = steps.length;
    const request: IllustrationRequest = {
      illustration_type: `process_flow_${stepCount}step`,
      data: { steps },
      theme,
      size: 'medium',
      output_format: 'svg'
    };

    const response = await this.client.post<IllustrationResponse>(
      '/v1.0/generate',
      request
    );
    return response.data;
  }

  async generateBCGMatrix(
    products: Array<{
      name: string;
      quadrant: 'star' | 'cash_cow' | 'question_mark' | 'dog';
      market_share: number;
      market_growth: number;
    }>,
    theme = 'professional'
  ): Promise<IllustrationResponse> {
    const request: IllustrationRequest = {
      illustration_type: 'bcg_matrix',
      data: { products },
      theme
    };

    const response = await this.client.post<IllustrationResponse>(
      '/v1.0/generate',
      request
    );
    return response.data;
  }
}

// Usage
const client = new IllustratorClient();

// Generate process flow
const processFlow = await client.generateProcessFlow([
  { number: 1, title: 'Research', description: 'Market analysis' },
  { number: 2, title: 'Design', description: 'Create prototypes' },
  { number: 3, title: 'Build', description: 'Development' },
  { number: 4, title: 'Launch', description: 'Release to market' }
], 'bold');

console.log(`Generated SVG (${processFlow.generation_time_ms}ms)`);
```

### 7.3 cURL Examples

**Generate SWOT Analysis**:
```bash
curl -X POST https://illustrator-service.railway.app/v1.0/generate \
  -H "Content-Type: application/json" \
  -d '{
    "illustration_type": "swot_2x2",
    "data": {
      "strengths": ["Strong brand", "Market leader", "Innovation"],
      "weaknesses": ["High costs", "Limited reach"],
      "opportunities": ["New markets", "Digital transformation"],
      "threats": ["Competition", "Economic downturn"]
    },
    "theme": "professional",
    "size": "medium",
    "output_format": "svg"
  }'
```

**Generate Process Flow**:
```bash
curl -X POST https://illustrator-service.railway.app/v1.0/generate \
  -H "Content-Type: application/json" \
  -d '{
    "illustration_type": "process_flow_5step",
    "data": {
      "steps": [
        {"number": 1, "title": "Research", "description": "Gather requirements"},
        {"number": 2, "title": "Design", "description": "Create mockups"},
        {"number": 3, "title": "Build", "description": "Develop solution"},
        {"number": 4, "title": "Test", "description": "Quality assurance"},
        {"number": 5, "title": "Deploy", "description": "Release to production"}
      ]
    },
    "theme": "bold"
  }'
```

**Generate Custom Illustration**:
```bash
curl -X POST https://illustrator-service.railway.app/v1.0/generate/custom \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a BCG matrix showing 4 products positioned in star, cash cow, question mark, and dog quadrants",
    "theme": "minimal",
    "size": "large"
  }'
```

**List All Tier 1 Illustrations**:
```bash
curl https://illustrator-service.railway.app/v1.0/illustrations?tier=1
```

**Get SWOT Details**:
```bash
curl https://illustrator-service.railway.app/v1.0/illustration/swot_2x2
```

**Health Check**:
```bash
curl https://illustrator-service.railway.app/health
```

---

## Appendix A: Complete Illustration Type Reference

### Process & Flow Diagrams
- `process_flow_3step`, `process_flow_4step`, `process_flow_5step`
- `flowchart_4step`, `flowchart_6step`
- `circular_process_4step`, `circular_process_6step`
- `funnel_3stage`, `funnel_4stage`, `funnel_5stage`
- `timeline_horizontal_5point`, `timeline_horizontal_7point`
- `swimlane_diagram`
- `gantt_chart_simple`
- `decision_tree`

### Strategic Frameworks & Matrices
- `swot_2x2`
- `bcg_matrix`
- `ansoff_matrix`
- `porters_five_forces`
- `value_chain`
- `balanced_scorecard`
- `mckinsey_7s`
- `business_model_canvas`
- `stakeholder_mapping`
- `risk_matrix`

### Organizational Charts
- `org_chart_hierarchical_3level`
- `org_chart_matrix`
- `org_chart_flat`

### Comparison & Analysis
- `venn_2circle`, `venn_3circle`
- `pros_vs_cons`
- `before_vs_after`

### Data Visualization
- `pyramid_3level`, `pyramid_4level`, `pyramid_5level`
- `gauge_meter`
- `kpi_dashboard_2x2`, `kpi_dashboard_3x2`

### Technical Diagrams
- `system_architecture`
- `network_topology`
- `entity_relationship`
- `component_diagram`
- `deployment_diagram`

### Relationship Diagrams
- `hub_and_spoke`
- `mind_map`
- `network_graph`
- `influence_diagram`
- `cause_and_effect`

### Conceptual Diagrams
- `iceberg_model`
- `bridge_metaphor`
- `ladder_of_inference`
- `onion_diagram`
- `cycle_of_improvement`

### Geographical
- `world_map_highlight`
- `regional_map`
- `location_pins`

### Specialized Business
- `customer_journey_map`
- `sales_pipeline`
- (Plus 42 additional specialized illustrations)

---

**End of API Specification**
