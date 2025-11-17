# New Illustration Development Workflow (Modus Operandi)

**Purpose**: Standard operating procedure for building, integrating, and deploying new illustration types from concept to production.

**Version**: 1.0
**Last Updated**: November 16, 2025

---

## 📋 Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [Phase 1: Visual Design & HTML Iteration](#phase-1-visual-design--html-iteration)
3. [Phase 2: Variant Creation](#phase-2-variant-creation)
4. [Phase 3: User Validation](#phase-3-user-validation)
5. [Phase 4: Technical Implementation (Automated)](#phase-4-technical-implementation-automated)
6. [Phase 5: Director Integration](#phase-5-director-integration)
7. [Phase 6: End-to-End Testing](#phase-6-end-to-end-testing)
8. [Phase 7: Production Deployment](#phase-7-production-deployment)
9. [Quick Reference Checklist](#quick-reference-checklist)

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEW ILLUSTRATION LIFECYCLE                    │
└─────────────────────────────────────────────────────────────────┘

Phase 1: VISUAL DESIGN & ITERATION (User + Claude)
├── User provides: Picture/sketch/reference
├── Claude creates: First HTML variant
├── Iterate together: Refine until satisfied
└── ✅ Output: Approved base variant HTML

Phase 2: VARIANT CREATION (Claude)
├── Create variants: Different configurations (3-level, 4-level, etc.)
├── Apply constraints: Character limits per variant
└── ✅ Output: Complete variant set (3-6 variants)

Phase 3: USER VALIDATION (User)
├── Review all variants: Visual quality check
├── Test with sample content: Ensure flexibility
└── ✅ Output: All variants approved OR iterate

Phase 4: TECHNICAL IMPLEMENTATION (Claude - Automated)
├── Create constraint files: JSON specs per variant
├── Build validator: Character counting logic
├── Extend LLM service: Content generation methods
├── Create generator: Orchestration with retry logic
├── Build API endpoint: FastAPI route
├── Create test script: Comprehensive testing
└── ✅ Output: Complete working endpoint

Phase 5: DIRECTOR INTEGRATION (Claude - Automated)
├── Update service registry: Add new endpoint
├── Document integration: Update Director docs
└── ✅ Output: Director integration ready

Phase 6: END-TO-END TESTING (User + Claude)
├── User requests: "Generate slides with [new illustration]"
├── Director calls: New illustration endpoint
├── Validate output: Visual quality, content fit
├── Minor tweaks: Adjust constraints if needed
└── ✅ Output: Production-quality slides

Phase 7: PRODUCTION DEPLOYMENT
├── Mark as APPROVED: Update README, status docs
├── Archive old templates: If replacing illustration
└── ✅ REPEAT FOR NEXT ILLUSTRATION
```

---

## Phase 1: Visual Design & HTML Iteration

**Duration**: 30-60 minutes
**Participants**: User + Claude
**Goal**: Create and agree on base HTML variant

### Step 1.1: User Provides Visual Inspiration

**User provides ONE of**:
- Picture/screenshot of desired illustration
- Sketch or mockup
- Reference to existing illustration (PowerPoint, web, etc.)
- Verbal description with key visual elements

**Example**:
```
User: "I want a timeline illustration that shows 5 milestones horizontally
with dates above and descriptions below. Here's a picture [uploads image]."
```

### Step 1.2: Claude Creates First HTML Variant

**Claude actions**:
1. Analyze visual requirements
2. Choose implementation approach (HTML+CSS vs SVG)
3. Create complete HTML template with:
   - Embedded styles (`<style>` tag)
   - Semantic structure
   - Placeholder syntax: `{field_name}`
   - Sample content filled in
4. Save as: `templates/[illustration_type]/base_variant.html`

**Deliverable**: Working HTML file that renders in browser

### Step 1.3: Iterate Together Until Satisfied

**Iteration cycle**:
```
Claude: "Here's the first version [shows HTML rendering]"
User: "Good, but make the circles bigger and add connecting lines"
Claude: [Updates HTML, shows new version]
User: "Perfect! I like this."
```

**Common iteration topics**:
- Colors and gradients
- Spacing and sizing
- Typography (font sizes, weights)
- Shapes (boxes, circles, arrows)
- Layout (horizontal vs vertical, alignment)

**Exit criteria**: User says "I approve this design" or "This looks good"

---

## Phase 2: Variant Creation

**Duration**: 30-45 minutes
**Participants**: Claude (mostly automated)
**Goal**: Create multiple configuration variants

### Step 2.1: Identify Variant Dimensions

**Claude asks user**:
```
"How many variants should this illustration support?"

Examples:
- Timeline: 3-milestone, 4-milestone, 5-milestone
- Pyramid: 3-level, 4-level, 5-level, 6-level
- Matrix: 2x2, 3x3
- Process Flow: 3-step, 4-step, 5-step, 6-step
```

**User responds**: "Create 3, 4, and 5-milestone variants"

### Step 2.2: Create Variant Templates

**Claude creates**:
```
templates/timeline/
├── 3.html  (3 milestones)
├── 4.html  (4 milestones)
└── 5.html  (5 milestones)
```

**Each variant**:
- Based on approved base design
- Adjusted for different counts (more/fewer elements)
- Mathematically calculated spacing/sizing
- Consistent visual style across variants

### Step 2.3: Define Character Constraints

**Claude creates**: `app/variant_specs/[illustration]_constraints.json`

**Example** (timeline_constraints.json):
```json
{
  "timeline_3": {
    "milestone_1": {
      "date": [8, 12],           // "Jan 2024" or "Q1 2024"
      "title": [15, 30],         // "Product Launch"
      "description": [40, 60]    // "Launched beta version..."
    },
    "milestone_2": { ... },
    "milestone_3": { ... }
  },
  "timeline_4": { ... },
  "timeline_5": { ... }
}
```

**Constraints based on**:
- Visual space available in template
- Readability (not too cramped)
- Typical content patterns

---

## Phase 3: User Validation

**Duration**: 15-30 minutes
**Participants**: User
**Goal**: Validate all variants work correctly

### Step 3.1: Claude Generates Sample Content

**Claude creates test file**: `test_[illustration]_variants.html`

**Shows each variant with**:
- Sample realistic content
- Different content lengths (short, medium, long)
- Edge cases (longest allowed text, shortest)

**Example**:
```html
<!-- Shows 3-milestone, 4-milestone, 5-milestone side by side -->
<!-- Each with different sample content -->
```

### Step 3.2: User Reviews All Variants

**User checks**:
- ✅ All variants render correctly
- ✅ Content fits well (not cramped, not too sparse)
- ✅ Consistent visual style across variants
- ✅ Placeholders work correctly
- ✅ Edge cases handled gracefully

**Possible outcomes**:
1. **All approved**: Proceed to Phase 4
2. **Need adjustments**: Return to Phase 1 or 2
3. **Reject specific variant**: Remove from set

### Step 3.3: Final Approval

**User confirms**: "All variants approved. Proceed with implementation."

---

## Phase 4: Technical Implementation (Automated)

**Duration**: 45-60 minutes
**Participants**: Claude (fully automated)
**Goal**: Create complete working API endpoint

**User triggers**: "Build the endpoint for [illustration_type]"

### Step 4.1: Create Validator (Layer 4)

**Claude creates**: `app/core/[illustration]_validator.py`

```python
class TimelineValidator:
    def __init__(self):
        # Load constraints from JSON
        constraints_path = "app/variant_specs/timeline_constraints.json"
        with open(constraints_path) as f:
            self.all_constraints = json.load(f)

    def validate_content(self, content: Dict, num_milestones: int):
        """Validate against character constraints"""
        # HTML-aware character counting
        # Field-level violation reporting
        # Return (is_valid, violations)
```

**Features**:
- HTML-aware character counting (strips tags)
- Field-level violation details
- Singleton pattern (`get_timeline_validator()`)

### Step 4.2: Extend LLM Service (Layer 3)

**Claude modifies**: `app/llm_services/llm_service.py`

**Adds methods**:
```python
async def generate_timeline_content(
    self,
    topic: str,
    num_milestones: int,
    context: Dict[str, Any],
    constraints: Dict[str, Dict[str, list]],
    target_points: Optional[list] = None,
    tone: str = "professional",
    audience: str = "general"
) -> Dict[str, Any]:
    """Generate timeline content with constraints"""

    # Build constraint-driven prompt
    # Inject previous_slides context
    # Enforce JSON schema
    # Return structured content
```

**Adds service getter**:
```python
def get_timeline_service() -> GeminiService:
    """Uses LLM_TIMELINE environment variable"""
    global _timeline_service
    if _timeline_service is None:
        model_name = os.getenv("LLM_TIMELINE", "gemini-2.0-flash-exp")
        _timeline_service = GeminiService(model_name=model_name)
    return _timeline_service
```

### Step 4.3: Create Generator (Layer 2)

**Claude creates**: `app/llm_services/[illustration]_generator.py`

```python
class TimelineGenerator:
    def __init__(self):
        self.llm_service = get_timeline_service()
        self.validator = get_timeline_validator()

    async def generate_timeline_data(
        self,
        num_milestones: int,
        topic: str,
        context: Dict[str, Any],
        validate_constraints: bool = True,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """Orchestrate generation with retry logic"""

        # Get constraints for variant
        # Retry loop (max 2 attempts)
        # Call LLM service
        # Validate content
        # Return with metadata
```

**Features**:
- Retry logic on validation failures
- Performance tracking
- Comprehensive error handling

### Step 4.4: Create Pydantic Models

**Claude modifies**: `app/models.py`

**Adds request model**:
```python
class TimelineGenerationRequest(BaseModel):
    num_milestones: int = Field(..., ge=3, le=5)
    topic: str = Field(..., min_length=3)

    # Session tracking (Director alignment)
    presentation_id: Optional[str] = None
    slide_id: Optional[str] = None
    slide_number: Optional[int] = None

    # Context
    context: Dict[str, Any] = Field(default_factory=dict)
    target_points: Optional[List[str]] = None

    # Configuration
    tone: str = Field(default="professional")
    audience: str = Field(default="general")
    theme: str = Field(default="professional")
    size: str = Field(default="medium")
    validate_constraints: bool = Field(default=True)
```

**Adds response model**:
```python
class TimelineGenerationResponse(BaseModel):
    success: bool
    html: str  # Complete timeline HTML
    metadata: Dict[str, Any]
    generated_content: Dict[str, str]
    character_counts: Dict[str, Dict[str, int]]
    validation: Dict[str, Any]
    generation_time_ms: int

    # Session echoing
    presentation_id: Optional[str] = None
    slide_id: Optional[str] = None
    slide_number: Optional[int] = None
```

### Step 4.5: Create API Route (Layer 1)

**Claude creates**: `app/api_routes/[illustration]_routes.py`

```python
@router.post("/v1.0/timeline/generate", response_model=TimelineGenerationResponse)
async def generate_timeline_with_llm(request: TimelineGenerationRequest):
    """Generate timeline illustration using LLM"""

    start_time = time.time()

    # Generate content
    generator = get_timeline_generator()
    gen_result = await generator.generate_timeline_data(...)

    # Load template
    template_path = f"templates/timeline/{request.num_milestones}.html"
    template_html = load_template(template_path)

    # Fill placeholders
    filled_html = fill_template(template_html, gen_result["content"])

    # Clean unfilled placeholders
    filled_html = cleanup_placeholders(filled_html)

    # Echo session fields
    return TimelineGenerationResponse(
        success=True,
        html=filled_html,
        generated_content=gen_result["content"],
        validation=gen_result["validation"],
        metadata=gen_result["metadata"],
        generation_time_ms=int((time.time() - start_time) * 1000),
        presentation_id=request.presentation_id,
        slide_id=request.slide_id,
        slide_number=request.slide_number
    )
```

### Step 4.6: Register Router

**Claude modifies**: `main.py`

```python
from app.api_routes.timeline_routes import router as timeline_router

app.include_router(timeline_router)

# Update root endpoint
@app.get("/")
async def root():
    return {
        "endpoints": {
            "pyramid_generate": "POST /v1.0/pyramid/generate (LLM-powered)",
            "funnel_generate": "POST /v1.0/funnel/generate (LLM-powered)",
            "timeline_generate": "POST /v1.0/timeline/generate (LLM-powered)"  # NEW
        }
    }
```

### Step 4.7: Update Environment Configuration

**Claude modifies**: `.env.example`

```bash
# Timeline-specific LLM Model
LLM_TIMELINE=gemini-2.0-flash-exp
```

### Step 4.8: Create Test Script

**Claude creates**: `test_[illustration]_api.py`

```python
"""Test script for Timeline Generation API"""

async def test_timeline_generation(num_milestones, topic, context):
    """Test timeline generation with specific parameters"""

    payload = {
        "num_milestones": num_milestones,
        "topic": topic,
        "context": context,
        "tone": "professional",
        "validate_constraints": True
    }

    response = await client.post(
        f"{BASE_URL}/v1.0/timeline/generate",
        json=payload
    )

    # Save HTML output
    # Report generation time
    # Show validation results

async def main():
    """Run comprehensive tests"""

    # Test 3-milestone timeline
    await test_timeline_generation(3, "Product Launch Timeline", {...})

    # Test 4-milestone timeline
    await test_timeline_generation(4, "Project Milestones", {...})

    # Test 5-milestone timeline
    await test_timeline_generation(5, "Company Growth Journey", {...})

    # Test with previous_slides context
    await test_timeline_generation(4, "Development Roadmap", {
        "previous_slides": [...]
    })
```

### Step 4.9: Automated Verification

**Claude runs**:
1. Start service: `python main.py`
2. Run test script: `python test_timeline_api.py`
3. Verify all variants generate correctly
4. Check character constraints validated
5. Confirm HTML renders properly

**Claude reports**: "✅ Timeline endpoint implementation complete and tested"

---

## Phase 5: Director Integration

**Duration**: 15-20 minutes
**Participants**: Claude (fully automated)
**Goal**: Update Director integration documentation

### Step 5.1: Update Service Registry

**Claude modifies**: `agents/director_agent/v3.4/src/utils/service_registry.py`

**Adds timeline configuration**:
```python
"illustrator_service": ServiceConfig(
    enabled=True,
    base_url="http://localhost:8000",
    slide_types=[
        "pyramid",
        "funnel",
        "timeline",  # ✅ ADDED
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
        "timeline": ServiceEndpoint(  # ✅ ADDED
            path="/v1.0/timeline/generate",
            method="POST",
            timeout=60
        )
    }
)
```

### Step 5.2: Update Director Integration Plan

**Claude modifies**: `agents/director_agent/v3.4/docs/ILLUSTRATOR_INTEGRATION_PLAN.md`

**Adds**:
1. Timeline endpoint to Service Registry section
2. `generate_timeline()` method specification for IllustratorClient
3. Updated success criteria

**Example method specification**:
```python
async def generate_timeline(
    self,
    num_milestones: int,
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
    """Generate timeline visualization with AI-generated content"""

    payload = {
        "num_milestones": num_milestones,
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
            f"{self.base_url}/v1.0/timeline/generate",
            json=payload
        )

    return response.json()
```

### Step 5.3: Create Quick Reference Guide

**Claude creates**: `agents/illustrator/v1.0/TIMELINE_DIRECTOR_INTEGRATION_GUIDE.md`

**Includes**:
- API endpoint details
- Request/response examples
- Integration checklist for Director team
- Usage examples
- Key differences from pyramid/funnel

### Step 5.4: Notify User

**Claude says**:
```
✅ Director integration documentation complete!

Updated files:
1. agents/director_agent/v3.4/src/utils/service_registry.py
2. agents/director_agent/v3.4/docs/ILLUSTRATOR_INTEGRATION_PLAN.md
3. agents/illustrator/v1.0/TIMELINE_DIRECTOR_INTEGRATION_GUIDE.md

Ready to notify Director team: "Timeline endpoint is ready for integration"
```

---

## Phase 6: End-to-End Testing

**Duration**: 30-60 minutes
**Participants**: User + Claude + Director Service
**Goal**: Validate complete workflow from Director to slide output

### Step 6.1: User Requests Slide Generation

**User says**:
```
"Generate a presentation with a timeline slide:

Presentation: Q4 Product Roadmap
Slide 5: Development Timeline
Topic: Major feature releases over next 6 months
```

### Step 6.2: Director Orchestration

**Director workflow**:
1. Receives user request
2. Identifies need for timeline illustration
3. Determines `num_milestones=4` based on topic
4. Builds context with previous slides
5. Calls Illustrator timeline endpoint:
   ```python
   response = await illustrator_client.generate_timeline(
       num_milestones=4,
       topic="Major feature releases over next 6 months",
       presentation_id="pres-001",
       slide_id="slide-5",
       slide_number=5,
       context={
           "presentation_title": "Q4 Product Roadmap",
           "previous_slides": [...]
       }
   )
   ```
6. Receives HTML from Illustrator
7. Assembles complete slide with layout
8. Returns to user

### Step 6.3: User Validates Output

**User checks**:
- ✅ Timeline renders correctly
- ✅ Content is relevant and coherent
- ✅ Visual quality matches expectations
- ✅ Character constraints respected (no overflow)
- ✅ Narrative continuity with previous slides

**Possible outcomes**:

**A. Perfect** → "Looks great! Approved for production"

**B. Minor tweaks needed** → "Timeline is good but dates are too long"
   - Claude adjusts constraints in `timeline_constraints.json`
   - Regenerate to verify fix
   - User validates again

**C. Major issues** → Return to Phase 1 or 2 to redesign

### Step 6.4: Iterate on Constraints (if needed)

**Common adjustment scenarios**:

**Scenario 1: Text too long**
```
User: "The milestone descriptions are getting cut off"

Claude:
1. Checks constraint: "description": [40, 60]
2. Increases to: "description": [40, 80]
3. Regenerates test slides
4. User validates: "Perfect now!"
```

**Scenario 2: Text too short (wasted space)**
```
User: "There's a lot of empty space, can we fit more content?"

Claude:
1. Checks constraint: "description": [30, 40]
2. Increases to: "description": [40, 60]
3. Adjusts LLM prompt to generate more detailed content
4. User validates
```

**Scenario 3: Visual layout issue**
```
User: "When there are 5 milestones, they're too cramped"

Claude:
1. Reviews template: templates/timeline/5.html
2. Adjusts spacing/sizing in CSS
3. Regenerates
4. User validates
```

---

## Phase 7: Production Deployment

**Duration**: 10-15 minutes
**Participants**: Claude
**Goal**: Mark illustration as APPROVED and prepare for next

### Step 7.1: Update Status Documentation

**Claude updates**: `agents/illustrator/v1.0/README.md`

**Changes**:
```markdown
## ✅ Currently Supported Illustrations

- **Pyramid** (3-6 levels) - ✅ **APPROVED** - Production ready
- **Funnel** (3-5 stages) - ✅ **APPROVED** - Production ready
- **Timeline** (3-5 milestones) - ✅ **APPROVED** - Production ready  ← NEW
```

### Step 7.2: Create Implementation Summary

**Claude creates**: `agents/illustrator/v1.0/TIMELINE_IMPLEMENTATION_COMPLETE.md`

**Includes**:
- Complete implementation details
- All files created/modified
- Constraint specifications
- Director integration status
- Test results
- Success criteria checklist

### Step 7.3: Archive Old Templates (if replacing)

**If timeline REPLACES an old illustration**:
```bash
# Move old timeline to archive
mv templates/timeline_old templates/archive/timeline_old

# Update ARCHIVED_TEMPLATES.md
# Explain why replaced
```

### Step 7.4: Production Readiness Checklist

**Claude verifies**:
- [x] All variants tested and working
- [x] Character constraints validated
- [x] LLM generation successful (>90% pass rate)
- [x] Director integration documented
- [x] End-to-end test passed
- [x] Status docs updated
- [x] README updated
- [x] Implementation summary created

### Step 7.5: Ready for Next Illustration

**Claude confirms**:
```
✅ Timeline illustration is APPROVED and production-ready!

Summary:
- 3 variants created (3, 4, 5 milestones)
- API endpoint: POST /v1.0/timeline/generate
- Director integration: Complete
- Status: APPROVED

Ready to repeat workflow for next illustration.
```

---

## Quick Reference Checklist

### For Each New Illustration

**Phase 1: Design** (30-60 min)
- [ ] User provides picture/reference
- [ ] Claude creates first HTML variant
- [ ] Iterate together until approved
- [ ] Save base template

**Phase 2: Variants** (30-45 min)
- [ ] Define variant dimensions (3-level, 4-level, etc.)
- [ ] Create variant templates
- [ ] Define character constraints (JSON)
- [ ] Document constraints rationale

**Phase 3: Validation** (15-30 min)
- [ ] Generate sample content for all variants
- [ ] User reviews and approves all variants
- [ ] Confirm constraints are appropriate

**Phase 4: Implementation** (45-60 min) ⚡ AUTOMATED
- [ ] Create validator (`[illustration]_validator.py`)
- [ ] Extend LLM service (add generation methods)
- [ ] Create generator (`[illustration]_generator.py`)
- [ ] Add Pydantic models (request/response)
- [ ] Create API route (`[illustration]_routes.py`)
- [ ] Register router in `main.py`
- [ ] Update `.env.example` (LLM_[ILLUSTRATION])
- [ ] Create test script (`test_[illustration]_api.py`)
- [ ] Run tests and verify

**Phase 5: Integration** (15-20 min) ⚡ AUTOMATED
- [ ] Update Director service registry
- [ ] Update Director integration plan
- [ ] Create quick reference guide
- [ ] Notify Director team

**Phase 6: E2E Testing** (30-60 min)
- [ ] User requests slide with new illustration
- [ ] Director calls endpoint
- [ ] Validate output quality
- [ ] Adjust constraints if needed
- [ ] User final approval

**Phase 7: Deployment** (10-15 min)
- [ ] Update README (mark as APPROVED)
- [ ] Create implementation summary
- [ ] Archive old templates (if replacing)
- [ ] Verify production readiness checklist

**Total Time**: ~3-4 hours per illustration (from concept to production)

---

## Success Criteria

### Technical Success
- ✅ All API endpoints respond correctly
- ✅ Character constraint validation works
- ✅ LLM generation success rate >90%
- ✅ HTML renders correctly in all variants
- ✅ Session field echoing works
- ✅ Previous slides context integrates properly

### Quality Success
- ✅ Visual output matches approved design
- ✅ Content fits well in all variants
- ✅ Consistent style across variants
- ✅ No visual artifacts or rendering issues
- ✅ Readability maintained across content lengths

### Integration Success
- ✅ Director can successfully call endpoint
- ✅ Complete workflow from request to slide works
- ✅ Narrative continuity maintained
- ✅ Session tracking works correctly
- ✅ Error handling graceful

### User Success
- ✅ User approves visual quality
- ✅ Generated slides meet expectations
- ✅ Workflow is repeatable and efficient
- ✅ Documentation is clear and complete

---

## Tips for Smooth Workflow

### During Design (Phase 1)
- **Keep iterations focused**: Change one thing at a time
- **Use browser DevTools**: Quick CSS adjustments
- **Test with realistic content**: Don't use "Lorem ipsum"
- **Consider edge cases**: Very long text, very short text

### During Implementation (Phase 4)
- **Follow pyramid pattern exactly**: Proven architecture
- **Test locally first**: Don't wait for Director integration
- **Use descriptive variable names**: `milestone_1_date` not `m1d`
- **Log comprehensively**: Debug future issues easily

### During Testing (Phase 6)
- **Test all variants**: Don't just test one configuration
- **Test edge cases**: Maximum characters, minimum characters
- **Test with context**: Include previous_slides in tests
- **Document issues clearly**: Makes fixes faster

---

## Common Issues & Solutions

### Issue: LLM generates content too long
**Solution**:
1. Strengthen constraint language in prompt
2. Add explicit examples of correct length
3. Lower max_chars constraint by 10-20%

### Issue: HTML rendering breaks with certain content
**Solution**:
1. Test template with edge case content
2. Add CSS overflow handling
3. Validate HTML structure

### Issue: Constraints too restrictive
**Solution**:
1. Test with real user content
2. Adjust constraints based on actual needs
3. Balance visual quality vs content flexibility

### Issue: Director integration fails
**Solution**:
1. Verify endpoint paths match exactly
2. Check session field echoing
3. Test with minimal payload first
4. Review Director logs for errors

---

## Next Illustration Ideas

**Ready to implement** (following this workflow):
- Process Flow (3-6 steps, horizontal or vertical)
- Comparison Matrix (2x2, 3x3, side-by-side)
- Circular Process (3-8 stages in a cycle)
- Organization Chart (2-4 levels hierarchical)
- Gantt Timeline (project tasks with duration bars)
- Venn Diagram (2-3 overlapping circles)
- SWOT Analysis (2x2 grid with categories)

**Pick one and start Phase 1!** 🚀

---

**End of Workflow Document**

**Remember**: This is a proven, repeatable process. Follow it systematically for every new illustration, and you'll have production-ready endpoints in 3-4 hours.
