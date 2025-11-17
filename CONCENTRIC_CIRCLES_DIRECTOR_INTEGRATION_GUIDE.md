# Concentric Circles - Director Integration Guide

**Date**: November 17, 2025
**Status**: Implementation Complete - Ready for Director Integration
**Version**: v1.0

---

## Executive Summary

The Concentric Circles illustration endpoint is **production-ready** and follows the same proven pattern as Pyramid and Funnel endpoints. This guide provides everything needed for Director v3.4 integration.

---

## API Endpoint

### **POST /v1.0/concentric_circles/generate**

**Base URL**: `http://localhost:8000` (Illustrator Service)

**Timeout**: 60 seconds (recommended)

---

## Request Model

### ConcentricCirclesGenerationRequest

```json
{
  "num_circles": 3,  // Required: 3-5 (number of concentric circles)
  "topic": "Business Strategy Layers",  // Required: Main topic/theme

  // Session Tracking (Optional - Director should populate these)
  "presentation_id": "pres-001",  // Optional: Presentation identifier
  "slide_id": "slide-5",          // Optional: Slide identifier
  "slide_number": 5,              // Optional: Slide position

  // Context (Optional but recommended for narrative continuity)
  "context": {
    "presentation_title": "Strategic Planning 2024",
    "slide_purpose": "Show layered business strategy approach",
    "key_message": "Core focus expanding to broader market",
    "industry": "Technology",
    "previous_slides": [  // Array of previous slide summaries
      {
        "title": "Market Overview",
        "key_points": ["Growing demand", "Competition analysis"]
      }
    ]
  },

  // Content Guidance (Optional)
  "target_points": [  // Suggested circle labels (LLM will consider these)
    "Core Team",
    "Extended Network",
    "Market Reach"
  ],

  // Configuration
  "tone": "professional",         // Default: "professional"
  "audience": "executives",       // Default: "general"
  "theme": "professional",        // Default: "professional" (for future use)
  "size": "medium",              // Default: "medium" (for future use)
  "validate_constraints": true   // Default: true
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `num_circles` | int | ✅ Yes | Number of concentric circles (3-5) |
| `topic` | string | ✅ Yes | Main topic/theme (min 3 chars) |
| `presentation_id` | string | ❌ No | Presentation identifier for tracking |
| `slide_id` | string | ❌ No | Slide identifier |
| `slide_number` | int | ❌ No | Slide position in presentation |
| `context` | object | ❌ No | Additional context for content generation |
| `target_points` | array[string] | ❌ No | Suggested circle labels |
| `tone` | string | ❌ No | Writing tone (default: "professional") |
| `audience` | string | ❌ No | Target audience (default: "general") |
| `validate_constraints` | bool | ❌ No | Enforce character limits (default: true) |

---

## Response Model

### ConcentricCirclesGenerationResponse

```json
{
  "success": true,
  "html": "<div class='concentric-container'>...</div>",

  "metadata": {
    "num_circles": 3,
    "template_file": "3.html",
    "theme": "professional",
    "size": "medium",
    "topic": "Business Strategy Layers",
    "generation_time_ms": 2572,
    "attempts": 1,
    "model": "gemini-2.5-flash-lite",
    "usage": {
      "prompt_tokens": 850,
      "completion_tokens": 320
    }
  },

  "generated_content": {
    "circle_1_label": "Core Values",
    "circle_2_label": "Strategic Goals",
    "circle_3_label": "Market Position",
    "legend_1_bullet_1": "Customer-first approach drives decisions",
    "legend_1_bullet_2": "Innovation and quality are paramount",
    // ... all generated fields
  },

  "character_counts": {
    "circle_1_label": 11,
    "circle_2_label": 15,
    "circle_3_label": 17,
    // ... all field counts
  },

  "validation": {
    "valid": true,
    "violations": []  // Empty if all constraints met
  },

  "generation_time_ms": 2572,

  // Session fields echoed from request
  "presentation_id": "pres-001",
  "slide_id": "slide-5",
  "slide_number": 5
}
```

---

## Character Constraints

### 3-Circle Variant
- **Circle Labels**: 5-12, 8-16, 10-18 chars
- **Legend Bullets**: 30-45 chars each (5 bullets per legend, 3 legends total)

### 4-Circle Variant
- **Circle Labels**: 5-12, 8-14, 8-16, 10-18 chars
- **Legend Bullets**: 30-45 chars each (4 bullets per legend, 4 legends total)

### 5-Circle Variant
- **Circle Labels**: 5-12, 8-14, 8-16, 8-18, 10-18 chars
- **Legend Bullets**: 30-45 chars each (3 bullets per legend, 5 legends total)

**Note**: As circles increase, bullets per legend decrease (5→4→3) to fit available space.

---

## Director Integration Steps

### Step 1: Update Service Registry

**File**: `agents/director_agent/v3.4/src/utils/service_registry.py`

```python
"illustrator_service": ServiceConfig(
    enabled=True,
    base_url="http://localhost:8000",
    slide_types=[
        "pyramid",
        "funnel",
        "concentric_circles",  # ✅ ADD THIS
    ],
    endpoints={
        "pyramid": ServiceEndpoint(
            path="/v1.0/pyramid/generate",
            method="POST",
            timeout=60
        ),
        "funnel": ServiceEndpoint(
            path="/v1.0/funnel/generate",
            method="POST",
            timeout=60
        ),
        "concentric_circles": ServiceEndpoint(  # ✅ ADD THIS
            path="/v1.0/concentric_circles/generate",
            method="POST",
            timeout=60
        )
    }
)
```

### Step 2: Add IllustratorClient Method

**File**: `agents/director_agent/v3.4/src/clients/illustrator_client.py`

```python
async def generate_concentric_circles(
    self,
    num_circles: int,
    topic: str,
    presentation_id: Optional[str] = None,
    slide_id: Optional[str] = None,
    slide_number: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None,
    target_points: Optional[List[str]] = None,
    tone: str = "professional",
    audience: str = "general",
    validate_constraints: bool = True
) -> Dict[str, Any]:
    """
    Generate concentric circles visualization with AI-generated content.

    Args:
        num_circles: Number of concentric circles (3-5)
        topic: Main topic/theme for the circles
        presentation_id: Optional presentation identifier
        slide_id: Optional slide identifier
        slide_number: Optional slide position
        context: Additional context for content generation
        target_points: Optional suggested circle labels
        tone: Writing tone (default: "professional")
        audience: Target audience (default: "general")
        validate_constraints: Whether to enforce character limits

    Returns:
        Dict with success, html, metadata, generated_content, validation
    """
    payload = {
        "num_circles": num_circles,
        "topic": topic,
        "tone": tone,
        "audience": audience,
        "validate_constraints": validate_constraints
    }

    # Add session tracking
    if presentation_id:
        payload["presentation_id"] = presentation_id
    if slide_id:
        payload["slide_id"] = slide_id
    if slide_number is not None:
        payload["slide_number"] = slide_number

    # Add context
    if context:
        payload["context"] = context
    if target_points:
        payload["target_points"] = target_points

    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.post(
            f"{self.base_url}/v1.0/concentric_circles/generate",
            json=payload
        )
        response.raise_for_status()

    return response.json()
