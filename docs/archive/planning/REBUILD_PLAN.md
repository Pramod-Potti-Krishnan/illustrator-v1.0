# Illustrator Service v1.0 - Rebuild Implementation Plan

**Date**: 2025-01-14
**Status**: In Progress
**Approach**: Option A (Create all templates individually)

---

## 📋 Overview

Rebuilding illustration templates based on user feedback with new architecture:
- **5 Illustration Types** (down from 15)
- **26 Total Variants** across all types
- **Smart Layout Selection** (L02 for smaller variants, L25 for larger)

---

## ✅ Completed Work

### 1. Pyramid Templates ✅
**Status**: COMPLETE - Ready for Review
**Variants**: 4 (3-stage, 4-stage, 5-stage, 6-stage)
**Review URL**: https://web-production-f0d13.up.railway.app/p/4d964abe-9e85-4c7d-93aa-8da7edb829ea

**Templates Created**:
- ✅ `templates/pyramid/3.html` (L02 layout - centered)
- ✅ `templates/pyramid/4.html` (L02 layout - centered)
- ✅ `templates/pyramid/5.html` (L25 layout - with descriptions)
- ✅ `templates/pyramid/6.html` (L25 layout - with descriptions)

**Data Structure**:
```python
# 3-4 stage (simple labels only)
{
    "level_N_label": str  # For each level
}

# 5-6 stage (labels + descriptions)
{
    "level_N_label": str,
    "level_N_description": str  # For each level
}
```

**Layout Assignment**:
- 3-4 stages → L02 (diagram on left, text explanation on right)
- 5-6 stages → L25 (full rich content with integrated descriptions)

---

### 2. Funnel Templates ✅
**Status**: COMPLETE - Pending Review
**Variants**: 3 (3-stage, 4-stage, 5-stage)

**Templates Created**:
- ✅ `templates/funnel/3.html` (L25 layout)
- ✅ `templates/funnel/4.html` (L25 layout)
- ✅ `templates/funnel/5.html` (L25 layout)

**Data Structure**:
```python
{
    "stage_N_icon": str,          # Emoji or icon HTML
    "stage_N_title": str,         # Stage title
    "stage_N_description": str    # Stage description
}
```

**Reference**: Sales Funnel Infographics template
**Layout**: All use L25 (full-width rich content)

---

## 🚧 Pending Work

### 3. Horizontal Process Flow
**Status**: PENDING
**Variants**: 5 (3-step, 4-step, 5-step, 6-step, 7-step)
**Layout**: All use L25
**Reference**: 6-Step Horizontal Flow Diagram with semi-circles

**Templates to Create**:
- ⏳ `templates/horizontal_process/3.html`
- ⏳ `templates/horizontal_process/4.html`
- ⏳ `templates/horizontal_process/5.html`
- ⏳ `templates/horizontal_process/6.html`
- ⏳ `templates/horizontal_process/7.html`

**Data Structure**:
```python
{
    "step_N_icon": str,           # Icon/emoji
    "step_N_title": str,          # Step title
    "step_N_description": str     # Step description
}
```

**Design Features**:
- Horizontal flow with connecting line
- Semi-circle containers with icons
- Number badges (01, 02, etc.)
- Consistent spacing and alignment
- Color gradient across steps

---

### 4. Horizontal Timeline
**Status**: PENDING
**Variants**: 4 (4-event, 5-event, 6-event, 7-event)
**Layout**: All use existing layout (likely L25 or L02)
**Reference**: Horizontal Timeline Infographics with chevron arrows

**Templates to Create**:
- ⏳ `templates/timeline_horizontal/4.html`
- ⏳ `templates/timeline_horizontal/5.html`
- ⏳ `templates/timeline_horizontal/6.html`
- ⏳ `templates/timeline_horizontal/7.html`

**Data Structure**:
```python
{
    "event_N_date": str,          # Year or date
    "event_N_icon": str,          # Icon/emoji
    "event_N_title": str,         # Event title
    "event_N_description": str    # Event description
}
```

**Design Features**:
- Chevron arrow progression
- Icons above/below timeline
- Alternating text placement
- Year/date markers
- Connecting timeline bar

---

### 5. Concentric Circles
**Status**: PENDING
**Variants**: 4 (3-circle, 4-circle, 5-circle, 6-circle)
**Layout**: All use L25
**Reference**: Concentric Circle Nested Diagram

