# Illustrator API Design Principles

**Purpose**: This document captures the core design principles, architectural patterns, and best practices extracted from production illustration implementations. These principles should guide all future illustration endpoint development.

**Source**: Pyramid API (v1.0), Funnel Templates, Concentric Circle Templates - Production-ready implementations
**Last Updated**: 2025-11-18

---

## Table of Contents

1. [Core Architecture Principles](#core-architecture-principles)
2. [HTML Fragment Design Principles](#html-fragment-design-principles)
3. [Visual Design Patterns](#visual-design-patterns)
4. [Typography & Text Styling](#typography--text-styling)
5. [Color & Gradient Standards](#color--gradient-standards)
6. [Layout & Spacing Formulas](#layout--spacing-formulas)
7. [LLM Integration Best Practices](#llm-integration-best-practices)
8. [API Contract Design](#api-contract-design)
9. [Validation & Quality Assurance](#validation--quality-assurance)
10. [Template Architecture](#template-architecture)
11. [Environment Configuration](#environment-configuration)
12. [Integration with Director](#integration-with-director)
13. [Error Handling & Resilience](#error-handling--resilience)

---

## Core Architecture Principles

### 1. Stateless Service Design

**Principle**: The Illustrator service maintains NO server-side session state. Director is the sole "source of truth" for presentation context.

**Implementation**:
```python
# Director passes context IN every request
request = {
    "topic": "Product Strategy",
    "presentation_id": "pres-001",  # Optional - for correlation
    "slide_id": "slide-3",          # Optional
    "slide_number": 3,              # Optional
    "context": {
        "presentation_title": "Q4 Strategic Plan",
        "previous_slides": [...]    # Narrative continuity
    }
}

# Illustrator echoes session fields in response
response = {
    "success": true,
    "html": "<div>...</div>",
    "presentation_id": "pres-001",  # Echoed back
    "slide_id": "slide-3",          # Echoed back
    "slide_number": 3               # Echoed back
}
```

**Benefits**:
- Horizontal scaling (no session affinity)
- Simplified deployment (no session storage)
- Clear responsibility boundaries
- Aligns with Text Service v1.2 architecture

**Reference**: `agents/illustrator/v1.0/TEXT_SERVICE_ALIGNMENT_COMPLETE.md`

---

### 2. Three-Layer Architecture

**Principle**: Clear separation of concerns across orchestration, generation, and validation layers.

**Layer Structure**:
```
┌──────────────────────────────────┐
│   API Routes Layer               │  FastAPI endpoints
│   - Request validation           │  pyramid_routes.py
│   - Session field echoing        │
│   - Response assembly            │
└─────────────┬────────────────────┘
              ↓
┌──────────────────────────────────┐
│   Generator Layer                │  Business logic
│   - Orchestration                │  pyramid_generator.py
│   - Retry logic                  │
│   - Metadata assembly            │
└─────────────┬────────────────────┘
              ↓
┌──────────────────────────────────┐
│   LLM Service Layer              │  AI integration
│   - Prompt construction          │  llm_service.py
│   - Vertex AI calls              │
│   - JSON parsing                 │
└─────────────┬────────────────────┘
              ↓
┌──────────────────────────────────┐
│   Validation Layer               │  Quality assurance
│   - Constraint checking          │  pyramid_validator.py
│   - Character counting           │
│   - Violation reporting          │
└──────────────────────────────────┘
```

**Benefits**:
- Testable components (each layer can be unit tested)
- Easy to extend (add new layers without modifying existing)
- Clear debugging path (errors localized to specific layer)

---

### 3. Template-First Philosophy

**Principle**: Templates are pre-built, human-validated, and APPROVED before deployment. Runtime is simple placeholder substitution.

**Workflow**:
```
1. Design template in HTML+CSS
   ↓
2. Human review & validation
   ↓
3. Approve for production
   ↓
4. Deploy template file
   ↓
5. Runtime: LLM generates content → Fill placeholders
```

**Template Structure**:
```html
<!-- Pre-validated, fixed layout -->
<div class="pyramid-container">
    <div class="pyramid-level level-4">
        <div class="level-label">{level_4_label}</div>  <!-- Placeholder -->
    </div>
    <div class="description-text">{level_4_description}</div>
</div>
```

**Runtime Filling** (simple string replacement):
```python
filled_html = template_html
for key, value in generated_content.items():
    placeholder = f"{{{key}}}"
    filled_html = filled_html.replace(placeholder, value)
```

**Benefits**:
- Guaranteed visual quality (human-approved layouts)
- Fast runtime (no layout computation)
- Easy iteration (modify template, re-approve, deploy)
- No risk of LLM-generated broken HTML

**Reference**: `agents/illustrator/v1.0/README.md`

---

## HTML Fragment Design Principles

### 1. Fragment-Only Structure (No DOCTYPE or HTML Wrapper)

**Principle**: Templates are HTML fragments, NOT complete HTML documents. They will be embedded into Deck Builder slides.

**❌ WRONG - Complete HTML Document**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Pyramid</title>
    <style>
        .pyramid-container { ... }
    </style>
</head>
<body>
    <div class="pyramid-container">
        <!-- Content -->
    </div>
</body>
</html>
```

**✅ CORRECT - HTML Fragment**:
```html
<div class="funnel-container" style="margin: 0; padding: 40px 60px; box-sizing: border-box; width: 100%; height: 100%; max-width: 1800px; max-height: 720px; display: flex; align-items: center; justify-content: center; font-family: Arial, sans-serif; gap: 60px">
<!-- Funnel Visual (Left Side) -->
<div class="funnel-visual" style="margin: 0; padding: 0; box-sizing: border-box; flex: 0 0 40%; display: flex; flex-direction: column; align-items: center; gap: 10px">
    <!-- Content -->
</div>
</div>
```

**Why?**
- Deck Builder already has `<html>`, `<head>`, `<body>` structure
- Templates are injected into slide containers
- Multiple DOCTYPE declarations cause rendering issues
- No need for `<title>`, `<meta>` tags in fragments

**Railway Deployment Consideration**: Fragments render correctly in both preview and production environments.

---

### 2. Inline Styles Only (No External CSS)

**Principle**: ALL styles must be inline `style=""` attributes. No `<style>` tags, no external CSS files.

**❌ WRONG - Style Tag**:
```html
<style>
    .funnel-container {
        display: flex;
        gap: 60px;
    }
</style>
<div class="funnel-container">...</div>
```

**✅ CORRECT - Inline Styles**:
```html
<div class="funnel-container" style="display: flex; gap: 60px; margin: 0; padding: 40px 60px; box-sizing: border-box">...</div>
```

**Why?**
- Style tag content may be stripped by Deck Builder's sanitization
- Inline styles have highest specificity (won't be overridden)
- Fragments are self-contained (no dependency resolution)
- Prevents CSS conflicts between multiple slides

**Best Practice**:
```html
<!-- Always include these in every element's inline style -->
style="margin: 0; padding: 0; box-sizing: border-box; [additional styles]"
```

---

### 3. Reset Styles on Every Element

**Principle**: Every element should reset `margin`, `padding`, and `box-sizing` to prevent inheritance issues.

**Standard Reset Pattern**:
```html
<div style="margin: 0; padding: 0; box-sizing: border-box; [other styles]">
```

**Why?**
- Deck Builder may apply default styles to slides
- Browser default styles vary
- `box-sizing: border-box` makes width/height calculations predictable
- Prevents layout shifts when embedded

**Complete Element Example**:
```html
<div class="funnel-stage" style="margin: 0; padding: 0; box-sizing: border-box; width: 100%; display: flex; justify-content: center; position: relative">
    <div class="funnel-section" style="margin: 0; padding: 0; box-sizing: border-box; display: flex; align-items: center; justify-content: center; height: 120px; color: white">
        <span style="margin: 0; padding: 0; box-sizing: border-box; font-size: 18px; font-weight: 900">Stage 1</span>
    </div>
</div>
```

---

### 4. Maximum Dimensions for Slide Compatibility

**Principle**: All templates must fit within standard slide dimensions and be responsive.

**Standard Slide Canvas**:
```html
<div class="[template]-container" style="
    width: 100%;
    height: 100%;
    max-width: 1800px;   /* 16:9 presentation width */
    max-height: 720px;    /* Standard slide height */
    ...
">
```

**Responsive Scaling**:
- Use percentage widths for child elements: `flex: 0 0 45%`
- Use `max-width` and `max-height` to prevent overflow
- Test at multiple viewport sizes
- Ensure text remains readable when scaled

**Railway Production Note**: Templates render at various screen sizes. Always test responsive behavior.

---

## Visual Design Patterns

### 1. Icon Positioning Outside Legend Boxes

**Principle**: Number icons positioned OUTSIDE and to the LEFT of colored legend boxes using absolute positioning.

**Pattern Established** (from Concentric Circles, Funnels, Pyramids):
```html
<div class="legend-item" style="
    margin: 0;
    padding: 15px 30px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: linear-gradient(135deg, #c85a3d 0%, #b54935 100%);
    color: white;
    border-radius: 8px;
    position: relative;
    margin-left: 70px  /* Space for icon */
">
    <!-- Icon positioned OUTSIDE to the left -->
    <div class="icon" style="
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        position: absolute;
        left: -70px;           /* Positioned outside */
        top: 50%;
        transform: translateY(-50%)  /* Vertically centered */
    ">
        <div class="icon-inner" style="
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: 900;
            background: linear-gradient(135deg, #c85a3d 0%, #b54935 100%)
        ">1</div>
    </div>

    <!-- Content with bullets -->
    <ul style="list-style-type: disc; padding-left: 20px; color: white">
        <li>{bullet_1}</li>
        <li>{bullet_2}</li>
        <li>{bullet_3}</li>
    </ul>
</div>
```

**Key Dimensions**:
- Outer icon: `60px × 60px` (white circle with shadow)
- Inner icon: `50px × 50px` (colored circle with number)
- Icon font: `24px`, weight `900`
- Icon position: `left: -70px` (outside parent)
- Parent margin: `margin-left: 70px` (creates space for icon)
- Vertical centering: `top: 50%; transform: translateY(-50%)`

**Why This Pattern?**
- Visual hierarchy: Icons clearly mark each level
- Clean separation: Icons don't clutter content area
- Consistent alignment: All icons vertically centered
- Professional appearance: Floating icons create depth

**Used In**: Concentric Circles (3, 4, 5), Funnels (3, 4, 5), Pyramids (3, 4, 5, 6)

---

### 2. Gradient Backgrounds Matching Visual Elements

**Principle**: Legend/description boxes use gradient backgrounds that MATCH the colors of their corresponding visual elements (funnel stages, circles, pyramid levels).

**Pattern**:
```html
<!-- Funnel Stage 1 (Red gradient) -->
<div class="funnel-section" style="background: linear-gradient(135deg, #c85a3d 0%, #b54935 100%)">
    Stage 1
</div>

<!-- Legend Box 1 - SAME gradient -->
<div class="description-item" style="background: linear-gradient(135deg, #c85a3d 0%, #b54935 100%); color: white">
    <ul style="color: white">
        <li>Bullet 1</li>
        <li>Bullet 2</li>
    </ul>
</div>
```

**Color Coordination Examples**:

**Funnels**:
- Stage 1 (Red): `linear-gradient(135deg, #c85a3d 0%, #b54935 100%)`
- Stage 2 (Gold): `linear-gradient(135deg, #daa520 0%, #c49419 100%)`
- Stage 3 (Blue): `linear-gradient(135deg, #5b8db8 0%, #4a7ba0 100%)`
- Stage 4 (Green): `linear-gradient(135deg, #8ba846 0%, #7a9339 100%)`
- Stage 5 (Purple): `linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)`

**Pyramids**:
- Level 6/Top (Red): `linear-gradient(135deg, #ef4444 0%, #dc2626 100%)`
- Level 5 (Pink): `linear-gradient(135deg, #ec4899 0%, #db2777 100%)`
- Level 4 (Orange): `linear-gradient(135deg, #f59e0b 0%, #d97706 100%)`
- Level 3 (Purple): `linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)`
- Level 2 (Blue): `linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)`
- Level 1 (Green): `linear-gradient(135deg, #10b981 0%, #059669 100%)`

**Concentric Circles**:
- Circle 5 (Light Blue): `linear-gradient(135deg, #7eb3d5 0%, #6ba3c7 100%)`
- Circle 4 (Yellow): `linear-gradient(135deg, #f9c74f 0%, #f3b52e 100%)`
- Circle 3 (Gray): `linear-gradient(135deg, #9ca3af 0%, #848c99 100%)`
- Circle 2 (Orange): `linear-gradient(135deg, #f4a261 0%, #e8913f 100%)`
- Circle 1 (Blue): `linear-gradient(135deg, #4a90e2 0%, #3a7bc8 100%)`

**Gradient Angle**: Always `135deg` (diagonal top-left to bottom-right) for consistency.

---

### 3. Vertical Stacking with Flexbox Column

**Principle**: Legend boxes use `flex-direction: column` to stack icons and bullets vertically.

**Layout Pattern**:
```html
<div class="descriptions-column" style="
    display: flex;
    flex-direction: column;  /* Vertical stacking */
    gap: 10px;               /* Spacing between boxes */
">
    <div class="legend-item" style="
        display: flex;
        flex-direction: column;  /* Bullets stack vertically */
        justify-content: center; /* Vertical centering */
    ">
        <ul style="display: flex; flex-direction: column; gap: 3px">
            <li>Bullet 1</li>
            <li>Bullet 2</li>
            <li>Bullet 3</li>
        </ul>
    </div>
</div>
```

**Key Properties**:
- Parent container: `flex-direction: column` (stacks legend boxes)
- Individual box: `flex-direction: column` (stacks content vertically)
- Bullets list: `flex-direction: column; gap: 3px` (spacing between bullets)
- Centering: `justify-content: center` (vertically centers content in box)

**Why Column Layout?**
- Clean vertical flow: Natural reading order
- Consistent spacing: `gap` property handles spacing uniformly
- Easy alignment: Flexbox handles centering automatically
- Responsive: Stacks naturally on smaller screens

---

### 4. White Text on Colored Backgrounds

**Principle**: All text, bullets, and icons on colored gradient backgrounds use white color for maximum contrast and readability.

**Text Color Rules**:
```html
<!-- On colored backgrounds: ALWAYS white -->
<div style="background: linear-gradient(135deg, #c85a3d 0%, #b54935 100%); color: white">
    <span style="color: white">Label Text</span>
    <ul style="color: white">
        <li style="color: white">Bullet 1</li>
        <li style="color: white">Bullet 2</li>
    </ul>
</div>

<!-- Exception: Yellow backgrounds use dark text for contrast -->
<div style="background: linear-gradient(135deg, #f9c74f 0%, #f3b52e 100%); color: #2d3748">
    <ul style="color: #2d3748">
        <li>Bullet (dark text)</li>
    </ul>
</div>
```

**Contrast Standards**:
- White on dark gradients: `color: white` or `#ffffff`
- Dark on yellow: `color: #2d3748` (dark gray for readability)
- Always test contrast ratio (aim for WCAG AA: 4.5:1 minimum)

**Bullet Styling**:
```html
<ul style="
    list-style-type: disc;
    padding-left: 20px;
    color: white;         /* Bullet markers inherit this */
    font-size: 19.2px
">
    <li style="color: white">Bullet text</li>
</ul>
```

---

## Typography & Text Styling

### 1. Label Text Standards

**Principle**: Labels in visual elements (pyramid levels, funnel stages, circle labels) use consistent, bold, uppercase styling.

**Standard Label Style**:
```html
<div class="level-label" style="
    margin: 0;
    padding: 0 12px;
    box-sizing: border-box;
    color: white;
    font-size: 18px;           /* Standard label size */
    font-weight: 900;          /* Extra bold */
    text-align: center;
    text-transform: uppercase; /* ALL CAPS */
    letter-spacing: 1px        /* Slight spacing for readability */
">{level_label}</div>
```

**Label Dimensions**:
- Font size: `18px` (consistent across all templates)
- Font weight: `900` (maximum boldness)
- Letter spacing: `1px` (improves readability at small sizes)
- Text transform: `uppercase` (consistent capitalization)
- Text align: `center` (centered in container)

**Why These Values?**
- 18px: Large enough to read at slide scale, not overwhelming
- 900 weight: Ensures visibility against gradients
- Uppercase: Creates visual hierarchy, professional appearance
- 1px spacing: Prevents character crowding in uppercase

**Used In**: Pyramid levels, Funnel stages, Concentric circle labels

---

### 2. Bullet Text Standards

**Principle**: Bullets use slightly larger text (19.2px) for readability in description boxes.

**Standard Bullet Style**:
```html
<ul style="
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    list-style-type: disc;     /* Standard bullet points */
    padding-left: 20px;        /* Indent for bullet markers */
    display: flex;
    flex-direction: column;
    gap: 3px;                  /* Spacing between bullets */
    font-size: 19.2px;         /* Standard bullet size */
    color: white
">
    <li style="margin: 0; padding: 0; box-sizing: border-box">{bullet_text}</li>
</ul>
```

**Bullet Specifications**:
- Font size: `19.2px` (larger than labels for readability)
- List style: `disc` (standard filled circles)
- Padding left: `20px` (indents bullets from box edge)
- Gap: `3px` (vertical spacing between bullets)
- Line height: `1.2` (compact but readable)

**Bullet Count Standards**:
- 6-level templates: **2 bullets per item**
- 3, 4, 5-level templates: **3 bullets per item**
- Maximum: 3 bullets (avoids overcrowding)

**Why 19.2px?**
- 1.2× scale of 16px base (standard body text)
- Ensures readability in small description boxes
- Balances with 18px labels (slightly larger for emphasis)

---

### 3. Font Family Inheritance

**Principle**: Use `font-family: Arial, sans-serif` on container to ensure consistent font across all child elements.

**Container Font Declaration**:
```html
<div class="funnel-container" style="
    font-family: Arial, sans-serif;  /* Inherited by all children */
    ...
">
    <!-- All text inherits Arial unless overridden -->
    <div class="label">...</div>
    <ul class="bullets">...</ul>
</div>
```

**Why Arial?**
- Universal availability (installed on all systems)
- Clean, professional appearance
- Excellent readability at small sizes
- Sans-serif works well in presentations
- Fallback to `sans-serif` ensures rendering even if Arial missing

**Alternative Acceptable Fonts**:
- Helvetica (Mac preference)
- Roboto (modern, clean)
- Open Sans (web-friendly)

**Avoid**:
- Serif fonts (less readable at small sizes)
- Decorative fonts (unprofessional)
- Custom fonts (loading issues, compatibility)

---

### 4. Text Alignment in Visual Elements

**Principle**: Center all text both vertically and horizontally within visual elements (trapezoids, circles, pyramid levels).

**Centering Pattern**:
```html
<div class="funnel-section" style="
    display: flex;
    align-items: center;      /* Vertical centering */
    justify-content: center;  /* Horizontal centering */
    height: 120px;
    ...
">
    <span style="text-align: center">{stage_name}</span>
</div>
```

**Flexbox Centering Properties**:
- `display: flex` - Enable flexbox layout
- `align-items: center` - Vertically center children
- `justify-content: center` - Horizontally center children
- `text-align: center` - Center multi-line text

**Why Flexbox for Centering?**
- Works with any content size (no hardcoded offsets)
- Handles multi-line text gracefully
- Maintains centering when scaled
- Simple, declarative syntax

**Verified In**: Funnel 4 and 5 bottom trapezoids (user confirmed alignment is correct)

---

## Color & Gradient Standards

### 1. Gradient Direction and Angle

**Principle**: All gradients use `135deg` angle (diagonal from top-left to bottom-right) for visual consistency.

**Standard Gradient Syntax**:
```css
background: linear-gradient(135deg, [light-color] 0%, [dark-color] 100%);
```

**Examples**:
```html
<!-- Red gradient -->
background: linear-gradient(135deg, #c85a3d 0%, #b54935 100%);

<!-- Blue gradient -->
background: linear-gradient(135deg, #5b8db8 0%, #4a7ba0 100%);

<!-- Purple gradient -->
background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
```

**Why 135deg?**
- Creates subtle depth and dimension
- Light source appears from top-left (natural reading direction)
- Consistent across all templates (professional cohesion)
- Not too dramatic (45deg too subtle, 180deg too stark)

**Color Stops**: Always `0%` (start) and `100%` (end) for full coverage.

---

### 2. Color Palette Standards

**Principle**: Use a predefined color palette with tested contrast ratios and gradient pairs.

**Primary Palette** (Light → Dark pairs):

| Color Name | Light Shade | Dark Shade | Usage |
|------------|-------------|------------|-------|
| **Red** | `#c85a3d` | `#b54935` | Funnel 1, Pyramid 6 |
| **Pink** | `#ec4899` | `#db2777` | Pyramid 5 |
| **Gold** | `#daa520` | `#c49419` | Funnel 2 |
| **Orange** | `#f59e0b` | `#d97706` | Pyramid 4 |
| **Orange (alt)** | `#f4a261` | `#e8913f` | Circle 2 |
| **Yellow** | `#f9c74f` | `#f3b52e` | Circle 4 |
| **Green** | `#8ba846` | `#7a9339` | Funnel 4 |
| **Green (alt)** | `#10b981` | `#059669` | Pyramid 1 |
| **Blue (dark)** | `#3b82f6` | `#2563eb` | Pyramid 2 |
| **Blue (medium)** | `#5b8db8` | `#4a7ba0` | Funnel 3, Circle 3 |
| **Blue (light)** | `#7eb3d5` | `#6ba3c7` | Circle 5 |
| **Blue (bright)** | `#4a90e2` | `#3a7bc8` | Circle 1 |
| **Purple** | `#8b5cf6` | `#7c3aed` | Funnel 5, Pyramid 3 |
| **Gray** | `#9ca3af` | `#848c99` | Circle 3 |

**Gradient Generation Formula**:
```
Dark Shade = Light Shade - 10-15% brightness
```

**Testing Contrast**:
- White text on gradient: Minimum 4.5:1 ratio
- Use WebAIM Contrast Checker
- Test against darkest part of gradient

---

### 3. Icon Inner/Outer Circle Colors

**Principle**: Icon circles use matching gradients with white outer ring for depth.

**Two-Layer Icon Pattern**:
```html
<!-- Outer circle: White background -->
<div class="icon-outer" style="
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: white;              /* White ring */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: center
">
    <!-- Inner circle: Colored gradient matching legend box -->
    <div class="icon-inner" style="
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #c85a3d 0%, #b54935 100%);
        color: white;
        font-size: 24px;
        font-weight: 900;
        display: flex;
        align-items: center;
        justify-content: center
    ">1</div>
</div>
```

**Sizing Ratio**: 60px outer : 50px inner = 10px white ring

**Why Two Layers?**
- White ring creates visual separation from background
- Gradient inner circle matches legend box
- Shadow adds depth (floating effect)
- Number remains readable with white text on colored background

---

### 4. Border and Shadow Specifications

**Principle**: Use subtle shadows and borders to create depth without overwhelming design.

**Standard Box Shadow**:
```css
box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);  /* Soft shadow for icons */
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);  /* Lighter shadow for boxes */
```

**White Borders for Separation**:
```css
border: 4px solid white;  /* Concentric circles */
```

**Shadow Parameters**:
- X-offset: `0` (directly below)
- Y-offset: `4px` or `2px` (vertical drop)
- Blur: `8px` or `4px` (soft edges)
- Color: `rgba(0, 0, 0, 0.1)` (10% black, very subtle)

**When to Use**:
- Icons: `0 4px 8px` shadow
- Legend boxes: `0 2px 4px` shadow
- Visual elements with white borders: `border: 4px solid white`

---

## Layout & Spacing Formulas

### 1. Mathematical Pyramid Construction

**Principle**: Use mathematical formulas for proportional pyramid sizing instead of arbitrary values.

**Pyramid Height Formula**:
```
Given:
  H = Total height (80% of slide height = 576px for 720px slide)
  n = Number of trapezoids (excludes top triangle)

Calculate:
  h = H / (1.075n + 1.5)

Results:
  Triangle height = 1.5h
  Trapezoid height = h
  Gap between segments = 0.075h
```

**Calculated Dimensions**:

| Levels | n | h (trapezoid) | Triangle | Gap |
|--------|---|---------------|----------|-----|
| **6** | 5 | 84px | 126px | 6px |
| **5** | 4 | 99px | 149px | 7px |
| **4** | 3 | 122px | 183px | 9px |
| **3** | 2 | 158px | 237px | 12px |

**Implementation**:
```html
<!-- 6-level pyramid -->
<div class="pyramid-visual" style="gap: 6px">  <!-- Gap = 0.075h -->
    <!-- Triangle -->
    <div style="height: 126px">...</div>  <!-- 1.5h -->
    <!-- Trapezoids -->
    <div style="height: 84px">...</div>   <!-- h -->
    <div style="height: 84px">...</div>   <!-- h -->
    <div style="height: 84px">...</div>   <!-- h -->
    <div style="height: 84px">...</div>   <!-- h -->
    <div style="height: 84px">...</div>   <!-- h -->
</div>
```

**Benefits**:
- Proportional scaling across all pyramid variants
- Predictable spacing (gaps scale with height)
- Mathematical consistency (no arbitrary adjustments)
- Easy to extend (formula works for any level count)

**Reference**: Pyramid templates 3.html, 4.html, 5.html, 6.html

---

### 2. Container Padding and Gaps

**Principle**: Consistent padding around containers and gaps between elements for visual breathing room.

**Standard Container Padding**:
```html
<div class="container" style="padding: 40px 60px">
    <!-- 40px vertical, 60px horizontal -->
</div>

<!-- Alternative for tighter layouts -->
<div class="container" style="padding: 30px 50px">
    <!-- 30px vertical, 50px horizontal -->
</div>
```

**Element Gaps**:
```html
<!-- Between legend boxes -->
<div style="display: flex; flex-direction: column; gap: 10px">

<!-- Between funnel stages -->
<div style="display: flex; flex-direction: column; gap: 10px">

<!-- Between bullets -->
<ul style="display: flex; flex-direction: column; gap: 3px">
```

**Gap Standards**:
- Container padding: `40px` vertical, `60px` horizontal
- Between major sections: `50-60px`
- Between boxes: `10px`
- Between bullets: `3px`
- Between icon and box: `70px` (margin-left)

**Why These Values?**
- 40px/60px: Comfortable margins for 1800×720 canvas
- 10px: Visible separation without excess space
- 3px: Compact bullet spacing for readability
- 70px: Accommodates 60px icon + 10px clearance

---

### 3. Flexbox Proportions

**Principle**: Use flex ratios for responsive layouts that adapt to different screen sizes.

**Two-Column Layout Pattern**:
```html
<div class="container" style="display: flex; gap: 50px">
    <!-- Visual column (left) -->
    <div class="visual-column" style="flex: 0 0 45%">
        <!-- Pyramid, funnel, or circles -->
    </div>

    <!-- Description column (right) -->
    <div class="description-column" style="flex: 0 0 53%">
        <!-- Legend boxes with bullets -->
    </div>
</div>
```

**Flex Ratio Breakdown**:
- `flex: 0 0 45%` - Visual column
  - `0` - Don't grow
  - `0` - Don't shrink
  - `45%` - Fixed 45% width
- `flex: 0 0 53%` - Description column (remaining space)
- Gap: `50-60px` between columns

**Column Width Standards**:
- Funnel visual: `40%`, Description: `55%`
- Pyramid visual: `45%`, Description: `53%`
- Circles visual: `680px` (fixed), Description: `flex: 1` (fill)

**Why These Proportions?**
- Visual emphasis balanced with descriptive text
- Room for detailed bullets without crowding
- Works well when scaled down for mobile

---

### 4. Height Calculation for Matching Elements

**Principle**: Visual elements and their corresponding legend boxes must have identical heights for visual alignment.

**Height Matching Pattern**:
```html
<!-- Funnel stage: height 120px -->
<div class="funnel-section" style="height: 120px">
    Stage 1
</div>

<!-- Corresponding legend box: SAME height -->
<div class="legend-item" style="height: 120px">
    <ul>
        <li>Bullet 1</li>
        <li>Bullet 2</li>
        <li>Bullet 3</li>
    </ul>
</div>
```

**Height Standards**:
- **Funnel 3-stage**: Trapezoid `163px`, Box `163px`
- **Funnel 4-stage**: Trapezoid `120px`, Box `120px`
- **Funnel 5-stage**: Trapezoid `94px`, Box `94px`
- **Pyramid 6-level**: Triangle `126px`, Box `126px`; Trapezoid `84px`, Box `84px`

**Gap Matching**: Gap between visual elements = Gap between legend boxes

**Why Match Heights?**
- Visual alignment: Rows line up perfectly
- Professional appearance: No jagged edges
- Easier to scan: Eyes move horizontally across levels
- Predictable layout: Heights calculate from formula

---

## LLM Integration Best Practices

### 1. Constraint-Driven Prompting

**Principle**: Inject precise character limits and formatting rules directly into LLM prompts to ensure generated content fits the template.

**Implementation**:
```python
# Build constraints from JSON spec
constraints_str = "\n\nCharacter Constraints (MUST FOLLOW EXACTLY):"
constraints_str += f"\n- Level 4 label (TOP): 1-2 words ONLY, each word 5-9 chars"
constraints_str += f"\n  If 2 words, format as: Word1<br>Word2"
constraints_str += f"\n  Total length (excluding <br>): 5-18 characters"
constraints_str += f"\n- Level 4 description: 50-60 characters"

prompt = f"""Generate a 4-level pyramid for: "{topic}"

Instructions:
1. Create hierarchical progression from base to peak
2. Top level label: MUST be 1-2 words, each 5-9 chars
3. Use <strong> tags to emphasize 1-2 key words per description

{constraints_str}

Return ONLY valid JSON in this exact format:
{{
  "level_4_label": "...",
  "level_4_description": "..."
}}"""
```

**Benefits**:
- High success rate (LLM follows explicit constraints)
- Fewer retries needed
- Predictable output format

**Reference**: `agents/illustrator/v1.0/app/llm_services/llm_service.py`

---

### 2. Context Injection for Narrative Continuity

**Principle**: Inject `previous_slides` context into prompts to ensure illustrations build upon the presentation narrative.

**Implementation**:
```python
# Build previous slides context
if context.get("previous_slides"):
    previous_context_str = "\n\nPrevious slides in this presentation:"
    for slide in previous_slides:
        slide_num = slide.get("slide_number")
        slide_title = slide.get("slide_title")
        slide_summary = slide.get("summary", "")
        previous_context_str += f"\n- Slide {slide_num}: {slide_title}"
        if slide_summary:
            previous_context_str += f"\n  {slide_summary}"

    previous_context_str += "\n\nIMPORTANT: Ensure this pyramid builds upon and complements the narrative established in previous slides."

    prompt = f"{base_prompt}{previous_context_str}"
```

**Example Scenario**:
- Slide 2: Pyramid about "Organizational Structure" (CEO → Managers → Teams)
- Slide 4: Pyramid about "Skills Development" should use consistent terminology and build on the org structure

**Benefits**:
- Consistent terminology across slides
- Coherent narrative flow
- Avoids contradictions between slides

---

### 3. Retry Logic with Validation Feedback

**Principle**: Automatically retry LLM generation (max 2 times) when validation fails. Return content even after all retries exhausted.

**Implementation**:
```python
max_retries = 2

for attempt in range(max_retries + 1):
    # Generate content with LLM
    result = await llm_service.generate_pyramid_content(
        topic=topic,
        num_levels=num_levels,
        constraints=constraints
    )

    if not result["success"]:
        return result  # LLM error, abort

    # Validate constraints (if enabled)
    if validate_constraints:
        is_valid, violations = validator.validate_content(
            generated_content=result["content"],
            constraints=constraints
        )

        if is_valid:
            break  # Success! Exit retry loop
        else:
            logger.warning(f"Attempt {attempt + 1} failed validation: {violations}")
            continue  # Retry with same prompt
    else:
        break  # Validation disabled, accept result

# Return result (even if invalid after all retries)
return {
    "success": True,
    "content": result["content"],
    "validation": {
        "valid": is_valid,
        "violations": violations  # Detailed violations for debugging
    },
    "metadata": {
        "attempts": attempt + 1
    }
}
```

**Benefits**:
- Graceful degradation (return content even if invalid)
- Transparency (violations reported to caller)
- Automatic recovery (most violations fixed on retry)

---

### 4. Structured Output with JSON Schema

**Principle**: Enforce strict JSON schema in LLM responses for predictable parsing.

**Implementation**:
```python
# Build JSON example in prompt
json_fields = {}
for level_num in range(num_levels, 0, -1):
    json_fields[f"level_{level_num}_label"] = f"Level {level_num} label text"
    json_fields[f"level_{level_num}_description"] = f"Level {level_num} description"

json_example = json.dumps(json_fields, indent=2)

prompt += f"""
Return ONLY valid JSON in this exact format:
{json_example}

CRITICAL:
- Every field must meet its character constraints exactly
- Count characters carefully (spaces count!)
- HTML tags do NOT count toward character limits
"""

# Configure Gemini for JSON output
generation_config = GenerationConfig(
    temperature=0.7,
    max_output_tokens=2048,
    response_mime_type="application/json"
)
```

**Benefits**:
- Predictable parsing (no regex needed)
- Type safety (Pydantic validation)
- Easy error handling (JSON parse failures are clear)

---

### 5. Usage Metadata Tracking

**Principle**: Return token usage and model metadata for cost tracking and debugging.

**Implementation**:
```python
# Extract usage metadata from Gemini response
usage_metadata = {}
if hasattr(response, 'usage_metadata'):
    usage_metadata = {
        "prompt_token_count": response.usage_metadata.prompt_token_count,
        "candidates_token_count": response.usage_metadata.candidates_token_count,
        "total_token_count": response.usage_metadata.total_token_count
    }

return {
    "success": True,
    "content": generated_content,
    "usage_metadata": usage_metadata,
    "model": self.model_name  # e.g., "gemini-1.5-flash-002"
}
```

**Benefits**:
- Cost tracking (tokens → API costs)
- Performance optimization (identify expensive prompts)
- Model versioning (know which model generated content)

---

## API Contract Design

### 1. Request Schema Pattern

**Principle**: Required fields for core functionality, optional fields for context and session management.

**Schema** (Pydantic):
```python
class PyramidGenerationRequest(BaseModel):
    # REQUIRED: Core functionality
    num_levels: int = Field(..., ge=3, le=6, description="Number of pyramid levels")
    topic: str = Field(..., min_length=1, description="Pyramid topic/theme")

    # OPTIONAL: Context & customization
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    target_points: Optional[List[str]] = Field(None, description="Key points to include")
    tone: str = Field("professional", description="Writing tone")
    audience: str = Field("general", description="Target audience")
    theme: str = Field("professional", description="Color theme")

    # OPTIONAL: Session management (for Director integration)
    presentation_id: Optional[str] = Field(None, description="Presentation identifier")
    slide_id: Optional[str] = Field(None, description="Slide identifier")
    slide_number: Optional[int] = Field(None, description="Slide position in deck")

    # OPTIONAL: Configuration
    validate_constraints: bool = Field(True, description="Enforce character limits")
```

**Benefits**:
- Backward compatible (optional fields can be added)
- Clear validation (Pydantic enforces types and constraints)
- Self-documenting (field descriptions become API docs)

---

### 2. Response Schema Pattern

**Principle**: Consistent response structure with success flag, output, metadata, and validation results.

**Schema**:
```python
class PyramidGenerationResponse(BaseModel):
    success: bool
    html: str  # Complete rendered illustration

    # Generated content (for debugging)
    generated_content: Dict[str, str]

    # Validation results
    character_counts: Dict[str, Dict[str, int]]
    validation: Dict[str, Any]  # {"valid": bool, "violations": [...]}

    # Metadata
    metadata: Dict[str, Any]  # model, generation_time_ms, attempts
    generation_time_ms: int

    # Session fields (echoed from request)
    presentation_id: Optional[str] = None
    slide_id: Optional[str] = None
    slide_number: Optional[int] = None
```

**Benefits**:
- Complete transparency (validation results, violations, attempts)
- Debugging support (character counts, generated content)
- Session correlation (echoed IDs match requests)

---

### 3. Session Field Echoing

**Principle**: Echo `presentation_id`, `slide_id`, `slide_number` from request to response for stateless correlation.

**Implementation**:
```python
return PyramidGenerationResponse(
    success=True,
    html=filled_html,
    generated_content=generated_content,
    # ... other fields ...
    presentation_id=request.presentation_id,  # Echo from request
    slide_id=request.slide_id,                # Echo from request
    slide_number=request.slide_number         # Echo from request
)
```

**Director Usage**:
```python
# Director makes async call
response = await illustrator.generate_pyramid(request)

# Match response to request using echoed fields
assert response.presentation_id == request.presentation_id
assert response.slide_id == request.slide_id
```

**Benefits**:
- Stateless correlation (no session storage needed)
- Async request tracking (match responses to requests)
- Multi-slide handling (Director can track multiple concurrent requests)

---

## Validation & Quality Assurance

### 1. Constraint Definition Files

**Principle**: Define character limits per illustration variant in JSON files, separate from code.

**File Structure** (`app/variant_specs/pyramid_constraints.json`):
```json
{
  "pyramid_4": {
    "level_4": {
      "label": [5, 18],
      "description": [50, 60],
      "comment": "Top level: 1-2 words, each word 5-9 chars, separated by <br>"
    },
    "level_3": {
      "label": [8, 20],
      "description": [50, 60],
      "comment": "Second from top: max 20 chars total"
    }
  }
}
```

**Benefits**:
- Separation of concerns (constraints not hardcoded)
- Easy updates (modify JSON, no code changes)
- Documentation (comments explain special rules)
- Reusability (shared across validator and LLM service)

---

### 2. HTML-Aware Character Counting

**Principle**: Strip HTML tags before counting characters, since tags don't consume visual space.

**Implementation**:
```python
import re

def count_characters(text: str) -> int:
    """Count characters excluding HTML tags"""
    # Remove HTML tags
    text_without_html = re.sub(r'<[^>]+>', '', text)
    return len(text_without_html)

# Validation
label = "Vision<br>Driven"  # User sees: "Vision\nDriven"
char_count = count_characters(label)  # 12 chars (excludes <br>)

description = "Develop the <strong>product vision</strong> and blueprint"
char_count = count_characters(description)  # 45 chars (excludes <strong>)
```

**Benefits**:
- Accurate counting (matches visual perception)
- Allows formatting (can use `<br>`, `<strong>`, etc.)
- Consistent validation (same logic in validator and LLM prompt)

---

### 3. Violation Reporting

**Principle**: Provide detailed, field-level violation information for debugging and retry optimization.

**Implementation**:
```python
violations = []

for field_name, value in generated_content.items():
    char_count = count_characters(value)
    min_chars, max_chars = constraints[field_name]

    if char_count < min_chars or char_count > max_chars:
        violations.append({
            "field": field_name,
            "value": value,
            "char_count": char_count,
            "min_allowed": min_chars,
            "max_allowed": max_chars,
            "violation_type": "too_short" if char_count < min_chars else "too_long"
        })

return {
    "valid": len(violations) == 0,
    "violations": violations
}
```

**Example Violation**:
```json
{
  "valid": false,
  "violations": [
    {
      "field": "level_4_label",
      "value": "Achieve Strategic Excellence Leadership",
      "char_count": 42,
      "min_allowed": 5,
      "max_allowed": 18,
      "violation_type": "too_long"
    }
  ]
}
```

**Benefits**:
- Precise debugging (know exactly which field failed)
- Optimization insights (identify problematic constraints)
- Transparency (caller sees exactly what went wrong)

---

### 4. Configurable Validation

**Principle**: Allow validation to be disabled via `validate_constraints` flag for flexibility.

**Use Cases**:
- **Production**: `validate_constraints=true` (enforce quality)
- **Testing**: `validate_constraints=false` (test LLM behavior without retries)
- **Debugging**: `validate_constraints=false` (see raw LLM output)

**Implementation**:
```python
if request.validate_constraints:
    is_valid, violations = validator.validate_content(...)
    if not is_valid and attempt < max_retries:
        continue  # Retry
else:
    is_valid = True
    violations = []
```

---

## Template Architecture

### 1. HTML+CSS First, SVG Only When Necessary

**Principle**: Use HTML+CSS for rectangular/box-based layouts. Use SVG only for curves, circles, and complex paths.

**When to Use HTML+CSS**:
- Rectangles, squares, boxes → `<div>` with width/height
- Trapezoids, triangles → `clip-path: polygon()`
- Gradients → `linear-gradient()`, `radial-gradient()`
- Flexbox layouts → rows, columns, centering
- Grid layouts → 2×2 matrices, dashboards

**When to Use SVG**:
- Circles (perfect circles) → `<circle>` element
- Curved arrows → `<path>` with bezier curves
- Complex shapes → arbitrary polygons
- Text on curves → `<textPath>`

**Pyramid Example** (HTML+CSS):
```html
<!-- Trapezoid using clip-path -->
<div style="
    width: 76.17%;
    clip-path: polygon(12.6% 0%, 87.4% 0%, 100% 100%, 0% 100%);
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
">
    <div>Level 3</div>
</div>

<!-- Triangle (top level) -->
<div style="
    width: 28.51%;
    clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
">
    <div>Level 4</div>
</div>
```

**Benefits**:
- Simpler code (no SVG path calculations)
- Better text rendering (HTML text vs SVG text)
- Easier maintenance (CSS is more familiar than SVG)

**Reference**: `agents/illustrator/v1.0/templates/pyramid/*.html`

---

### 2. Placeholder Pattern

**Principle**: Use `{field_name}` syntax for placeholders. Simple string replacement at runtime.

**Template**:
```html
<div class="level-label">{level_4_label}</div>
<div class="description-text">{level_4_description}</div>
<ul>
    <li>{level_1_bullet_1}</li>
    <li>{level_1_bullet_2}</li>
    <li>{level_1_bullet_3}</li>
</ul>
```

**Filling**:
```python
generated_content = {
    "level_4_label": "Vision<br>Driven",
    "level_4_description": "Define strategic <strong>goals</strong> and vision",
    "level_1_bullet_1": "Establish long-term objectives",
    "level_1_bullet_2": "Align with company mission",
    "level_1_bullet_3": "Communicate to stakeholders"
}

filled_html = template_html
for key, value in generated_content.items():
    filled_html = filled_html.replace(f"{{{key}}}", value)
```

**Benefits**:
- Simple implementation (no templating engine)
- Fast execution (pure string replacement)
- Easy debugging (search for `{` to find unfilled placeholders)

---

### 3. Fixed Layouts (Pre-Calculated Geometry)

**Principle**: Template geometry (widths, heights, positions) is pre-calculated and hardcoded. No runtime layout computation.

**Example** (4-level pyramid using mathematical formula):
```html
<!-- H = 576px, n = 3, h = 122px, triangle = 183px, gap = 9px -->
<div class="pyramid-visual" style="gap: 9px">
    <!-- Triangle -->
    <div class="level-4" style="height: 183px; width: 25%; clip-path: polygon(50% 0%, 100% 100%, 0% 100%)">
        Level 4
    </div>
    <!-- Trapezoids -->
    <div class="level-3" style="height: 122px; width: 50%; clip-path: polygon(25% 0%, 75% 0%, 100% 100%, 0% 100%)">
        Level 3
    </div>
    <div class="level-2" style="height: 122px; width: 75%; clip-path: polygon(12.5% 0%, 87.5% 0%, 100% 100%, 0% 100%)">
        Level 2
    </div>
    <div class="level-1" style="height: 122px; width: 100%; clip-path: polygon(9.6% 0%, 90.4% 0%, 100% 100%, 0% 100%)">
        Level 1
    </div>
</div>
```

**Benefits**:
- Guaranteed visual consistency (no runtime variations)
- Performance (no layout calculations)
- Simplicity (what you see in template is what renders)

---

### 4. Responsive Scaling Considerations

**Principle**: Templates should gracefully scale on different viewport sizes while maintaining aspect ratio.

**Responsive Container**:
```html
<div class="container" style="
    width: 100%;
    height: 100%;
    max-width: 1800px;  /* Prevents excessive stretching */
    max-height: 720px;   /* Maintains aspect ratio */
    display: flex;
    align-items: center;
    justify-content: center
">
```

**Relative Sizing**:
- Use percentages for widths: `flex: 0 0 45%`
- Use `em` or `rem` for scalable text (if needed)
- Use `vh`/`vw` sparingly (can break in iframe)

**Testing Checklist**:
- [ ] Renders correctly at 1800×720 (standard)
- [ ] Scales down to 1200×675 (smaller screens)
- [ ] Text remains readable when scaled to 80%
- [ ] No horizontal scrolling at any size
- [ ] Icons and bullets maintain alignment

---

## Environment Configuration

### 1. Service-Specific Model Selection

**Principle**: Each illustration type can specify its optimal LLM model via environment variable.

**Pattern**:
```bash
# .env file
LLM_PYRAMID=gemini-1.5-flash-002       # Optimized for pyramid generation
LLM_FUNNEL=gemini-2.0-flash-exp        # Future: optimized for funnel
LLM_PROCESS_FLOW=gemini-1.5-flash     # Future: simpler model for flows
```

**Implementation**:
```python
class GeminiService:
    def __init__(self, model_name: Optional[str] = None):
        # Service-specific model from env
        self.model_name = model_name or os.getenv("LLM_PYRAMID")

        if not self.model_name:
            raise ValueError("LLM_PYRAMID environment variable must be set")

        self.model = GenerativeModel(self.model_name)
```

**Benefits**:
- Optimization (different models for different complexity)
- Cost control (use cheaper models for simpler illustrations)
- Experimentation (A/B test models without code changes)

**Reference**: `agents/illustrator/v1.0/.env.example`

---

### 2. Vertex AI with Application Default Credentials (ADC)

**Principle**: Use ADC for Vertex AI authentication. No API keys in code or env files.

**Setup**:
```bash
# Authenticate once (credentials stored in ~/.config/gcloud/)
gcloud auth application-default login
```

**Implementation**:
```python
from google.cloud import aiplatform

# Initialize Vertex AI with project/location
aiplatform.init(
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GEMINI_LOCATION")
)

# Model uses ADC automatically (no explicit credentials)
model = GenerativeModel(model_name)
```

**Benefits**:
- Security (no API keys in code/env)
- Simplicity (gcloud CLI handles auth)
- Rotation (credentials auto-refresh)

**Reference**: `agents/illustrator/v1.0/app/llm_services/llm_service.py`

---

### 3. Configuration Validation at Startup

**Principle**: Validate all required environment variables when service starts. Fail fast if misconfigured.

**Implementation**:
```python
class GeminiService:
    def __init__(self):
        # Read required env vars
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GEMINI_LOCATION")
        self.model_name = os.getenv("LLM_PYRAMID")

        # Validate ALL required vars present
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID environment variable must be set")

        if not self.location:
            raise ValueError("GEMINI_LOCATION environment variable must be set")

        if not self.model_name:
            raise ValueError("LLM_PYRAMID environment variable must be set")
```

**Benefits**:
- Fail fast (errors at startup, not during request)
- Clear error messages (know exactly what's missing)
- Prevents silent failures (misconfiguration caught immediately)

---

## Integration with Director

### 1. Director as State Manager

**Principle**: Director manages ALL presentation state. Illustrator is a stateless content generator.

**Director Responsibilities**:
- Track presentation context (title, theme, target audience)
- Maintain `previous_slides` history with summaries
- Manage slide ordering and dependencies
- Coordinate multiple service calls (Text, Illustrator, Diagram)

**Illustrator Responsibilities**:
- Receive context in each request
- Generate illustration based on context
- Return HTML with echoed session fields
- NO session storage, NO state management

**Flow**:
```
Director (Stateful)
├── Creates slide specification
├── Builds previous_slides array from history
├── Calls Illustrator with full context
│
Illustrator (Stateless)
├── Receives: topic, context, previous_slides
├── Injects context into LLM prompt
├── Generates content with narrative continuity
├── Returns: HTML + echoed session fields
│
Director
├── Receives response
├── Stores illustration in slide
├── Updates previous_slides history with summary
└── Continues to next slide
```

---

### 2. Previous Slides Context Pattern

**Principle**: Director passes `previous_slides` array with slide summaries. Illustrator injects into LLM prompt for narrative continuity.

**Director Preparation**:
```python
# Director builds context before calling Illustrator
previous_slides = []
for completed_slide in presentation.slides[:current_slide_index]:
    previous_slides.append({
        "slide_number": completed_slide.slide_number,
        "slide_title": completed_slide.title,
        "summary": completed_slide.generate_summary()  # AI-generated summary
    })

# Call Illustrator with context
request = {
    "topic": "Skills Development Path",
    "context": {
        "previous_slides": previous_slides
    }
}
response = await illustrator.generate_pyramid(request)
```

**Illustrator Processing**:
```python
# Illustrator injects into LLM prompt
if context.get("previous_slides"):
    prompt += "\n\nPrevious slides in this presentation:"
    for slide in previous_slides:
        prompt += f"\n- Slide {slide['slide_number']}: {slide['slide_title']}"
        if slide.get("summary"):
            prompt += f"\n  {slide['summary']}"

    prompt += "\n\nIMPORTANT: Build upon the narrative established in previous slides."
```

**Benefits**:
- Consistent terminology (LLM sees previous content)
- Coherent storyline (builds on prior context)
- Avoids repetition (knows what was already covered)

**Reference**: `agents/illustrator/v1.0/PYRAMID_API.md`

---

## Error Handling & Resilience

### 1. Graceful Degradation

**Principle**: Return content even if validation fails after all retries. Include violation details for debugging.

**Implementation**:
```python
# After max retries exhausted
return PyramidGenerationResponse(
    success=True,  # Still return success (content was generated)
    html=filled_html,  # HTML may not perfectly fit template
    generated_content=generated_content,
    validation={
        "valid": False,
        "violations": violations  # Detailed violations
    },
    metadata={
        "attempts": max_retries + 1,
        "note": "Content returned despite validation failure"
    }
)
```

**Benefits**:
- Availability (service doesn't fail due to validation)
- Transparency (caller knows content is sub-optimal)
- Debugging (violations help diagnose issue)

---

### 2. Placeholder Cleanup

**Principle**: Remove unfilled placeholders to avoid visible `{field_name}` in rendered HTML.

**Implementation**:
```python
# Remove any remaining placeholders
import re
filled_html = re.sub(r'\{[^}]+\}', '', filled_html)
```

**Use Case**: If LLM fails to generate a field, don't show `{field_name}` placeholder to user.

---

### 3. Comprehensive Logging

**Principle**: Log all key events (LLM calls, validation results, retries) for debugging and monitoring.

**Implementation**:
```python
logger.info(f"Initialized GeminiService: model={self.model_name}")
logger.warning(f"Attempt {attempt + 1} failed validation: {violations}")
logger.error(f"Error generating content with Gemini: {e}")
```

---

## Summary: Key Takeaways

### For Future Illustration Endpoints

1. **Follow Three-Layer Architecture**: Routes → Generator → LLM Service → Validator
2. **Use HTML Fragments**: No DOCTYPE, html, head, body tags (inline styles only)
3. **Apply Mathematical Formulas**: Use proportional calculations (pyramid formula)
4. **Position Icons Outside**: Absolute positioning with `left: -70px` pattern
5. **Match Colors Consistently**: Visual elements and legend boxes use same gradients
6. **Use Constraint-Driven Prompting**: Inject limits into LLM prompts
7. **Implement Retry Logic**: Max 2 retries on validation failure
8. **Echo Session Fields**: Return `presentation_id`, `slide_id`, `slide_number`
9. **Support Previous Slides Context**: Inject into LLM for narrative continuity
10. **Pre-Build Templates**: Human-validate layouts before deployment
11. **Use HTML+CSS First**: SVG only when necessary
12. **Graceful Degradation**: Return content even if validation fails
13. **Service-Specific Models**: Optimize LLM model per illustration type
14. **Comprehensive Metadata**: Return usage stats, attempts, violations
15. **Test Responsively**: Verify rendering at multiple sizes

### Architecture Checklist

- [ ] Stateless service (no session storage)
- [ ] Three-layer separation (Routes, Generator, LLM, Validator)
- [ ] HTML fragment structure (no DOCTYPE/html/head/body)
- [ ] Inline styles only (no style tags or external CSS)
- [ ] Reset styles on every element (margin, padding, box-sizing)
- [ ] Mathematical layout formulas (proportional dimensions)
- [ ] Icon positioning pattern (absolute, left: -70px)
- [ ] Color gradient matching (visual ↔ legend boxes)
- [ ] Typography standards (18px labels, 19.2px bullets, 900 weight)
- [ ] Flexbox column layouts (vertical stacking)
- [ ] White text on colored backgrounds
- [ ] Constraint definition file (JSON)
- [ ] Pydantic request/response models
- [ ] LLM retry logic (max 2)
- [ ] Session field echoing
- [ ] Previous slides context support
- [ ] Character constraint validation
- [ ] Graceful degradation
- [ ] Comprehensive logging
- [ ] Environment variable validation
- [ ] Responsive testing (multiple viewport sizes)

---

**End of Design Principles Document**

**Next Steps**: Apply these principles when building future illustration endpoints (Process Flow, Timeline, Matrix, etc.)
