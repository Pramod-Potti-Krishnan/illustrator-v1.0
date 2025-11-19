# Illustrator Service v1.0 - Technical Approach

## Executive Summary

This document defines the technical architecture and implementation approach for the Illustrator Service v1.0, a FastAPI-based microservice that generates professional PowerPoint illustrations using **pre-built, validated HTML+CSS templates**. The service is built on a simple philosophy: templates are human-validated visual structures, and the service performs text substitution and theme color application at runtime.

**Key Technical Decisions**:
- **Rendering**: HTML+CSS first (simple shapes), SVG only when necessary (complex curves/shapes)
- **Templates**: Pre-built, human-validated HTML/CSS files with `{placeholders}`
- **Runtime**: Load template → Fill text → Apply theme → Return HTML or convert to PNG
- **Integration**: REST API compatible with Director Agent v3.4 and Text Service v1.2
- **Output Formats**: HTML (primary) + PNG conversion

---

## 1. Core Philosophy

### 1.1 Template-First Approach

**What Templates Are**:
- **Pre-built HTML+CSS layouts** with fixed shapes and structure
- **Text placeholders**: `{title}`, `{bullet_1}`, `{strength_1}`, etc.
- **Theme color variables**: `{theme.primary}`, `{theme.text}`, etc.
- **Human-validated**: Each template and variant approved before deployment

**What Templates Are NOT**:
- NOT programmatically generated at runtime
- NOT complex algorithmic composition
- NOT LLM-generated layouts

**Example - SWOT 2x2 Template**:
```html
<!-- templates/swot_2x2/base.html -->
<div class="swot-container" style="width: {width}px; height: {height}px;">
  <style>
    .swot-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 2px;
      background: {theme.border};
      font-family: Arial, sans-serif;
    }
    .quadrant {
      background: white;
      padding: 20px;
    }
    .quadrant h3 {
      color: {theme.text};
      font-size: 24px;
      margin: 0 0 15px 0;
    }
    .quadrant.strengths h3 { color: {theme.success}; }
    .quadrant.weaknesses h3 { color: {theme.danger}; }
    .quadrant ul {
      list-style: none;
      padding: 0;
    }
    .quadrant li {
      padding: 8px 0;
      color: {theme.text};
    }
  </style>

  <div class="quadrant strengths">
    <h3>Strengths</h3>
    <ul>
      {strengths_items}
    </ul>
  </div>

  <div class="quadrant weaknesses">
    <h3>Weaknesses</h3>
    <ul>
      {weaknesses_items}
    </ul>
  </div>

  <div class="quadrant opportunities">
    <h3>Opportunities</h3>
    <ul>
      {opportunities_items}
    </ul>
  </div>

  <div class="quadrant threats">
    <h3>Threats</h3>
    <ul>
      {threats_items}
    </ul>
  </div>
</div>
```

### 1.2 Runtime Simplicity

**Service Responsibilities** (at runtime):
1. **Receive request**: `{illustration_type, variant_id, data, theme, size}`
2. **Load template**: Read pre-validated HTML file from disk
3. **Fill placeholders**: Replace `{strength_1}` with actual text from request
4. **Apply theme**: Replace `{theme.primary}` with color values
5. **Apply size**: Set width/height based on preset
6. **Return**: HTML string OR convert to PNG

**What Service Does NOT Do**:
- Does NOT generate layouts algorithmically
- Does NOT use LLM for standard illustrations (Phase 1-2)
- Does NOT choose between multiple rendering methods
- Does NOT complex shape calculations

**Simple Python Implementation**:
```python
def generate_illustration(illustration_type: str, variant_id: str,
                         data: dict, theme: Theme, size: SizePreset):
    # 1. Load pre-validated template
    template_path = f"templates/{illustration_type}/{variant_id}.html"
    template = load_template(template_path)

    # 2. Prepare text substitutions
    substitutions = {
        "width": size.width,
        "height": size.height,
        "theme.primary": theme.primary,
        "theme.text": theme.text,
        # ... all theme colors
        **data  # Merge in caller's text data
    }

    # 3. Fill template (simple string replacement)
    html = template.format(**substitutions)

    # 4. Return HTML or convert to PNG
    return html  # or convert_to_png(html)
```

---

## 2. Architecture Overview

