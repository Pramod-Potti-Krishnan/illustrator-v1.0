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

## Documentation

All documentation is organized in the `docs/` directory:

- **[Documentation Index](docs/README.md)** - Start here for all documentation
- **[API Specification](docs/api/API_SPECIFICATION.md)** - Complete API reference
- **[Quick Start Guide](docs/guides/QUICK_START.md)** - Detailed getting started guide
- **[Director Integration](docs/guides/DIRECTOR_INTEGRATION_SUMMARY.md)** - Integration with Director Agent
- **[Architecture](docs/architecture/)** - Technical architecture and design principles

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
illustrator/v1.0/
├── main.py                     # FastAPI entry point
├── requirements.txt            # Dependencies
│
├── app/                        # Application code
│   ├── core/                  # Core logic (validators, template engine)
│   ├── api_routes/            # API route handlers
│   ├── llm_services/          # LLM content generators
│   ├── variant_specs/         # Illustration constraints
│   ├── models.py              # Pydantic models
│   ├── themes.py              # Color themes
│   └── sizes.py               # Size presets
│
├── templates/                  # HTML+CSS templates (human-validated)
│   ├── pyramid/
│   ├── funnel/
│   ├── concentric_circles/
│   └── archive/               # Deprecated templates
│
├── tests/                     # All test files
│   ├── api/                  # API endpoint tests
│   ├── integration/          # Integration tests
│   ├── fixtures/             # Test data & golden examples
│   └── outputs/              # Test-generated outputs
│
├── docs/                      # Documentation (organized by category)
│   ├── README.md             # Documentation index
│   ├── api/                  # API specifications
│   ├── guides/               # Integration & usage guides
│   ├── architecture/         # Technical architecture
│   ├── workflows/            # Development workflows
│   └── archive/              # Historical documentation
│
└── scripts/                   # Utility scripts
```

**📚 For detailed documentation**, see [docs/README.md](docs/README.md)

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

## Contributing

To add new illustration types or make changes, see:
- **[New Illustration Workflow](docs/workflows/NEW_ILLUSTRATION_WORKFLOW.md)** - Process for adding new illustrations
- **[Visual-Driven Workflow](docs/workflows/VISUAL_DRIVEN_WORKFLOW.md)** - Visual-first development approach
- **[Illustrator API Design Principles](docs/architecture/ILLUSTRATOR_API_DESIGN_PRINCIPLES.md)** - Design guidelines

## Additional Resources

- **[Implementation Roadmap](docs/archive/IMPLEMENTATION_ROADMAP.md)** - Historical development roadmap
- **[Archived Templates](docs/archive/ARCHIVED_TEMPLATES.md)** - Deprecated illustration types
- **[Recent Updates](docs/archive/)** - Completion reports and bug fixes