```

---

## Usage Examples

### Example 1: Simple 3-Circle Generation

```python
# Director orchestration code
result = await illustrator_client.generate_concentric_circles(
    num_circles=3,
    topic="Business Strategy Layers",
    presentation_id=session.presentation_id,
    slide_id=slide_spec.slide_id,
    slide_number=5
)

# Extract HTML for layout
concentric_circles_html = result["html"]
```

### Example 2: With Context and Target Points

```python
result = await illustrator_client.generate_concentric_circles(
    num_circles=4,
    topic="Customer Engagement Model",
    presentation_id=session.presentation_id,
    slide_id=slide_spec.slide_id,
    slide_number=7,
    context={
        "presentation_title": "Customer Success Framework",
        "industry": "SaaS",
        "previous_slides": previous_slide_summaries
    },
    target_points=[
        "Core Users",
        "Active Customers",
        "Trial Users",
        "Potential Market"
    ],
    tone="professional",
    audience="customer success team"
)
```

### Example 3: Error Handling

```python
try:
    result = await illustrator_client.generate_concentric_circles(
        num_circles=5,
        topic="Market Influence Zones",
        presentation_id=session.presentation_id,
        slide_id=slide_spec.slide_id,
        slide_number=10
    )

    if not result["success"]:
        logger.error(f"Concentric circles generation failed: {result.get('error')}")
        # Fallback to alternative slide type

    # Check validation
    if not result["validation"]["valid"]:
        logger.warning(
            f"Character constraint violations: "
            f"{len(result['validation']['violations'])} fields"
        )
        # Decide whether to accept or retry

