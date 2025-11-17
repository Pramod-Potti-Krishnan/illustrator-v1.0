# Illustrator Service v1.0

Professional PowerPoint illustrations through pre-built, human-validated HTML+CSS templates.

## ✅ Currently Supported Illustrations

- **Pyramid** (3-6 levels) - ✅ **APPROVED** - LLM-powered content generation with character constraint validation
- **Funnel** (3-5 stages) - ✅ **IMPLEMENTATION COMPLETE** - LLM-powered content generation, ready for testing
- **Concentric Circles** (3-5 circles) - ✅ **IMPLEMENTATION COMPLETE** - LLM-powered content generation, Director integration ready

> **Note**: All other illustration types have been archived. See `templates/archive/` for legacy templates.
>
> **Latest Update (Nov 17, 2025)**: Concentric Circles endpoint implementation complete. Local testing passed. Director integration ready. See `CONCENTRIC_CIRCLES_DIRECTOR_INTEGRATION_GUIDE.md` for integration details.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python3 main.py

# Or with uvicorn
uvicorn main:app --reload --port 8000
```

The service will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## How It Works

This service uses a **simple template-based approach**:

1. **Load** pre-built HTML+CSS template from disk
2. **Fill** placeholders with your data
3. **Apply** theme colors
4. **Return** HTML (or PNG in future)

Templates are located in `templates/{illustration_type}/{variant}.html`

## API Examples

### Pyramid Generation (LLM-Powered)

```bash
curl -X POST http://localhost:8000/v1.0/pyramid/generate \
  -H "Content-Type: application/json" \
  -d '{
    "num_levels": 4,
    "topic": "Product Development Strategy",
    "tone": "professional",
    "audience": "executives"
  }'
```

### Manual Template Generation

```bash
curl -X POST http://localhost:8000/v1.0/generate \
  -H "Content-Type: application/json" \
  -d '{
    "illustration_type": "pyramid",
    "variant_id": "4",
    "data": {
      "level_4_label": "Vision",
      "level_4_description": "Strategic objectives",
      "level_3_label": "Strategy",
      "level_3_description": "Planning and resources"
    },
    "theme": "professional",
    "size": "medium"
  }'
```

## Current Status

**Production Ready** ✅
- ✅ FastAPI application with `/v1.0/generate` and `/v1.0/pyramid/generate` endpoints
- ✅ Pydantic request/response models
- ✅ Theme system (4 themes: Professional, Bold, Minimal, Playful)
- ✅ Size presets (3 sizes: Small, Medium, Large)
- ✅ Template loading service with caching
- ✅ LLM-powered pyramid content generation (Gemini 2.5 Flash)
- ✅ Character constraint validation for pyramids
- ✅ Layout service integration (L25, L01, L02 support)
- ✅ Session context support for narrative continuity
- ✅ Health check and CORS configuration

**Approved Illustrations**:
- **Pyramid** (3-6 levels) - Fully approved and production-ready

**In Development**:
- **Funnel** - Work in progress

**Archived**:
- 15 illustration types archived (see `ARCHIVED_TEMPLATES.md`)

## Project Structure

```
agents/illustrator/v1.0/
├── main.py                 # FastAPI entry point
├── requirements.txt        # Dependencies
├── app/
│   ├── __init__.py
│   ├── models.py          # Pydantic models
│   ├── themes.py          # 4 color themes
│   ├── sizes.py           # 3 size presets
│   ├── services.py        # Template loading & filling
│   └── routes.py          # API endpoints
├── templates/             # HTML+CSS templates (human-validated)
│   └── (illustration types will go here)
├── tests/
└── docs/                  # Comprehensive documentation
    ├── ILLUSTRATION_TAXONOMY.md
    ├── IMPLEMENTATION_ROADMAP.md
    ├── TECHNICAL_APPROACH.md
    └── API_SPECIFICATION.md
```

## Available Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /v1.0/generate` - Generate illustration
- `GET /v1.0/illustrations` - List available templates
- `GET /v1.0/illustration/{type}` - Get template details
- `GET /v1.0/themes` - List color themes
- `GET /v1.0/sizes` - List size presets

## Development Philosophy

1. **Templates are pre-built and human-validated**
2. **Runtime is simple text substitution**
3. **HTML+CSS first, SVG only when needed**
4. **Each template validated before deployment**

## Next Steps

1. Create first template: SWOT 2x2 with base variant
2. Test generation end-to-end
3. Present for validation
4. Create 2-3 variants
5. Move to next illustration type

See `docs/IMPLEMENTATION_ROADMAP.md` for full plan.
