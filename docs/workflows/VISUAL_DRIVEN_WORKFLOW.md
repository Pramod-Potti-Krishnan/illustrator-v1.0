# Visual-Driven Illustration Workflow

**Purpose**: Document the new image-based approach for building future illustration endpoints.

**Philosophy**: "Show, don't tell" - User provides visual reference, Claude recreates using HTML+CSS+JS.

**Last Updated**: 2025-11-15

---

## Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [Shape Toolkit (HTML+CSS)](#shape-toolkit-htmlcss)
3. [Interactivity Options (JavaScript)](#interactivity-options-javascript)
4. [Implementation Steps](#implementation-steps)
5. [Examples by Illustration Type](#examples-by-illustration-type)
6. [Best Practices](#best-practices)

---

## Workflow Overview

### The New Approach

**Traditional Workflow** (slow, text-driven):
```
User describes → Claude interprets → Build → User feedback → Iterate
```

**Visual-Driven Workflow** (fast, image-driven):
```
User provides image → Claude analyzes visual → Recreate → Done
```

### Key Principles

1. **Visual First**: User shows exactly what they want (image, screenshot, sketch)
2. **Regular Shapes Only**: No SVG complexity - use HTML+CSS shapes
3. **Interactivity Built-In**: Add JavaScript for hover, click, animations
4. **Fast Iteration**: Visual feedback is immediate and precise

### When to Use This Workflow

✅ **Use for**:
- Funnel diagrams
- Concentric circles
- Process flows
- Timelines
- Matrix diagrams (2×2, 3×3)
- Organizational charts
- Simple infographics

❌ **Don't use for**:
- Complex curved paths (use Mermaid/Diagram service)
- Data visualizations (use Analytics service)
- Interactive charts (use Charting agent)

---

## Shape Toolkit (HTML+CSS)

### Core Shapes Reference

#### 1. Rectangle / Square

**HTML**:
```html
<div class="rectangle"></div>
```

**CSS**:
```css
.rectangle {
    width: 200px;
    height: 100px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    border-radius: 8px;  /* Optional rounded corners */
}
```

**Use Cases**: Boxes, cards, process steps, tiles

---

#### 2. Circle

**HTML**:
```html
<div class="circle"></div>
```

**CSS**:
```css
.circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;  /* Makes it circular */
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}
```

**Use Cases**: Milestones, icons, concentric circles, badges

---

#### 3. Triangle (Equilateral)

**HTML**:
```html
<div class="triangle"></div>
```

**CSS**:
```css
.triangle {
    width: 100px;
    height: 100px;
    clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}
```

**Variations**:
```css
/* Upside-down triangle */
.triangle-down {
    clip-path: polygon(0% 0%, 100% 0%, 50% 100%);
}

/* Right-pointing triangle */
.triangle-right {
    clip-path: polygon(0% 0%, 0% 100%, 100% 50%);
}

/* Left-pointing triangle */
.triangle-left {
    clip-path: polygon(100% 0%, 100% 100%, 0% 50%);
}
```

**Use Cases**: Pyramid top, arrows, directional indicators

---

#### 4. Trapezoid

**HTML**:
```html
<div class="trapezoid"></div>
```

**CSS**:
```css
.trapezoid {
    width: 200px;
    height: 80px;
    clip-path: polygon(15% 0%, 85% 0%, 100% 100%, 0% 100%);
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}
```

**Customization**:
```css
/* Wider at bottom (pyramid section) */
.trapezoid-bottom-wide {
    clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);
}

/* Funnel section (wider at top) */
.trapezoid-top-wide {
    clip-path: polygon(0% 0%, 100% 0%, 80% 100%, 20% 100%);
}
```

**Use Cases**: Pyramid sections, funnel stages, 3D boxes

---

#### 5. Hexagon

**HTML**:
```html
<div class="hexagon"></div>
```

**CSS**:
```css
.hexagon {
    width: 100px;
    height: 115px;  /* Height = width * 1.15 for regular hexagon */
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
}
```

**Use Cases**: Honeycomb patterns, process nodes, strategic frameworks

---

#### 6. Rounded Rectangle (Pill)

**HTML**:
```html
<div class="pill"></div>
```

**CSS**:
```css
.pill {
    width: 150px;
    height: 50px;
    border-radius: 25px;  /* Half of height for perfect pill */
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}
```

**Use Cases**: Tags, buttons, status indicators, labels

---

### Composite Shapes

#### Arrow (Using Triangle + Rectangle)

**HTML**:
```html
<div class="arrow">
    <div class="arrow-body"></div>
    <div class="arrow-head"></div>
</div>
```

**CSS**:
```css
.arrow {
    display: flex;
    align-items: center;
}

.arrow-body {
    width: 100px;
    height: 20px;
    background: #3b82f6;
}

.arrow-head {
    width: 0;
    height: 0;
    border-left: 25px solid #3b82f6;
    border-top: 15px solid transparent;
    border-bottom: 15px solid transparent;
}
```

**Use Cases**: Process flows, directional indicators, transitions

---

#### Concentric Circles

**HTML**:
```html
<div class="concentric-circles">
    <div class="circle-outer">
        <div class="circle-middle">
            <div class="circle-inner">
                <div class="circle-core">Core</div>
            </div>
        </div>
    </div>
</div>
```

**CSS**:
```css
.concentric-circles {
    display: flex;
    justify-content: center;
    align-items: center;
}

.circle-outer {
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: rgba(59, 130, 246, 0.2);  /* Blue, 20% opacity */
    display: flex;
    justify-content: center;
    align-items: center;
}

.circle-middle {
    width: 300px;
    height: 300px;
    border-radius: 50%;
    background: rgba(139, 92, 246, 0.3);  /* Purple, 30% opacity */
    display: flex;
    justify-content: center;
    align-items: center;
}

.circle-inner {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: rgba(245, 158, 11, 0.4);  /* Orange, 40% opacity */
    display: flex;
    justify-content: center;
    align-items: center;
}

.circle-core {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: rgba(16, 185, 129, 0.6);  /* Green, 60% opacity */
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: bold;
}
```

**Use Cases**: Target models, organizational layers, priority frameworks

---

### Layout Techniques

#### Flexbox (For Linear Arrangements)

**Horizontal Row**:
```css
.process-flow {
    display: flex;
    gap: 30px;
    align-items: center;
}
```

**Vertical Column**:
```css
.vertical-stack {
    display: flex;
    flex-direction: column;
    gap: 20px;
}
```

**Centered Content**:
```css
.centered {
    display: flex;
    justify-content: center;
    align-items: center;
}
```

---

#### CSS Grid (For Matrix Layouts)

**2×2 Matrix**:
```css
.matrix-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 20px;
    width: 600px;
    height: 600px;
}
```

**3×3 Grid**:
```css
.grid-3x3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 15px;
}
```

**Use Cases**: SWOT matrix, BCG matrix, prioritization grids

---

## Interactivity Options (JavaScript)

### Hover Effects

#### Scale on Hover

**HTML**:
```html
<div class="interactive-box">Content</div>
```

**CSS**:
```css
.interactive-box {
    width: 150px;
    height: 150px;
    background: #3b82f6;
    transition: transform 0.3s ease;
}

.interactive-box:hover {
    transform: scale(1.1);  /* 10% larger on hover */
}
```

---

#### Brightness Change

**CSS**:
```css
.interactive-box {
    filter: brightness(1.0);
    transition: filter 0.3s ease;
}

.interactive-box:hover {
    filter: brightness(1.2);  /* 20% brighter */
}
```

---

#### Shadow Enhancement

**CSS**:
```css
.interactive-box {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.3s ease;
}

.interactive-box:hover {
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}
```

---

### Click Interactions

#### Expand/Collapse

**HTML**:
```html
<div class="expandable" onclick="toggleExpand(this)">
    <div class="header">Click to expand</div>
    <div class="content" style="display: none;">Hidden content here</div>
</div>
```

**JavaScript**:
```javascript
function toggleExpand(element) {
    const content = element.querySelector('.content');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        element.querySelector('.header').textContent = 'Click to collapse';
    } else {
        content.style.display = 'none';
        element.querySelector('.header').textContent = 'Click to expand';
    }
}
```

---

#### Highlight Selected Item

**HTML**:
```html
<div class="selectable-item" onclick="selectItem(this)">Item 1</div>
<div class="selectable-item" onclick="selectItem(this)">Item 2</div>
<div class="selectable-item" onclick="selectItem(this)">Item 3</div>
```

**JavaScript**:
```javascript
function selectItem(element) {
    // Remove 'selected' class from all items
    document.querySelectorAll('.selectable-item').forEach(item => {
        item.classList.remove('selected');
    });

    // Add 'selected' class to clicked item
    element.classList.add('selected');
}
```

**CSS**:
```css
.selectable-item {
    background: #e5e7eb;
    cursor: pointer;
    transition: background 0.2s ease;
}

.selectable-item.selected {
    background: #3b82f6;
    color: white;
}
```

---

### Animations

#### Fade In on Load

**CSS**:
```css
@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.fade-in-element {
    animation: fadeIn 0.5s ease-in;
}
```

---

#### Slide In from Left

**CSS**:
```css
@keyframes slideInLeft {
    from {
        transform: translateX(-100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.slide-in {
    animation: slideInLeft 0.6s ease-out;
}
```

---

#### Pulse Effect

**CSS**:
```css
@keyframes pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
}

.pulse-element {
    animation: pulse 2s infinite;
}
```

---

### Tooltip on Hover

**HTML**:
```html
<div class="tooltip-container">
    Hover me
    <span class="tooltip-text">This is additional information</span>
</div>
```

**CSS**:
```css
.tooltip-container {
    position: relative;
    display: inline-block;
    cursor: pointer;
}

.tooltip-text {
    visibility: hidden;
    position: absolute;
    background-color: #1f2937;
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    white-space: nowrap;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip-container:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}
```

---

## Implementation Steps

### Step 1: User Provides Visual Reference

**User sends**:
- Image/screenshot of desired illustration
- Or detailed description: "3 concentric circles, blue to green gradient, labels for each ring"

**Example**:
```
"I want a funnel with 4 stages:
1. Awareness (top, widest)
2. Interest
3. Consideration
4. Purchase (bottom, narrowest)

Each stage should have:
- Trapezoid shape
- Stage name on left
- Metric number on right
- Blue gradient"
```

---

### Step 2: Claude Analyzes Visual

**Claude identifies**:
1. **Shapes needed**: Trapezoids (4 stages)
2. **Layout**: Vertical stack with decreasing widths
3. **Colors**: Blue gradient (#3b82f6 to #2563eb)
4. **Text placement**: Stage name (left), metric (right)
5. **Interactivity**: Hover to highlight, show details

---

### Step 3: Recreate with HTML+CSS

**HTML Structure**:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .funnel-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            padding: 40px;
        }

        .funnel-stage {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 40px;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .funnel-stage:hover {
            filter: brightness(1.2);
            transform: scale(1.02);
        }

        /* Stage 1 (Widest) */
        .stage-1 {
            width: 500px;
            clip-path: polygon(10% 0%, 90% 0%, 100% 100%, 0% 100%);
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        /* Stage 2 */
        .stage-2 {
            width: 400px;
            clip-path: polygon(12% 0%, 88% 0%, 100% 100%, 0% 100%);
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        /* Stage 3 */
        .stage-3 {
            width: 300px;
            clip-path: polygon(15% 0%, 85% 0%, 100% 100%, 0% 100%);
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        /* Stage 4 (Narrowest) */
        .stage-4 {
            width: 200px;
            clip-path: polygon(18% 0%, 82% 0%, 100% 100%, 0% 100%);
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        .stage-name {
            font-size: 18px;
        }

        .stage-metric {
            font-size: 24px;
            font-weight: 900;
        }
    </style>
</head>
<body>
    <div class="funnel-container">
        <div class="funnel-stage stage-1">
            <span class="stage-name">Awareness</span>
            <span class="stage-metric">10,000</span>
        </div>
        <div class="funnel-stage stage-2">
            <span class="stage-name">Interest</span>
            <span class="stage-metric">5,000</span>
        </div>
        <div class="funnel-stage stage-3">
            <span class="stage-name">Consideration</span>
            <span class="stage-metric">2,000</span>
        </div>
        <div class="funnel-stage stage-4">
            <span class="stage-name">Purchase</span>
            <span class="stage-metric">500</span>
        </div>
    </div>
</body>
</html>
```

---

### Step 4: Add Interactivity

**Add JavaScript for click-to-expand details**:

```html
<script>
function showDetails(stageName, metric) {
    alert(`Stage: ${stageName}\nConversion: ${metric} users`);
}
</script>

<!-- Update each stage -->
<div class="funnel-stage stage-1" onclick="showDetails('Awareness', '10,000')">
    ...
</div>
```

**Or add tooltip with conversion rate**:
```css
.funnel-stage::after {
    content: attr(data-conversion);
    position: absolute;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    opacity: 0;
    transition: opacity 0.3s;
}

.funnel-stage:hover::after {
    opacity: 1;
}
```

```html
<div class="funnel-stage stage-1" data-conversion="50% conversion to next stage">
```

---

### Step 5: Iterate Based on Feedback

**User**: "Make the top stage orange instead of blue"

**Claude**: Updates CSS:
```css
.stage-1 {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}
```

**User**: "Add a label above the funnel saying 'Sales Funnel 2024'"

**Claude**: Adds heading:
```html
<h2 style="text-align: center; color: #1f2937;">Sales Funnel 2024</h2>
<div class="funnel-container">
    ...
</div>
```

---

## Examples by Illustration Type

### Example 1: Concentric Circles (Target Model)

**User Request**: "Create concentric circles showing organizational priorities. 3 rings: Core (green), Support (blue), Optional (gray)."

**Implementation**:
```html
<div class="concentric-target">
    <div class="ring ring-outer" data-label="Optional Services">
        <div class="ring ring-middle" data-label="Support Functions">
            <div class="ring ring-core" data-label="Core Business">
                Core
            </div>
        </div>
    </div>
</div>

<style>
.concentric-target {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px;
}

.ring {
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    transition: transform 0.3s ease;
}

.ring:hover {
    transform: scale(1.05);
}

.ring-outer {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(209, 213, 219, 0.3), rgba(156, 163, 175, 0.5));
}

.ring-middle {
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.3), rgba(37, 99, 235, 0.5));
}

.ring-core {
    width: 160px;
    height: 160px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.5), rgba(5, 150, 105, 0.7));
    color: white;
    font-weight: bold;
    font-size: 18px;
}
</style>
```

---

### Example 2: Process Flow (4 Horizontal Steps)

**User Request**: "4-step horizontal process: Plan → Build → Test → Launch. With arrows between steps."

**Implementation**:
```html
<div class="process-flow">
    <div class="step">
        <div class="step-box">Plan</div>
    </div>
    <div class="arrow-connector">→</div>
    <div class="step">
        <div class="step-box">Build</div>
    </div>
    <div class="arrow-connector">→</div>
    <div class="step">
        <div class="step-box">Test</div>
    </div>
    <div class="arrow-connector">→</div>
    <div class="step">
        <div class="step-box">Launch</div>
    </div>
</div>

<style>
.process-flow {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 40px;
}

.step-box {
    width: 120px;
    height: 80px;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    border-radius: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    font-weight: 600;
    transition: transform 0.3s ease;
}

.step-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.arrow-connector {
    font-size: 32px;
    color: #6b7280;
}
</style>
```

---

### Example 3: Timeline (Horizontal Milestones)

**User Request**: "Horizontal timeline with 5 milestones. Circles connected by a line."

**Implementation**:
```html
<div class="timeline">
    <div class="timeline-line"></div>
    <div class="milestone">
        <div class="milestone-circle">Q1</div>
        <div class="milestone-label">Launch</div>
    </div>
    <div class="milestone">
        <div class="milestone-circle">Q2</div>
        <div class="milestone-label">Growth</div>
    </div>
    <div class="milestone">
        <div class="milestone-circle">Q3</div>
        <div class="milestone-label">Expand</div>
    </div>
    <div class="milestone">
        <div class="milestone-circle">Q4</div>
        <div class="milestone-label">Scale</div>
    </div>
</div>

<style>
.timeline {
    position: relative;
    display: flex;
    justify-content: space-around;
    padding: 60px 40px;
}

.timeline-line {
    position: absolute;
    top: 75px;
    left: 80px;
    right: 80px;
    height: 4px;
    background: #cbd5e1;
}

.milestone {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
    position: relative;
    z-index: 1;
}

.milestone-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: bold;
    transition: transform 0.3s ease;
}

.milestone-circle:hover {
    transform: scale(1.2);
}

.milestone-label {
    font-size: 14px;
    color: #475569;
    font-weight: 600;
}
</style>
```

---

## Best Practices

### 1. Keep It Simple

**Do**:
- Use regular shapes (rectangles, circles, trapezoids)
- Stick to HTML+CSS when possible
- Add minimal JavaScript for interactivity

**Don't**:
- Over-complicate with SVG paths
- Add unnecessary animations
- Use complex JavaScript frameworks

---

### 2. Match User's Visual Exactly

**Do**:
- Recreate colors precisely (ask for hex codes if unclear)
- Match proportions and spacing
- Use exact text/labels from user's image

**Don't**:
- "Improve" on user's design without asking
- Change colors/layout arbitrarily
- Add elements not in original visual

---

### 3. Responsive Design

**Do**:
- Use relative units (`%`, `em`, `rem`, `vh`, `vw`)
- Test at different viewport sizes
- Use flexbox/grid for adaptive layouts

**Don't**:
- Hardcode pixel values for everything
- Assume fixed 1920×1080 viewport
- Ignore mobile/tablet considerations

---

### 4. Performance

**Do**:
- Use CSS transitions (smoother than JavaScript animations)
- Minimize JavaScript (prefer CSS-only solutions)
- Optimize gradients (2-color gradients are fastest)

**Don't**:
- Use heavy JavaScript libraries for simple effects
- Add dozens of event listeners
- Create complex animations that drop frames

---

### 5. Accessibility

**Do**:
- Use semantic HTML (`<section>`, `<article>`, `<h2>`)
- Add `alt` text for visual elements
- Ensure sufficient color contrast

**Don't**:
- Rely solely on color to convey meaning
- Use `<div>` for everything
- Forget keyboard navigation

---

## Summary: Why This Workflow Works

### Benefits

1. **Speed**: Visual reference eliminates interpretation time
2. **Accuracy**: User sees exactly what they get
3. **Simplicity**: HTML+CSS is maintainable and familiar
4. **Interactivity**: JavaScript enhances UX without complexity
5. **Iteration**: Fast feedback loop for refinements

### Limitations

**Not suitable for**:
- Complex curved paths (use Mermaid/SVG)
- Data-driven charts (use Analytics service)
- Algorithmic layouts (use dedicated services)

### When to Use

✅ Use visual-driven workflow when:
- User can provide visual reference
- Illustration uses regular shapes
- Interactivity enhances UX
- Fast iteration is needed

---

**End of Visual-Driven Workflow Document**

**Next Steps**: Apply this workflow when building Funnel, Concentric Circles, Process Flow, Timeline, and other future illustrations.
