# Funnel & Pyramid API Endpoints - Quick Reference

**Date**: November 16, 2025
**For**: Director Agent v3.4 Integration

---

## 🔄 API Endpoint Comparison

### Pyramid Endpoint
```
POST /v1.0/pyramid/generate
```

### Funnel Endpoint
```
POST /v1.0/funnel/generate
```

**Key Difference**: Different paths, but **same architectural pattern**.

---

## 📋 Request/Response Patterns

Both endpoints follow the **identical pattern** with only parameter differences:

### Common Request Structure

```json
{
  // CORE PARAMETERS (different per type)
  "num_levels": 4,        // Pyramid: 3-6 levels
  "num_stages": 4,        // Funnel: 3-5 stages
  "topic": "string",      // Both: Main topic

  // SESSION TRACKING (identical)
  "presentation_id": "optional-string",
  "slide_id": "optional-string",
  "slide_number": 1,

  // CONTEXT (identical structure)
  "context": {
    "presentation_title": "string",
    "slide_purpose": "string",
    "industry": "string",
    "previous_slides": [...]  // Narrative continuity
  },

  // CUSTOMIZATION (identical)
  "target_points": ["Point 1", "Point 2"],
  "tone": "professional",
  "audience": "general",
  "theme": "professional",
  "size": "medium",
  "validate_constraints": true
}
```

### Common Response Structure

Both return **identical response format**:

```json
{
  "success": true,
  "html": "<div>...</div>",  // Complete visualization HTML
  "metadata": {
    "num_levels": 4,          // or num_stages for funnel
    "template_file": "4.html",
    "generation_time_ms": 2450,
    "attempts": 1,
    "model": "gemini-2.0-flash-exp"
  },
  "generated_content": {
    // Pyramid: level_N_label, level_N_description
    // Funnel: stage_N_name, stage_N_bullet_1/2/3
  },
  "character_counts": {...},
  "validation": {
    "valid": true,
    "violations": []
  },
  "generation_time_ms": 2450,

  // SESSION ECHOING (identical)
  "presentation_id": "echoed-value",
  "slide_id": "echoed-value",
  "slide_number": 1
}
```

---

## 🔧 Director Client Integration

### File to Update
```
agents/director_agent/v3.4/src/clients/illustrator_client.py
```

### Method to Add

The `generate_funnel()` method is **already specified** in the updated integration document. Here's a quick reference:

```python
async def generate_funnel(
    self,
    num_stages: int,
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
    Generate a funnel visualization with AI-generated content.

    Returns same structure as generate_pyramid()
    """
    payload = {
        "num_stages": num_stages,
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

    # Add context (including previous_slides)
    if context:
        payload["context"] = context

    if target_points:
        payload["target_points"] = target_points

    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.post(
            f"{self.base_url}/v1.0/funnel/generate",
            json=payload
        )

    return response.json()
```

---

## 📍 Service Registry Updates

### File to Update
```
agents/director_agent/v3.4/src/utils/service_registry.py
```

### Updated Configuration

```python
"illustrator_service": ServiceConfig(
    enabled=True,
    base_url="http://localhost:8000",
    slide_types=[
        "pyramid",
        "funnel",  # ✅ ADDED
    ],
    endpoints={
        "pyramid": ServiceEndpoint(
            path="/v1.0/pyramid/generate",
            method="POST",
            timeout=60
        ),
        "funnel": ServiceEndpoint(  # ✅ ADDED
            path="/v1.0/funnel/generate",
            method="POST",
            timeout=60
        )
    }
),
```

---

## 🎯 Usage Examples

### Pyramid Example
```python
# Director calls Illustrator
result = await illustrator_client.generate_pyramid(
    num_levels=4,
    topic="Organizational Hierarchy",
    context={
        "presentation_title": "Company Overview",
        "industry": "Technology"
    },
    target_points=["Vision", "Strategy", "Operations", "Execution"]
)

# Use result['html'] in L25 layout
```