**Templates to Create**:
- ⏳ `templates/concentric_circles/3.html`
- ⏳ `templates/concentric_circles/4.html`
- ⏳ `templates/concentric_circles/5.html`
- ⏳ `templates/concentric_circles/6.html`

**Data Structure**:
```python
{
    "circle_N_label": str,        # Circle label
    "circle_N_icon": str,         # Icon/emoji
    "circle_N_description": str   # Description (displayed on side)
}
```

**Design Features**:
- Nested concentric circles
- Icons in each ring
- Labels positioned around circles
- Descriptions in side panel
- Color progression from center outward

---

## 🗑️ Templates to Remove

**Deprecated Templates** (Remove after new templates are complete):
- ❌ `templates/venn_2circle/` - User doesn't want Venn diagrams
- ❌ `templates/value_chain/` - Not needed
- ❌ `templates/circular_process/` - Replaced by concentric circles
- ❌ `templates/pyramid_3tier/` - Replaced by new pyramid variants
- ❌ `templates/funnel_4stage/` - Replaced by new funnel variants

---

## 🔧 Code Updates Required

### Layout Selector Updates
**File**: `app/core/layout_selector.py`

```python
@staticmethod
def get_layout(illustration_type: str, variant_id: str = None) -> str:
    """Get appropriate layout for illustration type and variant"""

    # Pyramid: L02 for 3-4, L25 for 5-6
    if illustration_type == "pyramid":
        stages = int(variant_id) if variant_id else 3
        return "L02" if stages <= 4 else "L25"

    # Funnel: All use L25
    elif illustration_type == "funnel":
        return "L25"

    # Horizontal Process: All use L25
    elif illustration_type == "horizontal_process":
        return "L25"

    # Timeline: All use L25 (or L02 if preferred)
    elif illustration_type == "timeline_horizontal":
        return "L25"

    # Concentric Circles: All use L25
    elif illustration_type == "concentric_circles":
        return "L25"

    else:
        return "L25"  # Default
```

### Content Builder Updates
**File**: `app/core/content_builder.py`

No major changes needed - existing `build_l25_response()` and `build_l02_response()` methods will work.

### Models/API Updates
**Files**: `app/models_v2.py`, `app/routes.py`

Update to reflect new illustration types:
```python
ILLUSTRATION_TYPES = [
    "pyramid",              # 3-6 variants
    "funnel",              # 3-5 variants
    "horizontal_process",  # 3-7 variants
    "timeline_horizontal", # 4-7 variants
    "concentric_circles"   # 3-6 variants
]
```

---

## 📊 Progress Tracking

### Summary Statistics
- **Total Illustration Types**: 5
- **Total Variants**: 26
  - Pyramid: 4 variants ✅
  - Funnel: 3 variants ✅
  - Horizontal Process: 5 variants ⏳
  - Timeline: 4 variants ⏳
  - Concentric Circles: 4 variants ⏳

### Completion Status
- ✅ Completed: 7 templates (27%)
- ⏳ Pending: 19 templates (73%)

---

## 🎯 Next Steps

### Immediate (Waiting for User)
1. **Review Pyramid Templates** at: https://web-production-f0d13.up.railway.app/p/4d964abe-9e85-4c7d-93aa-8da7edb829ea
2. **Provide Feedback** on design, colors, sizing, layout
3. **Approve to Continue** or request changes

### After Approval
1. Create Horizontal Process Flow templates (3-7 steps)
2. Create Horizontal Timeline templates (4-7 events)
3. Create Concentric Circles templates (3-6 circles)
4. Update layout selector and content builder
5. Generate comprehensive review presentation
6. Test all templates
7. Remove deprecated templates
8. Update documentation

---

## 🔄 Rollback Plan

If needed to revert:
1. Backup current templates: `cp -r templates templates_backup_$(date +%Y%m%d)`
2. Git checkout previous version
3. Restore old layout selector logic

---

## 📝 Notes

- All templates use professional blue theme (#2563EB primary)
- Responsive sizing with max-width/max-height constraints
- Hover effects for interactivity
- Consistent typography and spacing
- Grid-based layouts for alignment

---

**Last Updated**: 2025-01-14
**Next Review**: After pyramid feedback received
