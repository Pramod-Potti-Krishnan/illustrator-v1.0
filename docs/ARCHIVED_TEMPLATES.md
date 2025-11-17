# Archived Templates

## Overview

This document lists illustration types that have been archived and are no longer actively supported by the Illustrator Service v1.0.

**Archive Date**: November 16, 2025
**Reason**: Templates did not meet quality standards or user requirements

## Archived Illustration Types

The following 15 illustration types have been moved to `templates/archive/`:

### Strategic Frameworks
1. **ansoff_matrix** - Ansoff Matrix (Market/Product Growth)
2. **bcg_matrix** - BCG Matrix (Portfolio Analysis)
3. **porters_five_forces** - Porter's Five Forces
4. **swot_2x2** - SWOT Analysis (2x2 grid)

### Process & Flow Diagrams
5. **circular_process** - Circular Process Flow
6. **horizontal_process** - Horizontal Process Flow
7. **process_flow_horizontal** - Process Flow (Horizontal variant)
8. **timeline_horizontal** - Timeline (Horizontal)
9. **value_chain** - Value Chain Diagram

### Comparisons & Visualizations
10. **before_after** - Before/After Comparison
11. **pros_cons** - Pros vs Cons
12. **venn_2circle** - Venn Diagram (2 circles)

### Other
13. **concentric_circles** - Concentric Circles
14. **kpi_dashboard** - KPI Dashboard
15. **org_chart** - Organization Chart

## Currently Supported Templates

### ✅ Approved
- **pyramid** - Pyramid diagrams (3-6 levels)
  - LLM-powered content generation
  - Character constraint validation
  - Multiple template variants (3.html, 4.html, 5.html, 6.html)

- **pyramid_3tier** - 3-tier pyramid variant

### 🚧 Work in Progress
- **funnel** - Funnel diagrams
- **funnel_4stage** - 4-stage funnel variant

## Accessing Archived Templates

Archived templates are still available in the codebase at:
```
templates/archive/{illustration_type}/{variant}.html
```

However, they are **not accessible** via the API endpoints:
- `/v1.0/generate` - Rejects archived types with 400 error
- `/v1.0/illustrations` - Does not list archived types

## Variant Specs Status

Variant specification files (`app/variant_specs/`) for archived templates have been **retained** for reference but are not actively used.

## Restoring an Archived Template

If you need to restore an archived template:

1. **Move template back**:
   ```bash
   mv templates/archive/{illustration_type} templates/
   ```

2. **Update allowed types** in `app/routes.py`:
   ```python
   ALLOWED_TYPES = ["pyramid", "pyramid_3tier", "funnel", "funnel_4stage", "{illustration_type}"]
   ```

3. **Test the template**:
   - Verify it works with all themes
   - Verify it works with all sizes
   - Test with sample data

4. **Update documentation**:
   - Add to README.md supported list
   - Remove from this archive list

## Archive Rationale

### Quality Issues
Templates were archived due to:
- Output quality did not meet professional standards
- Layout issues across different sizes
- Poor typography or spacing
- Inconsistent theme application

### User Feedback
Based on user review:
- Only **pyramid** templates were approved
- **Funnel** templates are being improved
- All other templates did not meet requirements

## Future Plans

The Illustrator Service will focus on:
1. **Pyramid refinement** - Continue improving approved pyramid templates
2. **Funnel completion** - Complete and approve funnel templates
3. **New illustrations** - Build new illustration types from scratch with user validation
4. **Quality standards** - Establish higher quality bar before adding new templates

## Questions?

For questions about archived templates or to request restoration:
- Review the template in `templates/archive/`
- Check if it meets current quality standards
- Discuss with the development team
