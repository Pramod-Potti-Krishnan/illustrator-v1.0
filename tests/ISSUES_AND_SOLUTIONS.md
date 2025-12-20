# Illustrator Service v1.0 - Issues and Solutions

**Test Date**: December 20, 2024
**Target URL**: `https://illustrator-v10-production.up.railway.app`

---

## Issue #1: Missing `infographic_html` Field (CRITICAL)

### Description

The contract (ILLUSTRATOR_SERVICE_CAPABILITIES.md v1.0.2) specifies that all visual generation endpoints should return an `infographic_html` field as an alias for `html` to support Layout Service integration.

**Affected Endpoints**:
- `POST /v1.0/pyramid/generate` (all variants: 3, 4, 5, 6 levels)
- `POST /v1.0/funnel/generate` (all variants: 3, 4, 5 stages)
- `POST /v1.0/concentric_circles/generate` (all variants: 3, 4, 5 rings)

**Working Endpoint**:
- `POST /concept-spread/generate` - Correctly returns `infographic_html`

### Impact

- **Layout Service integration is broken** for pyramid, funnel, and concentric circles
- Director Agent must map `html` -> `infographic_html` manually
- Contract violation

### Evidence

**Expected Response** (per contract):
```json
{
  "success": true,
  "html": "<div class='pyramid-container'>...</div>",
  "infographic_html": "<div class='pyramid-container'>...</div>",
  "metadata": {...},
  "generated_content": {...},
  "validation": {...}
}
```

**Actual Response**:
```json
{
  "success": true,
  "html": "<div class='pyramid-container'>...</div>",
  "metadata": {...},
  "generated_content": {...},
  "validation": {...}
}
```

### Solution

**Files to modify**:
1. `/illustrator/v1.0/app/api_routes/pyramid_routes.py`
2. `/illustrator/v1.0/app/api_routes/funnel_routes.py`
3. `/illustrator/v1.0/app/api_routes/concentric_circles_routes.py`

**Code Change Pattern**:

```python
# In the response model class, add:
class PyramidGenerationResponse(BaseModel):
    success: bool
    html: Optional[str] = None
    infographic_html: Optional[str] = None  # ADD THIS
    metadata: Optional[dict] = None
    generated_content: Optional[dict] = None
    validation: Optional[dict] = None

# In the generation function, set both fields:
return PyramidGenerationResponse(
    success=True,
    html=result["html"],
    infographic_html=result["html"],  # ADD THIS - same as html
    metadata=result["metadata"],
    generated_content=result["generated_content"],
    validation=result["validation"]
)
```

### Priority

**CRITICAL** - Blocks Layout Service integration

---

## Issue #2: Layout Service Grid Constraints Mismatch (DOCUMENTATION)

### Description

The contract shows example grid constraints of `gridWidth: 20, gridHeight: 12` but the actual validation limits are `gridWidth: 12, gridHeight: 8`.

### Impact

- API calls using documented example values fail validation
- Developers will encounter unexpected validation errors

### Evidence

**Documented Example** (ILLUSTRATOR_SERVICE_CAPABILITIES.md):
```json
{
  "constraints": {
    "gridWidth": 20,
    "gridHeight": 12,
    "itemCount": 4
  }
}
```

**Actual Validation Error**:
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "constraints", "gridWidth"],
      "msg": "Input should be less than or equal to 12",
      "input": 20
    },
    {
      "type": "less_than_equal",
      "loc": ["body", "constraints", "gridHeight"],
      "msg": "Input should be less than or equal to 8",
      "input": 12
    }
  ]
}
```

### Solution

**Option A**: Update documentation to show correct limits

```json
{
  "constraints": {
    "gridWidth": 12,    // max: 12
    "gridHeight": 8,    // max: 8
    "itemCount": 4
  }
}
```

**Option B**: Update validation to match documented limits

File: `/illustrator/v1.0/app/models/layout_service_request.py`

```python
class LayoutServiceConstraints(BaseModel):
    gridWidth: int = Field(..., ge=1, le=20)   # Change from le=12
    gridHeight: int = Field(..., ge=1, le=12)  # Change from le=8
    itemCount: Optional[int] = None