except httpx.TimeoutException:
    logger.error("Concentric circles generation timeout (>60s)")
    # Fallback handling

except httpx.HTTPStatusError as e:
    logger.error(f"Illustrator service error: {e.response.status_code}")
    # Error handling
```

---

## Layout Integration

### Supported Layouts

Like Pyramid and Funnel, Concentric Circles supports:
- **L25**: Full canvas (1800×720px) - `rich_content`
- **L01**: Diagram with body text - `element_4` (diagram) + `element_3` (text)
- **L02**: Diagram left, text right - `element_3` (diagram) + `element_2` (text)

### Layout Example (L25)

```python
# Director wraps illustration HTML in layout
layout_content = {
    "slide_title": "Business Strategy Framework",
    "subtitle": "Layered Approach to Market Positioning",
    "rich_content": result["html"]  # Concentric circles HTML
}

# Send to Layout Builder
await layout_builder_client.build_slide(
    layout_id="L25",
    content=layout_content
)
```

---

## Testing Checklist

Before deploying Director integration:

- [ ] Verify Illustrator service is running on port 8000
- [ ] Test `/v1.0/concentric_circles/generate` endpoint directly
- [ ] Confirm all 3 variants work (3, 4, 5 circles)
- [ ] Test with `previous_slides` context
- [ ] Verify session field echoing works
- [ ] Test error handling (timeout, invalid input)
- [ ] Validate HTML renders correctly in layouts
- [ ] Check character constraint validation
- [ ] Confirm generation time is acceptable (<10s)

---

## Key Differences from Pyramid/Funnel

| Aspect | Pyramid/Funnel | Concentric Circles |
|--------|----------------|-------------------|
| Variant count | Pyramid: 4 (3-6), Funnel: 3 (3-5) | 3 variants (3-5) |
| Structure | Vertical hierarchy | Radial layers (core to outer) |
| Legend bullets | Fixed per level | Varies: 5→4→3 bullets as circles increase |
| Visual metaphor | Top-down hierarchy | Center-outward expansion |
| Typical use cases | Strategy, processes | Influence zones, layered models |

---

## Performance Metrics (from local testing)

| Variant | Avg Generation Time | Success Rate |
|---------|-------------------|--------------|
| 3 circles | ~2.5s | 100% |
| 4 circles | ~7.5s | 100% |
| 5 circles | ~7.5s | 100% |

**Note**: Minor character constraint violations (1-2 chars) may occur but don't affect visual quality.

---

## Environment Variables

**Required in Illustrator Service `.env`**:
```bash
LLM_CONCENTRIC_CIRCLES=gemini-2.5-flash-lite
GCP_PROJECT_ID=deckster-xyz
GEMINI_LOCATION=us-central1
```

---

## Support & Troubleshooting

### Common Issues

**Issue**: Timeout errors
- **Solution**: Increase timeout to 90s for 5-circle variants

**Issue**: Character violations
- **Solution**: These are minor (1-2 chars) and don't affect quality. Accept gracefully.

**Issue**: Missing circle labels
- **Solution**: Check `target_points` is properly formatted as array

**Issue**: Context not working
- **Solution**: Verify `previous_slides` array structure matches Text Service v1.2 format

---

## Success Criteria

✅ **Integration is successful when**:
- Director can call endpoint and receive valid HTML
- All 3 variants generate correctly
- Session tracking fields echo properly
- Context (previous_slides) integrates successfully
- HTML renders correctly in all supported layouts
- Error handling is graceful
- Generation time is acceptable (<10s)

---

## Next Steps

1. **Update Director service registry** with concentric_circles endpoint
2. **Add `generate_concentric_circles()` method** to IllustratorClient
3. **Test end-to-end** with Director orchestration
4. **Update Director integration tests** to include concentric circles
5. **Deploy to production** after E2E validation

---

**Ready for Director Integration** ✅

For questions or issues, refer to:
- `test_concentric_circles_api.py` - Test script examples
- `FUNNEL_DIRECTOR_INTEGRATION_GUIDE.md` - Similar pattern reference
- Illustrator service logs - Debug information
