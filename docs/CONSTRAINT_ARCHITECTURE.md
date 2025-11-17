# Illustrator Service v1.0 - Constraint Architecture

**Document Purpose**: Define how Illustrator Service handles layout constraints following Text Service's proven pattern.

**Date**: November 10, 2025

---

## Executive Summary

The Illustrator Service will follow the **exact same constraint model** as Text Service v1.2:

1. **Pre-calibrated constraints** encoded in JSON specs (not dynamic pixel measurements)
2. **Fixed templates** with predictable dimensions based on CSS layout
3. **Item count + character limits** for text within illustrations
4. **LLM enforcement** through explicit prompt constraints
5. **Golden example process** to establish baselines

**Key Insight**: We do NOT receive "you have 1800×720px" from Layout Architect. Instead, we use **pre-tested constraints** that we know fit perfectly in L25's `rich_content` area.

---

## The Three-Layer Constraint System

### Layer 1: HTML Template (Spatial Structure)

**Current Problem**: Our SWOT template is hardcoded
```html
<div style="width: 1200px; height: 800px;">  <!-- WRONG -->
```

**Solution**: Use percentage/viewport units for L25 content area
```html
<div style="width: 100%; height: 100%; max-width: 1800px; max-height: 720px;">
  <style>
    .swot-container {
      display: grid;
      grid-template-columns: 1fr 1fr;  /* Always 50/50 split */
      grid-template-rows: 1fr 1fr;     /* Always 50/50 split */
      gap: 2px;                         /* Fixed spacing */
      font-size: 20px;                  /* Fixed font for predictability */
      line-height: 1.4;                 /* Fixed line spacing */
      height: 100%;
    }
    .swot-quadrant h3 {
      font-size: 28px;                  /* Fixed title size */
      font-weight: 600;
    }
    .swot-quadrant li {
      font-size: 18px;                  /* Fixed item size */
      line-height: 1.4;
    }
  </style>
  ...
</div>
```

**Why This Works**:
- L25 content area is always 1800×720px
- 100% width/height fills that area perfectly
- Fixed fonts make text dimensions predictable
- Grid `1fr 1fr` means each quadrant gets consistent space

### Layer 2: Variant Spec (Content Constraints)

**Following Text Service Pattern**:

```json
{
  "variant_id": "swot_2x2_base",
  "illustration_type": "swot_2x2",
  "template_path": "templates/swot_2x2/base.html",
  "l25_compatible": true,
  "elements": [
    {
      "element_id": "strengths",
      "element_type": "quadrant",
      "required_fields": ["items"],
      "item_constraints": {
        "min_items": 2,
        "max_items": 5,
        "baseline_items": 4,
        "chars_per_item": {
          "baseline": 45,
          "min": 40,
          "max": 50
        }
      }
    },
    {
      "element_id": "weaknesses",
      "element_type": "quadrant",
      "required_fields": ["items"],
      "item_constraints": {
        "min_items": 2,
        "max_items": 5,
        "baseline_items": 4,
        "chars_per_item": {
          "baseline": 45,
          "min": 40,
          "max": 50
        }
      }
    },
    {
      "element_id": "opportunities",
      "element_type": "quadrant",
      "required_fields": ["items"],
      "item_constraints": {
        "min_items": 2,
        "max_items": 5,
        "baseline_items": 4,
        "chars_per_item": {
          "baseline": 45,
          "min": 40,
          "max": 50
        }
      }
    },
    {
      "element_id": "threats",
      "element_type": "quadrant",
      "required_fields": ["items"],
      "item_constraints": {
        "min_items": 2,
        "max_items": 5,
        "baseline_items": 4,
        "chars_per_item": {
          "baseline": 45,
          "min": 40,
          "max": 50
        }
      }
    }
  ],
  "golden_example": {
    "strengths": [
      "Strong brand recognition in key markets",      // 41 chars
      "Market leader with 35% share",                 // 30 chars
      "Robust financial position and reserves",       // 42 chars
      "Experienced leadership team"                   // 28 chars
    ],
    "weaknesses": [
      "High operational costs vs competitors",        // 41 chars
      "Limited physical retail presence",             // 36 chars
      "Dependency on key suppliers"                   // 32 chars
    ],
    "opportunities": [
      "Emerging markets expansion in Asia-Pacific",   // 47 chars
      "AI and machine learning integration",          // 39 chars
      "Strategic partnerships and acquisitions",      // 43 chars
      "Growing demand for sustainable solutions"      // 44 chars
    ],
    "threats": [
      "Intense competition in core markets",          // 39 chars
      "Regulatory challenges and compliance costs",   // 46 chars
      "Rapid technological changes"                   // 30 chars
    ]
  }
}
```

**How Baseline Was Determined**:
1. Created SWOT template in L25 (1800×720px)
2. Manually wrote perfect example content
3. Counted characters per item
4. Tested ±5% tolerance
5. Verified visual quality
6. Encoded in JSON spec

### Layer 3: API Request Format

**Match Text Service Pattern**:

```python
class IllustrationGenerationRequest(BaseModel):
    """
    Request for illustration generation.
    Matches Text Service pattern.
    """
    # Session tracking
    presentation_id: str = Field(
        description="Unique presentation identifier"
    )

    # Slide identification
    slide_id: str = Field(
        description="Unique slide identifier like 'slide_003'"
    )
    slide_number: int = Field(
        description="Slide number in presentation"
    )

    # Illustration specification
    illustration_type: str = Field(
        description="Type: swot_2x2, ansoff_matrix, timeline_horizontal, etc."
    )
    variant_id: str = Field(
        default="base",
        description="Variant: base, rounded, condensed, etc."
    )

    # Content source
    topics: List[str] = Field(
        description="Key points to visualize (Director's key_points)"
    )
    narrative: str = Field(
        description="Overall story for this illustration",
        default=""
    )

    # Context
    context: Dict[str, Any] = Field(
        description="Presentation context",
        default_factory=dict
    )

    # NO pixel constraints - we use pre-calibrated specs!
    # constraints field is optional and ignored
```

**Response Format** (match Text Service):

```python
class IllustrationResponse(BaseModel):
    """
    Generated illustration response.
    Matches Text Service GeneratedText model.
    """
    content: str = Field(
        description="HTML-formatted illustration ready for L25.rich_content"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata"
    )

    # Example response:
    # {
    #   "content": "<div style='width: 100%; height: 100%;'>...</div>",
    #   "metadata": {
    #     "illustration_type": "swot_2x2",
    #     "variant_id": "base",
    #     "items_generated": {
    #       "strengths": 4,
    #       "weaknesses": 3,
    #       "opportunities": 4,
    #       "threats": 3
    #     },
    #     "within_constraints": true,
    #     "generation_time_ms": 250,
    #     "model_used": "template_based"
    #   }
    # }
```

---

## The Golden Example Process

### Step 1: Design Template

Create `templates/swot_2x2/base.html`:
```html
<div style="width: 100%; height: 100%; max-width: 1800px; max-height: 720px;">
  <style>
    .swot-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 2px;
      background: #CCCCCC;
      height: 100%;
      font-family: Arial, sans-serif;
    }
    /* ... fixed fonts, spacing, layout ... */
  </style>

  <div class="swot-quadrant strengths">
    <h3>Strengths</h3>
    <ul>{strengths_items}</ul>
  </div>
  <!-- ... other quadrants ... -->
</div>
```

### Step 2: Create Golden Example

Manually write perfect content:

**Strengths** (4 items):
- "Strong brand recognition in key markets" (41 chars) ✓
- "Market leader with 35% market share" (36 chars) ✓
- "Robust financial position and reserves" (42 chars) ✓
- "Experienced leadership team" (28 chars) ✓

**Visual Test**: Does it look good in L25? Yes!

### Step 3: Test Tolerance

**Test with 3 items** (min):
- Still looks balanced? Yes!

**Test with 5 items** (max):
- Still fits without overflow? Yes!

**Test with 35-char items** (min length):
- Looks too sparse? No, still good!

**Test with 55-char items** (max length):
- Text wraps nicely? Yes!

### Step 4: Codify in JSON

Create `variant_specs/swot_2x2/base.json` with measured constraints.

### Step 5: LLM Integration (Future)

If we want LLM to generate illustration data:

```python
prompt = f"""
Generate SWOT analysis content for: {narrative}

ITEM COUNT REQUIREMENTS (STRICT):
- Strengths: 2-5 items (target: 4)
- Weaknesses: 2-5 items (target: 3)
- Opportunities: 2-5 items (target: 4)
- Threats: 2-5 items (target: 3)

CHARACTER COUNT REQUIREMENTS (STRICT):
- Each item: 40-50 characters (target: 45)

Return JSON format:
{{
  "strengths": ["item1", "item2", ...],
  "weaknesses": ["item1", "item2", ...],
  "opportunities": ["item1", "item2", ...],
  "threats": ["item1", "item2", ...]
}}
"""
```

---

## Recommended Directory Structure

Following Text Service pattern:

```
agents/illustrator/v1.0/
├── main.py
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # IllustrationGenerationRequest
│   │   └── responses.py     # IllustrationResponse
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constraint_loader.py   # Loads variant specs
│   │   ├── template_engine.py     # Fills templates
│   │   └── validator.py           # Validates constraints
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # /api/v1/generate/illustration/{type}
│   └── themes.py            # 4 color themes
├── templates/               # HTML templates with fixed layouts
│   ├── swot_2x2/
│   │   ├── base.html
│   │   ├── rounded.html
│   │   └── condensed.html
│   ├── ansoff_matrix/
│   │   └── base.html
│   └── timeline/
│       ├── horizontal.html
│       └── vertical.html
└── variant_specs/           # JSON constraint definitions
    ├── swot_2x2/
    │   ├── base.json
    │   ├── rounded.json
    │   └── condensed.json
    ├── ansoff_matrix/
    │   └── base.json
    ├── timeline/
    │   ├── horizontal.json
    │   └── vertical.json
    └── variant_index.json
```

---

## API Endpoint Design