```

### Priority

**MEDIUM** - Documentation/validation mismatch

---

## Issue #3: Legacy Endpoint Undocumented Schema (DOCUMENTATION)

### Description

The `POST /v1.0/generate` legacy endpoint requires template-specific field names that are not documented in the contract.

### Impact

- Cannot use legacy endpoint without reverse-engineering template requirements
- No programmatic way to discover required fields

### Evidence

**Documented Request Schema**:
```json
{
  "illustration_type": "pyramid",
  "variant_id": "base",
  "data": {
    "levels": [
      {"label": "Vision", "description": "Long-term goals"}
    ]
  },
  "theme": "professional",
  "size": "medium",
  "output_format": "html"
}
```

**Actual Error**:
```json
{
  "detail": {
    "error_type": "validation_error",
    "message": "Missing required field in data: 'level_4_label'. Template expects this placeholder but it wasn't provided.",
    "suggestions": [
      "Check data structure for pyramid",
      "Use GET /v1.0/illustration/pyramid for schema"
    ]
  }
}
```

The endpoint requires specific field names like:
- `level_1_label`, `level_1_bullet_1`, `level_1_bullet_2`, `level_1_bullet_3`, `level_1_bullet_4`
- `level_2_label`, `level_2_bullet_1`, etc.

### Solution

**Option A**: Add schema endpoint for each template

```
GET /v1.0/illustration/{type}/schema
```

Returns:
```json
{
  "illustration_type": "pyramid",
  "variant": "4",
  "required_fields": [
    "level_1_label", "level_1_bullet_1", "level_1_bullet_2",
    "level_1_bullet_3", "level_1_bullet_4",
    "level_2_label", "level_2_bullet_1", ...
  ],
  "field_constraints": {
    "level_1_label": {"max_chars": 15},
    "level_1_bullet_1": {"max_chars": 25}
  }
}
```

**Option B**: Deprecate legacy endpoint

Mark `POST /v1.0/generate` as deprecated in documentation and direct users to use the LLM-powered endpoints instead:
- `POST /v1.0/pyramid/generate`
- `POST /v1.0/funnel/generate`
- `POST /v1.0/concentric_circles/generate`
- `POST /concept-spread/generate`

### Priority

**LOW** - Legacy endpoint, LLM-powered endpoints are preferred

---

## Issue #4: Themes Field Name Inconsistency (MINOR)

### Description

The contract documents `colors` object but actual response uses `palette`.

### Impact

- Minor inconsistency between documentation and implementation
- Could cause issues for clients relying on documented field names

### Evidence

**Documented Schema**:
```json
{
  "themes": [
    {
      "name": "professional",
      "colors": {
        "primary": "#1e3a5f",
        "secondary": "#3b82f6"
      }
    }
  ]
}
```

**Actual Response**:
```json
{
  "themes": [
    {
      "name": "professional",
      "palette": {
        "primary": "#0066CC",
        "secondary": "#FF6B00"
      }
    }
  ]
}
```

### Solution

**Option A**: Update documentation to use `palette`

**Option B**: Update code to use `colors`

File: `/illustrator/v1.0/app/routes.py` (themes endpoint)

### Priority

**LOW** - Minor documentation inconsistency

---

## Summary of Required Changes

| Issue | Priority | Type | Fix Location |
|-------|----------|------|--------------|
| Missing infographic_html | CRITICAL | Code | pyramid_routes.py, funnel_routes.py, concentric_circles_routes.py |
| Grid constraints mismatch | MEDIUM | Doc or Code | ILLUSTRATOR_SERVICE_CAPABILITIES.md or layout_service_request.py |
| Legacy schema undocumented | LOW | Doc | ILLUSTRATOR_SERVICE_CAPABILITIES.md |
| Themes field name | LOW | Doc or Code | ILLUSTRATOR_SERVICE_CAPABILITIES.md or routes.py |

---

## Implementation Order

1. **Issue #1** - Missing `infographic_html` (blocks Layout Service)
2. **Issue #2** - Grid constraints (documentation clarity)
3. **Issue #4** - Themes field name (consistency)
4. **Issue #3** - Legacy endpoint (can deprecate instead)

---

## Test Files

All test outputs are stored in `/illustrator/v1.0/tests/outputs/` for reference.