### 2.1 Simplified Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Illustrator Service v1.0                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   FastAPI    │  │    Jinja2    │  │   Themes    │  │
│  │  Application │  │   Template   │  │   (4 color  │  │
│  │              │  │    Loader    │  │   palettes) │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │
│         │                  │                  │         │
│  ┌──────▼──────────────────▼──────────────────▼──────┐ │
│  │         Request Handler (Validation)              │ │
│  └──────┬────────────────────────────────────────────┘ │
│         │                                               │
│  ┌──────▼────────────────────────────────────────────┐ │
│  │   Template Filling Engine (Simple Substitution)  │ │
│  │   - Load template HTML file                      │ │
│  │   - Replace {placeholders} with data            │ │
│  │   - Apply theme colors                          │ │
│  └──────┬───────────────────────────────────────────┘ │
│         │                                              │
│  ┌──────▼──────────────────────────────────────────┐  │
│  │   Output Layer                                   │  │
│  │   ┌──────────┐         ┌──────────┐            │  │
│  │   │   HTML   │         │   PNG    │            │  │
│  │   │  Output  │         │ Converter│            │  │
│  │   │          │         │(Playwright)          │  │
│  │   └──────────┘         └──────────┘            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ▲                                      │
         │                                      │
    ┌────┴────┐                            ┌────▼────┐
    │ Director│                            │  Client │
    │  v3.4   │                            │ Response│
    │   or    │                            │  (HTML/ │
    │  Text   │                            │   PNG)  │
    │ Service │                            └─────────┘
    └─────────┘

┌─────────────────────────────────────────────────────────┐
│          Template Storage (File System)                │
├─────────────────────────────────────────────────────────┤
│  templates/                                             │
│    swot_2x2/                                           │
│      base.html          (approved by human)            │
│      rounded.html       (approved variant)             │
│      minimal.html       (approved variant)             │
│    process_flow_4step/                                 │
│      horizontal.html    (approved)                     │
│      vertical.html      (approved variant)             │
│    bcg_matrix/                                         │
│      standard.svg       (SVG when needed)              │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

**FastAPI Application**
- HTTP request/response handling
- CORS configuration
- Health check endpoints
- API versioning (/v1.0/)
- Request validation (Pydantic models)

**Jinja2 Template Loader**
- Load HTML/CSS template files from disk
- Cache templates in memory (LRU cache)
- Handle template not found errors

**Themes (Color Palettes)**
- 4 predefined themes: Professional, Bold, Minimal, Playful
- Simple Python dataclasses with color values
- No complex theme logic - just color mappings

**Template Filling Engine**
- Extremely simple: `template.format(**data)`
- Replace text placeholders with caller's data
- Replace theme placeholders with color values
- Apply size dimensions

**Output Layer**
- **HTML Output**: Return filled template as-is
- **PNG Converter**: Use Playwright to screenshot HTML

---

## 3. HTML+CSS vs SVG Decision Matrix

### 3.1 When to Use HTML+CSS

**Use HTML+CSS for illustrations with**:
- ✅ **Rectangles and boxes** (divs, sections, grids)
- ✅ **Text-heavy layouts** (bullet points, tables, lists)
- ✅ **Grid structures** (CSS Grid is perfect for this)
- ✅ **Simple arrows** (CSS borders can create triangles)
- ✅ **Columnar layouts** (Flexbox handles this easily)

**Examples - HTML+CSS Illustrations**:
1. **SWOT 2x2** → 4 divs in CSS Grid
2. **Comparison columns** → Flexbox with divs
3. **Process flow (boxes + arrows)** → Flexbox + CSS triangle arrows
4. **Tables** → HTML `<table>` with CSS
5. **Metrics cards** → CSS Grid with styled divs
6. **Org charts (boxes + lines)** → Positioned divs + border lines
7. **Pros vs Cons** → Two column Flexbox
8. **Timeline (boxes)** → Horizontal Flexbox
9. **Value Chain** → Layered divs

### 3.2 When to Use SVG

