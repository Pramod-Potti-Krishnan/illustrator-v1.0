#!/bin/bash
#
# Illustrator Service Test: Star Diagram Endpoint
#
# Tests the newly auto-generated star_diagram endpoint
#
# Uses:
# - Illustrator: POST /v1.0/star-diagram/generate
# - Layout: POST /api/presentations with C4-infographic layout
#

# Service URLs
ILLUSTRATOR_SERVICE="https://illustrator-v10-production.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Output directory for responses
OUTPUT_DIR="./test_outputs/illustrator_star_diagram_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Default theme
DEFAULT_THEME="professional"

# Test configurations: variant_id|num_elements|topic|tone|audience
declare -a STAR_TESTS=(
  "star_5|5|Digital Marketing Strategy|professional|marketing team"
)

echo "=============================================="
echo "  Illustrator Service Test: Star Diagram"
echo "  Auto-Generated Endpoint Test"
echo "=============================================="
echo ""
echo "Illustrator Service: $ILLUSTRATOR_SERVICE"
echo "Layout Service:      $LAYOUT_SERVICE"
echo "Output Dir:          $OUTPUT_DIR"
echo ""
echo "Tests:"
echo "  Star Diagram: 5 elements (1 test)"
echo ""

# Array to collect slides JSON
SLIDES_JSON="["
FIRST_SLIDE=true
SUCCESS_COUNT=0
FAIL_COUNT=0
SLIDE_NUM=0

# ============================================
# STAR DIAGRAM TESTS
# ============================================
echo "=============================================="
echo "  STAR DIAGRAM TESTS (1 variant)"
echo "=============================================="

for item in "${STAR_TESTS[@]}"; do
  IFS='|' read -r variant num_elements topic tone audience <<< "$item"
  ((SLIDE_NUM++))

  echo ""
  echo "----------------------------------------------"
  echo ">>> Test $SLIDE_NUM: Star Diagram $num_elements elements"
  echo "    Topic: $topic"
  echo "    Tone: $tone, Audience: $audience"

  # Generate star diagram from Illustrator Service
  RESPONSE=$(curl -s -X POST "$ILLUSTRATOR_SERVICE/v1.0/star-diagram/generate" \
    -H "Content-Type: application/json" \
    -d "{
      \"num_elements\": $num_elements,
      \"topic\": \"$topic\",
      \"tone\": \"$tone\",
      \"audience\": \"$audience\",
      \"theme\": \"$DEFAULT_THEME\",
      \"size\": \"medium\",
      \"context\": {
        \"presentation_title\": \"Illustrator Star Diagram Test\",
        \"slide_purpose\": \"Testing $num_elements-element star diagram generation\"
      }
    }")

  # Save raw response
  echo "$RESPONSE" > "$OUTPUT_DIR/${variant}_response.json"

  # Extract fields from response
  SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
  HTML=$(echo "$RESPONSE" | jq -r '.html // .infographic_html')
  GEN_TIME=$(echo "$RESPONSE" | jq -r '.generation_time_ms')
  VALIDATION=$(echo "$RESPONSE" | jq -r '.validation.valid // .validation.is_valid // true')

  if [ "$SUCCESS" == "true" ] && [ "$HTML" != "null" ] && [ -n "$HTML" ]; then
    echo "    Illustrator: OK"
    echo "    Generation Time: ${GEN_TIME}ms"
    echo "    Validation: $VALIDATION"
    echo "    HTML Size: ${#HTML} chars"
    ((SUCCESS_COUNT++))

    # Save HTML for inspection
    echo "$HTML" > "$OUTPUT_DIR/${variant}.html"

    # Escape HTML for JSON
    HTML_ESCAPED=$(echo "$HTML" | jq -Rs .)

    # Build slide JSON for Layout Service (C4-infographic)
    SLIDE_JSON="{
      \"layout\": \"C4-infographic\",
      \"content\": {
        \"slide_title\": \"$topic\",
        \"subtitle\": \"Star Diagram - $num_elements Elements\",
        \"infographic_html\": $HTML_ESCAPED,
        \"presentation_name\": \"Star Diagram Test\",
        \"logo\": \" \"
      }
    }"

    # Add to slides array
    if [ "$FIRST_SLIDE" = true ]; then
      SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON"
      FIRST_SLIDE=false
    else
      SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON"
    fi
  else
    echo "    ERROR: Illustrator failed to generate content"
    echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
    ((FAIL_COUNT++))
  fi
done

# Close slides array
SLIDES_JSON="$SLIDES_JSON]"

# ============================================
# CREATE PRESENTATION
# ============================================
echo ""
echo "=============================================="
echo "  Creating Presentation"
echo "=============================================="
echo ""
echo "Slides generated: $SUCCESS_COUNT success, $FAIL_COUNT failed"

# Save slides JSON for debugging
echo "$SLIDES_JSON" > "$OUTPUT_DIR/all_slides.json"

# Create presentation with all slides
# Use jq with file input to handle large payloads (avoid argument too long errors)
jq -n --slurpfile slides "$OUTPUT_DIR/all_slides.json" \
  --arg title "Star Diagram Test ($SUCCESS_COUNT slides)" \
  '{title: $title, slides: $slides[0]}' > "$OUTPUT_DIR/layout_request.json"

# Use file-based input for curl to handle large payloads
LAYOUT_RESPONSE=$(curl -s -X POST "$LAYOUT_SERVICE/api/presentations" \
  -H "Content-Type: application/json" \
  -d @"$OUTPUT_DIR/layout_request.json")

echo "$LAYOUT_RESPONSE" > "$OUTPUT_DIR/layout_response.json"

PRES_ID=$(echo "$LAYOUT_RESPONSE" | jq -r '.id')

if [ "$PRES_ID" == "null" ] || [ -z "$PRES_ID" ]; then
  echo "ERROR: Layout Service failed to create presentation"
  echo "$LAYOUT_RESPONSE" | jq . 2>/dev/null || echo "$LAYOUT_RESPONSE"
  exit 1
fi

URL="$LAYOUT_SERVICE/p/$PRES_ID"

echo ""
echo "=============================================="
echo "  SUCCESS! Star Diagram Test Complete"
echo "=============================================="
echo ""
echo "Presentation ID: $PRES_ID"
echo "URL: $URL"
echo ""
echo "Results: $SUCCESS_COUNT / 1 slides"
echo "Output:  $OUTPUT_DIR"
echo ""
echo "Review Checklist:"
echo "  [ ] All star diagram illustrations rendered correctly"
echo "  [ ] 5 radial points displayed around center"
echo "  [ ] Labels and bullets properly sized"
echo "  [ ] Theme colors (professional) applied"
echo "  [ ] No placeholder text remaining"
echo "  [ ] Generation times acceptable (<5s each)"
echo ""

# Open in browser
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