### Funnel Example
```python
# Director calls Illustrator
result = await illustrator_client.generate_funnel(
    num_stages=4,
    topic="Sales Conversion Funnel",
    context={
        "presentation_title": "Q4 Sales Strategy",
        "industry": "B2B SaaS"
    },
    target_points=["Leads", "Qualification", "Proposal", "Closed-Won"]
)

# Use result['html'] in L25 layout
```

---

## ✅ Integration Checklist

### Illustrator Service (Done ✅)
- [x] Funnel endpoint implemented
- [x] Character constraint validation
- [x] LLM service integration (Gemini 2.5 Flash)
- [x] Session field echoing
- [x] Previous slides context support
- [x] Test script created

### Director Agent (To Do 📋)
- [ ] Add `generate_funnel()` to `illustrator_client.py`
- [ ] Update `service_registry.py` with funnel endpoint
- [ ] Add funnel to Stage 4 strawman prompt
- [ ] Add funnel routing in `service_router_v1_2.py`
- [ ] Test end-to-end: Director → Illustrator → Layout Builder

---

## 🔗 Documentation Links

### Primary Integration Document (Updated)
```
/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/
  agents/director_agent/v3.4/docs/ILLUSTRATOR_INTEGRATION_PLAN.md
```

**What's New**:
- ✅ Funnel endpoint added to Service Registry (line 218)
- ✅ `generate_funnel()` method specification (line 399)
- ✅ Updated Future Extensibility section with funnel status
- ✅ Updated success criteria and completion status

### Illustrator Implementation Docs
```
/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/
  agents/illustrator/v1.0/FUNNEL_IMPLEMENTATION_COMPLETE.md
```

---

## 🚀 Quick Start

### 1. Test Funnel Endpoint Locally
```bash
cd agents/illustrator/v1.0
python main.py

# In separate terminal
python test_funnel_api.py
```

### 2. Verify API Response
```bash
curl -X POST http://localhost:8000/v1.0/funnel/generate \
  -H "Content-Type: application/json" \
  -d '{
    "num_stages": 4,
    "topic": "Sales Pipeline",
    "tone": "professional"
  }'
```

### 3. Add to Director Client
Copy the `generate_funnel()` method from the integration plan to your IllustratorClient.

### 4. Update Service Registry
Add funnel endpoint configuration as shown above.

### 5. Test End-to-End
Run Director with a funnel slide request and verify HTML generation.

---

## 📊 Key Differences Summary

| Aspect | Pyramid | Funnel |
|--------|---------|--------|
| **Endpoint** | `/v1.0/pyramid/generate` | `/v1.0/funnel/generate` |
| **Count Param** | `num_levels` (3-6) | `num_stages` (3-5) |
| **Content Fields** | `level_N_label`<br>`level_N_description` | `stage_N_name`<br>`stage_N_bullet_1/2/3` |
| **Constraints** | Labels: 5-20 chars<br>Descriptions: 50-60 chars | Names: 8-25 chars<br>Bullets: 30-60 chars each |
| **Templates** | `3.html`, `4.html`, `5.html`, `6.html` | `3.html`, `4.html`, `5.html` |
| **Status** | ✅ Production (Jan 2025) | ✅ Ready (Nov 16, 2025) |

---

## 💡 Best Practices

### When to Use Pyramid
- Hierarchical structures
- Organizational charts
- Skill development pathways
- Strategic layers (Vision → Strategy → Tactics)

### When to Use Funnel
- Sales pipelines
- Conversion funnels
- Customer journey stages
- Process narrowing/filtering

---

## 🎉 Summary

**The funnel endpoint is production-ready and follows the exact same pattern as pyramid!**

- ✅ Same request/response structure
- ✅ Same session tracking (presentation_id, slide_id, slide_number)
- ✅ Same context support (previous_slides for narrative)
- ✅ Same validation approach (character constraints)
- ✅ Same integration pattern with Director

**Only differences**:
1. Endpoint path (`/pyramid/generate` vs `/funnel/generate`)
2. Parameter name (`num_levels` vs `num_stages`)
3. Generated content field names

**Integration effort**: ~30 minutes (copy generate_funnel method + update service registry)