**Use SVG for illustrations with**:
- ✅ **Circles** (can't make perfect circles with CSS easily)
- ✅ **Curved arrows** (CSS can't do smooth curves)
- ✅ **Arbitrary angles** (rotated shapes beyond 45°)
- ✅ **Overlapping shapes** (Venn diagrams)
- ✅ **Polygons** (pentagons, hexagons)
- ✅ **Curved paths** (arcs, bezier curves)

**Examples - SVG Illustrations**:
1. **Circular process** → Circles arranged in circle + curved arrows
2. **Funnel** → Trapezoid/polygon shapes
3. **Pyramid** → Stacked triangles/trapezoids
4. **BCG Matrix** → Axes + plotted circles
5. **Venn diagrams** → Overlapping circles
6. **Gauge/meter** → Arc + needle
7. **Network graph** → Circles + connecting lines at arbitrary angles
8. **Porter's Five Forces** → Center box + diagonal arrows

### 3.3 Decision Process

**Default approach**: Try HTML+CSS first
**Switch to SVG**: Only if HTML+CSS genuinely can't achieve the shape
**Validation**: Build with HTML+CSS → Show to user → If doesn't work → Try SVG → Validate again

---

## 4. Technology Stack

### 4.1 Core Framework

**Backend**:
- **Python 3.11+**: Modern async/await, type hints
- **FastAPI 0.109+**: Lightweight web framework
- **Pydantic v2**: Request/response validation
- **Jinja2**: Template loading (built into FastAPI)
- **Uvicorn**: ASGI server

**Frontend** (Templates):
- **HTML5**: Semantic markup
- **CSS3**: Grid, Flexbox, custom properties (variables)
- **Inline SVG**: When needed for complex shapes

**Image Conversion**:
- **Playwright**: Headless browser for HTML → PNG
- Alternative: **wkhtmltoimage** (lighter weight, no JS execution)

### 4.2 File Structure

```
agents/illustrator/v1.0/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment variables template
├── app/
│   ├── __init__.py
│   ├── models.py          # Pydantic request/response models
│   ├── themes.py          # Theme color definitions
│   ├── sizes.py           # Size preset definitions
│   ├── services.py        # Template filling logic
│   └── routes.py          # API endpoints
├── templates/             # Human-validated templates
│   ├── swot_2x2/
│   │   ├── base.html
│   │   ├── rounded.html
│   │   └── minimal.html
│   ├── process_flow_4step/
│   │   ├── horizontal.html
│   │   └── vertical.html
│   └── bcg_matrix/
│       └── standard.svg
├── tests/
│   ├── test_api.py
│   ├── test_template_filling.py
│   └── test_themes.py
└── docs/
    └── (documentation files)
```

### 4.3 Dependencies

**Core**:
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
jinja2==3.1.3
python-multipart==0.0.6
```

**Image Conversion**:
```txt
playwright==1.40.0
# OR
# wkhtmltopdf (system package)
```

**Development**:
```txt
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.26.0
black==24.1.0
ruff==0.1.14
```

---

## 5. Theme System

### 5.1 Simple Theme Definitions

**Python Dataclass**:
```python
from dataclasses import dataclass

@dataclass
class Theme:
    name: str
    primary: str
    secondary: str
    background: str
    text: str
    text_on_primary: str
    border: str
    success: str
    warning: str
    danger: str

# Predefined themes
PROFESSIONAL = Theme(
    name="professional",
    primary="#0066CC",
    secondary="#FF6B35",
    background="#FFFFFF",
    text="#1A1A1A",
    text_on_primary="#FFFFFF",
    border="#CCCCCC",
    success="#28A745",
    warning="#FFC107",
    danger="#DC3545"
)

BOLD = Theme(
    name="bold",
    primary="#E31E24",
    secondary="#FFD700",
    background="#F5F5F5",
    text="#000000",
    text_on_primary="#FFFFFF",
    border="#333333",
    success="#00C853",
    warning="#FF9100",
    danger="#D50000"
)

MINIMAL = Theme(
    name="minimal",
    primary="#2C3E50",
    secondary="#95A5A6",
    background="#FFFFFF",
    text="#34495E",
    text_on_primary="#FFFFFF",
    border="#BDC3C7",
    success="#27AE60",
    warning="#F39C12",
    danger="#E74C3C"
)

PLAYFUL = Theme(
    name="playful",
    primary="#9C27B0",
    secondary="#00BCD4",
    background="#FFFDE7",
    text="#424242",
    text_on_primary="#FFFFFF",
    border="#9E9E9E",
    success="#8BC34A",
    warning="#FF9800",
    danger="#F44336"
)

THEMES = {
    "professional": PROFESSIONAL,
    "bold": BOLD,
    "minimal": MINIMAL,
    "playful": PLAYFUL
}
```

### 5.2 Theme Application

**In Templates** (using placeholders):
```html
<style>
  .container {
    background: {theme.background};
    border: 2px solid {theme.border};
  }
  h1 {
    color: {theme.primary};
  }
  p {
    color: {theme.text};
  }
</style>
```

**At Runtime** (simple substitution):
```python
def apply_theme(template_html: str, theme: Theme) -> str:
    """Replace theme placeholders with actual colors"""
    return template_html.format(
        theme_primary=theme.primary,
        theme_secondary=theme.secondary,
        theme_background=theme.background,
        theme_text=theme.text,
        theme_text_on_primary=theme.text_on_primary,
        theme_border=theme.border,
        theme_success=theme.success,
        theme_warning=theme.warning,
        theme_danger=theme.danger
    )
```

---

## 6. Size Presets

### 6.1 Preset Definitions

```python
from dataclasses import dataclass

@dataclass
class SizePreset:
    name: str
    width: int
    height: int

    @property
    def aspect_ratio(self) -> str:
        from math import gcd
        divisor = gcd(self.width, self.height)
        return f"{self.width // divisor}:{self.height // divisor}"

# Predefined sizes
SMALL = SizePreset(name="small", width=600, height=400)
MEDIUM = SizePreset(name="medium", width=1200, height=800)
LARGE = SizePreset(name="large", width=1800, height=720)

SIZES = {
    "small": SMALL,
    "medium": MEDIUM,
    "large": LARGE
}
```

### 6.2 Responsive Scaling in Templates

**Option 1: Fixed sizes in template**
```html
<div style="width: {width}px; height: {height}px; font-size: {font_size}px;">
  <!-- Content -->
</div>
```

**Option 2: Percentage-based scaling**
```html
<style>
  .container {
    width: {width}px;
    height: {height}px;
  }
  h1 {
    font-size: calc({width}px * 0.03); /* 3% of width */
  }
  p {
    font-size: calc({width}px * 0.015); /* 1.5% of width */
  }
</style>
```

---

## 7. Template Development Workflow

### 7.1 Build → Validate → Approve Cycle

**For Each New Illustration Type**:

1. **Build Base Template** (Developer/Claude Code):
   - Create HTML+CSS with placeholder structure
   - Test with sample data
   - Verify rendering in browser
   - Save to `templates/{illustration_type}/base.html`

2. **Present for Validation** (Human Review):
   - Show rendered output with sample data
   - Get feedback on layout, spacing, typography
   - Iterate until approved

3. **Create Variants** (After base approval):
   - Build 2-3 visual variations
   - Different border styles, colors, spacing
   - All using same data structure

4. **Validate All Variants** (Human Review):
   - Review all variants together
   - Approve which ones to keep
   - Finalize and save

5. **Document Data Schema**:
   - Define required/optional fields
   - Add to API documentation
   - Create test cases

### 7.2 Template Quality Criteria

**Every template must**:
- ✅ Render correctly at all 3 size presets
- ✅ Work with all 4 color themes
- ✅ Handle variable text lengths gracefully
- ✅ Use semantic HTML structure
- ✅ Have clear, readable typography
- ✅ Be visually balanced and professional
- ✅ Match industry standard appearance for that illustration type

---

## 8. Runtime Implementation

### 8.1 Core Service Logic

```python
# app/services.py
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any
from .themes import Theme, THEMES
from .sizes import SizePreset, SIZES

class TemplateService:
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir

    @lru_cache(maxsize=128)
    def load_template(self, illustration_type: str, variant_id: str) -> str:
        """Load and cache template HTML"""
        template_path = self.templates_dir / illustration_type / f"{variant_id}.html"

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        return template_path.read_text()

    def fill_template(self, template: str, data: Dict[str, Any],
                     theme: Theme, size: SizePreset) -> str:
        """Fill template with data and apply theme"""

        # Prepare all substitutions
        substitutions = {
            # Size
            "width": size.width,
            "height": size.height,

            # Theme colors
            "theme.primary": theme.primary,
            "theme.secondary": theme.secondary,
            "theme.background": theme.background,
            "theme.text": theme.text,
            "theme.text_on_primary": theme.text_on_primary,
            "theme.border": theme.border,
            "theme.success": theme.success,
            "theme.warning": theme.warning,
            "theme.danger": theme.danger,

            # User data (merge last to allow overrides)
            **data
        }

        # Simple string replacement
        return template.format(**substitutions)

    def generate(self, illustration_type: str, variant_id: str,
                data: Dict[str, Any], theme_name: str,
                size_name: str) -> str:
        """Full generation pipeline"""

        # 1. Load template
        template = self.load_template(illustration_type, variant_id)

        # 2. Get theme and size
        theme = THEMES[theme_name]
        size = SIZES[size_name]

        # 3. Fill template
        html = self.fill_template(template, data, theme, size)

        return html
```

### 8.2 API Endpoint

```python
# app/routes.py
from fastapi import APIRouter, HTTPException
from .models import IllustrationRequest, IllustrationResponse
from .services import TemplateService
from .converter import html_to_png

router = APIRouter(prefix="/v1.0")
template_service = TemplateService(templates_dir=Path("templates"))

@router.post("/generate")
async def generate_illustration(request: IllustrationRequest) -> IllustrationResponse:
    """Generate illustration from template"""

    try:
        # Generate HTML
        html = template_service.generate(
            illustration_type=request.illustration_type,
            variant_id=request.variant_id or "base",
            data=request.data,
            theme_name=request.theme,
            size_name=request.size
        )

        # Convert to PNG if requested
        if request.output_format == "png":
            png_data = await html_to_png(html,
                                         width=SIZES[request.size].width,
                                         height=SIZES[request.size].height)
            data = png_data
            format_type = "png"
        else:
            data = html
            format_type = "html"

        return IllustrationResponse(
            illustration_type=request.illustration_type,
            format=format_type,
            data=data,
            metadata={
                "width": SIZES[request.size].width,
                "height": SIZES[request.size].height,
                "theme": request.theme,
                "variant": request.variant_id or "base",
                "rendering_method": "html_css"  # or "svg" for SVG templates
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400,
                          detail=f"Invalid theme or size: {e}")
```

### 8.3 HTML to PNG Conversion

```python
# app/converter.py
from playwright.async_api import async_playwright
import base64

async def html_to_png(html: str, width: int, height: int) -> str:
    """Convert HTML to PNG using Playwright"""

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})

        # Set HTML content
        await page.set_content(html)

        # Take screenshot
        screenshot_bytes = await page.screenshot(type="png")

        await browser.close()

        # Return as base64 data URL
        b64 = base64.b64encode(screenshot_bytes).decode()
        return f"data:image/png;base64,{b64}"
```

---

## 9. Testing Strategy

### 9.1 Template Validation Tests

```python
# tests/test_templates.py
import pytest
from pathlib import Path
from app.services import TemplateService
from app.themes import THEMES
from app.sizes import SIZES

@pytest.fixture
def template_service():
    return TemplateService(templates_dir=Path("templates"))

def test_swot_template_loads(template_service):
    """Verify SWOT template exists and loads"""
    template = template_service.load_template("swot_2x2", "base")
    assert "{strengths_items}" in template
    assert "{theme.primary}" in template

def test_swot_fills_correctly(template_service):
    """Verify SWOT template fills with data"""
    html = template_service.generate(
        illustration_type="swot_2x2",
        variant_id="base",
        data={
            "strengths_items": "<li>Strong brand</li><li>Market leader</li>",
            "weaknesses_items": "<li>High costs</li>",
            "opportunities_items": "<li>New markets</li>",
            "threats_items": "<li>Competition</li>"
        },
        theme_name="professional",
        size_name="medium"
    )

    assert "Strong brand" in html
    assert "#0066CC" in html  # Professional theme primary color
    assert "1200" in html  # Medium width

def test_all_themes_work(template_service):
    """Verify template works with all 4 themes"""
    for theme_name in THEMES.keys():
        html = template_service.generate(
            illustration_type="swot_2x2",
            variant_id="base",
            data={"strengths_items": "<li>Test</li>"},
            theme_name=theme_name,
            size_name="medium"
        )
        assert html is not None
        assert len(html) > 100

def test_all_sizes_work(template_service):
    """Verify template works with all 3 sizes"""
    for size_name in SIZES.keys():
        html = template_service.generate(
            illustration_type="swot_2x2",
            variant_id="base",
            data={"strengths_items": "<li>Test</li>"},
            theme_name="professional",
            size_name=size_name
        )
        assert str(SIZES[size_name].width) in html
```

### 9.2 Visual Regression Tests

```python
# tests/test_visual_regression.py
import pytest
from playwright.async_api import async_playwright
import imagehash
from PIL import Image
from io import BytesIO

@pytest.mark.asyncio
async def test_swot_visual_regression():
    """Compare rendered output to reference image"""

    # Generate current HTML
    html = template_service.generate(...)

    # Render to PNG
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html)
        screenshot = await page.screenshot()
        await browser.close()

    # Compare perceptual hash to reference
    current_hash = imagehash.average_hash(Image.open(BytesIO(screenshot)))
    reference_hash = load_reference_hash("swot_2x2_base_professional_medium")

    assert current_hash - reference_hash < 5  # Allow small differences
```

---

## 10. Deployment

### 10.1 Railway Configuration

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application
COPY . .

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**railway.toml**:
```toml
[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
```

---

## 11. Future Enhancements (Phase 2-3)

### Phase 2 Additions:
- Custom size support (beyond 3 presets)
- User-uploaded custom themes
- Batch generation endpoint

### Phase 3 Additions:
- **Custom endpoint with LLM**: Natural language → select template + fill data
- Animation-ready SVG exports (layer IDs for PowerPoint)
- Template marketplace (user contributions)

---

**End of Technical Approach Document**
