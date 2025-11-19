# Illustrator Service v1.0 - Quick Start Guide

## 🚀 Service is Running

The Illustrator Service is currently running at **http://localhost:8000**

---

## 📋 Quick API Reference

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. List Available Templates
```bash
curl http://localhost:8000/v1.0/illustrations
```

### 3. Generate SWOT 2×2
```bash
curl -X POST http://localhost:8000/v1.0/generate \
  -H "Content-Type: application/json" \
  -d '{
    "illustration_type": "swot_2x2",
    "variant_id": "base",
    "data": {
      "strengths_items": "<li>Your strength 1</li><li>Your strength 2</li>",
      "weaknesses_items": "<li>Your weakness 1</li>",
      "opportunities_items": "<li>Your opportunity 1</li><li>Your opportunity 2</li>",
      "threats_items": "<li>Your threat 1</li>"
    },
    "theme": "professional",
    "size": "medium"
  }'
```

---

## 🎨 Available Themes

| Theme | Description | Primary Color |
|-------|-------------|---------------|
| `professional` | Corporate and professional | Blue (#0066CC) |
| `bold` | High-energy and vibrant | Red (#E31E24) |
| `minimal` | Clean and understated | Gray (#2C3E50) |
| `playful` | Creative and fun | Purple (#9C27B0) |

---

## 📐 Available Sizes

| Size | Dimensions | Aspect Ratio | Use Case |
|------|------------|--------------|----------|
| `small` | 600×400px | 3:2 | Thumbnails, previews |
| `medium` | 1200×800px | 3:2 | Standard slides |
| `large` | 1800×720px | 5:2 | Widescreen presentations |

---

## 📝 Data Format for SWOT 2×2

The `data` object should contain HTML `<li>` items for each quadrant:

```json
{
  "strengths_items": "<li>Item 1</li><li>Item 2</li><li>Item 3</li>",
  "weaknesses_items": "<li>Item 1</li><li>Item 2</li>",
  "opportunities_items": "<li>Item 1</li><li>Item 2</li><li>Item 3</li>",
  "threats_items": "<li>Item 1</li><li>Item 2</li>"
}
```

**Tips**:
- Each quadrant can have 1-5 items (flexible)
- Wrap each item in `<li>` tags
- Combine all items into a single string per quadrant
- HTML will be safely inserted into the template

---

## 📊 Response Format

```json
{
  "illustration_type": "swot_2x2",
  "variant_id": "base",
  "format": "html",
  "data": "<div class=\"swot-container\">...</div>",
  "metadata": {
    "width": 1200,
    "height": 800,
    "theme": "professional",
    "rendering_method": "html_css"
  },
  "generation_time_ms": 3
}
```

---

## 🧪 Test Commands

### Test All Themes
```bash
# Professional
curl -s -X POST http://localhost:8000/v1.0/generate \
  -H "Content-Type: application/json" \
  -d '{"illustration_type":"swot_2x2","variant_id":"base","data":{"strengths_items":"<li>Test</li>","weaknesses_items":"<li>Test</li>","opportunities_items":"<li>Test</li>","threats_items":"<li>Test</li>"},"theme":"professional","size":"medium"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data'])" > professional.html

# Bold
curl -s -X POST http://localhost:8000/v1.0/generate \
  -H "Content-Type: application/json" \
  -d '{"illustration_type":"swot_2x2","variant_id":"base","data":{"strengths_items":"<li>Test</li>","weaknesses_items":"<li>Test</li>","opportunities_items":"<li>Test</li>","threats_items":"<li>Test</li>"},"theme":"bold","size":"medium"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data'])" > bold.html

# Minimal
curl -s -X POST http://localhost:8000/v1.0/generate \
  -H "Content-Type: application/json" \
  -d '{"illustration_type":"swot_2x2","variant_id":"base","data":{"strengths_items":"<li>Test</li>","weaknesses_items":"<li>Test</li>","opportunities_items":"<li>Test</li>","threats_items":"<li>Test</li>"},"theme":"minimal","size":"medium"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data'])" > minimal.html

# Playful
curl -s -X POST http://localhost:8000/v1.0/generate \
  -H "Content-Type: application/json" \
  -d '{"illustration_type":"swot_2x2","variant_id":"base","data":{"strengths_items":"<li>Test</li>","weaknesses_items":"<li>Test</li>","opportunities_items":"<li>Test</li>","threats_items":"<li>Test</li>"},"theme":"playful","size":"medium"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data'])" > playful.html

# Open all in browser
open professional.html bold.html minimal.html playful.html
```

---

## 🔧 Service Control

### Start Service
```bash
cd agents/illustrator/v1.0
python3 main.py
```

### Stop Service
Press `Ctrl+C` in the terminal where the service is running

### Check Service Status
```bash
curl http://localhost:8000/health
```

### View Service Logs
Logs are displayed in the terminal where the service is running. Look for:
- `INFO` - Normal operations
- `ERROR` - Issues that need attention

---

## 📁 Project Structure

```
agents/illustrator/v1.0/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── models.py          # Request/response models
│   ├── themes.py          # 4 color themes
│   ├── sizes.py           # 3 size presets
│   ├── services.py        # Template loading & filling
│   └── routes.py          # API endpoints
├── templates/
│   └── swot_2x2/
│       └── base.html      # SWOT 2×2 base template
├── docs/                  # Design documentation
├── SWOT_DEMO.html        # Visual demo (open in browser)
└── TEST_RESULTS.md       # Comprehensive test report
```

---

## 🎯 Current Status

✅ **Phase 1 Complete**: Infrastructure ready
- FastAPI service running
- 4 themes × 3 sizes working
- SWOT 2×2 base template complete
- Sub-millisecond generation times

⏳ **Awaiting User Validation**:
- Review SWOT 2×2 template in `SWOT_DEMO.html`
- Approve or request changes
- Proceed to variant creation

---

## 🔜 Next Steps

### After Base Template Approval:
1. Create **rounded** variant (softer corners, modern look)
2. Create **condensed** variant (more compact for dense content)
3. Create **highlighted** variant (colored quadrant backgrounds)

### Second Template (Week 3-4):
Choose from:
- Ansoff Matrix (2×2 grid)
- Pros vs Cons (two columns)
- Timeline (horizontal flow)
- Process Flow (sequential steps)

All use similar HTML+CSS approach!

---

## 📞 Need Help?

- View API docs: http://localhost:8000/docs
- Check test results: `TEST_RESULTS.md`
- View demo: `SWOT_DEMO.html`
- Review roadmap: `docs/IMPLEMENTATION_ROADMAP.md`