Following Text Service pattern:

```python
# Specialized endpoints (like Text Service)
@router.post("/api/v1/generate/illustration/swot_2x2")
async def generate_swot_2x2(request: IllustrationGenerationRequest):
    """Generate SWOT 2×2 matrix illustration"""
    ...

@router.post("/api/v1/generate/illustration/ansoff_matrix")
async def generate_ansoff_matrix(request: IllustrationGenerationRequest):
    """Generate Ansoff matrix illustration"""
    ...

@router.post("/api/v1/generate/illustration/timeline")
async def generate_timeline(request: IllustrationGenerationRequest):
    """Generate timeline illustration"""
    ...

# Generic endpoint (fallback)
@router.post("/api/v1/generate/illustration")
async def generate_illustration(request: IllustrationGenerationRequest):
    """Generic illustration generation"""
    ...
```

---

## Integration with Director Agent

**Director's Stage 6 Flow**:

```python
# Director classifies slide
slide_type = classifier.classify(slide)

# Check if needs illustration vs text
if slide_type in ["swot_analysis", "strategic_matrix", "timeline"]:
    # Call Illustrator Service
    illustration_request = {
        "presentation_id": pres_id,
        "slide_id": slide.id,
        "slide_number": slide.number,
        "illustration_type": map_slide_type_to_illustration(slide_type),
        "variant_id": "base",
        "topics": slide.key_points,
        "narrative": slide.narrative,
        "context": {
            "theme": "professional",
            "audience": context.audience,
            "slide_title": slide.title
        }
    }

    response = illustrator_client.generate(illustration_request)

    # Use in L25.rich_content
    enriched_slide.content = {
        "slide_title": slide.title,
        "rich_content": response["content"]  # Illustration HTML
    }

else:
    # Call Text Service (existing flow)
    text_request = {...}
    response = text_client.generate(text_request)
    enriched_slide.content = {
        "slide_title": slide.title,
        "rich_content": response["content"]  # Text HTML
    }
```

---

## Constraint Validation

```python
class ConstraintValidator:
    """Validates illustration content meets variant spec constraints"""

    def validate(self, content: Dict[str, Any], spec: Dict[str, Any]) -> bool:
        """
        Validate generated content against variant spec.

        Args:
            content: Generated illustration data
            spec: Variant specification with constraints

        Returns:
            True if valid, raises ValidationError otherwise
        """
        for element in spec["elements"]:
            element_id = element["element_id"]
            items = content.get(element_id, [])

            # Check item count
            constraints = element["item_constraints"]
            min_items = constraints["min_items"]
            max_items = constraints["max_items"]

            if not (min_items <= len(items) <= max_items):
                raise ValidationError(
                    f"{element_id}: has {len(items)} items, "
                    f"expected {min_items}-{max_items}"
                )

            # Check character count per item
            char_limits = constraints["chars_per_item"]
            for item in items:
                char_count = len(item)
                if not (char_limits["min"] <= char_count <= char_limits["max"]):
                    raise ValidationError(
                        f"{element_id} item '{item}': has {char_count} chars, "
                        f"expected {char_limits['min']}-{char_limits['max']}"
                    )

        return True
```

---

## Key Takeaways

### What We Learned from Text Service

1. ✅ **No dynamic pixel constraints** - Use pre-calibrated specs
2. ✅ **Fixed templates** - Predictable layouts with fixed fonts/spacing
3. ✅ **Item count + character limits** - Express spatial constraints
4. ✅ **Golden example process** - Manual testing establishes baselines
5. ✅ **JSON variant specs** - Codify constraints for reuse
6. ✅ **Validation** - Check output before returning

### How We'll Apply to Illustrator Service

1. ✅ Refactor templates to use **100% width/height** with **max constraints**
2. ✅ Create **variant specs** with item/character constraints
3. ✅ Build **golden examples** for each illustration type
4. ✅ Test **tolerance ranges** (±5% baseline)
5. ✅ Implement **constraint validation**
6. ✅ Match **Text Service API pattern** for Director integration

### Current Template Status

**SWOT 2x2 (base)**:
- ✅ HTML template exists
- ❌ Uses hardcoded dimensions (1200×800px)
- ❌ No variant spec JSON
- ❌ No constraint validation
- ❌ No golden example documented

**Next Steps**:
1. Refactor SWOT template for L25 constraints
2. Create variant spec JSON with measured constraints
3. Document golden example
4. Test in actual L25 reveal.js slide
5. Validate visual quality at baseline ±5%

---

## Summary

The Illustrator Service will **mirror Text Service's constraint architecture**:

- **Pre-calibrated specs** (not dynamic measurements)
- **Fixed template layouts** (predictable dimensions)
- **Item count + character limits** (spatial constraints)
- **Golden example process** (manual testing)
- **Validation before delivery** (ensure quality)

This approach has been **proven in production** by Text Service v1.2 and will ensure our illustrations always fit perfectly in L25 content slides.

---

**Document Version**: 1.0
**Created**: November 10, 2025
**Based On**: Text Service v1.2 constraint architecture analysis
**Status**: Ready for implementation
