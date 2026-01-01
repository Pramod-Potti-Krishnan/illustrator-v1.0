#!/bin/bash
#
# Illustrator Service Test: Round Table Illustration
#
# Tests round table illustration with different topics
#
# Uses:
# - Illustrator: POST /v1.0/round-table/generate
# - Layout: POST /api/presentations with C4-infographic layout
#

# Service URLs
ILLUSTRATOR_SERVICE="https://illustrator-v10-production.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Output directory for responses
OUTPUT_DIR="./test_outputs/illustrator_round_table_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Test configurations: variant_id|num_elements|topic|tone|audience
declare -a ROUND_TABLE_TESTS=(
  "round_table_5|5|Strategic Planning Essentials|professional|executives"
  "round_table_5|5|Agile Team Collaboration|professional|development teams"
  "round_table_5|5|Customer Experience Framework|professional|product managers"
)

echo "=============================================="
echo "  Illustrator Service Test: Round Table"
echo "=============================================="
echo ""
echo "Illustrator Service: $ILLUSTRATOR_SERVICE"
echo "Layout Service:      $LAYOUT_SERVICE"
echo "Output Dir:          $OUTPUT_DIR"
echo ""
echo "Tests: ${#ROUND_TABLE_TESTS[@]} round table variations"
echo ""

# Array to collect slides JSON
SLIDES_JSON="["
FIRST_SLIDE=true
SUCCESS_COUNT=0
FAIL_COUNT=0
SLIDE_NUM=0

# ============================================
# ROUND TABLE TESTS
# ============================================
echo "=============================================="
echo "  ROUND TABLE TESTS (${#ROUND_TABLE_TESTS[@]} variants)"
echo "=============================================="

for item in "${ROUND_TABLE_TESTS[@]}"; do
  IFS='|' read -r variant num_elements topic tone audience <<< "$item"
  ((SLIDE_NUM++))

  echo ""
  echo "----------------------------------------------"
  echo ">>> Test $SLIDE_NUM: Round Table $num_elements elements"
  echo "    Topic: $topic"
  echo "    Tone: $tone, Audience: $audience"

  # Generate round table from Illustrator Service
  RESPONSE=$(curl -s -X POST "$ILLUSTRATOR_SERVICE/v1.0/round-table/generate" \
    -H "Content-Type: application/json" \
    -d "{
      \"num_elements\": $num_elements,
      \"topic\": \"$topic\",
      \"tone\": \"$tone\",
      \"audience\": \"$audience\"
    }")

  # Check success
  SUCCESS=$(echo "$RESPONSE" | jq -r '.success')

  if [ "$SUCCESS" == "true" ]; then
    echo "    SUCCESS: Round Table generated"

    # Show character counts
    echo "    Character counts:"
    echo "$RESPONSE" | jq -r '.character_counts | to_entries | .[:6] | .[] | "      \(.key): \(.value)"'
    echo "      ..."

    # Show validation
    VALID=$(echo "$RESPONSE" | jq -r '.validation.valid')
    VIOLATIONS=$(echo "$RESPONSE" | jq -r '.validation.violations | length')
    echo "    Validation: valid=$VALID, violations=$VIOLATIONS"

    # Show generation time
    GEN_TIME=$(echo "$RESPONSE" | jq -r '.generation_time_ms')
    echo "    Generation time: ${GEN_TIME}ms"

    ((SUCCESS_COUNT++))

    # Get HTML
    HTML=$(echo "$RESPONSE" | jq -r '.html')

    # Save HTML for inspection
    echo "$HTML" > "$OUTPUT_DIR/${variant}_${SLIDE_NUM}.html"

    # Escape HTML for JSON
    HTML_ESCAPED=$(echo "$HTML" | jq -Rs .)

    # Build slide JSON for Layout Service (C4-infographic)
    SLIDE_JSON="{
      \"layout\": \"C4-infographic\",
      \"content\": {
        \"slide_title\": \"$topic\",
        \"subtitle\": \"Round Table - $num_elements Elements\",
        \"infographic_html\": $HTML_ESCAPED,
        \"presentation_name\": \"Illustrator Test Suite\",
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
LAYOUT_REQUEST="{
  \"title\": \"Illustrator Test: Round Table ($SUCCESS_COUNT slides)\",
  \"slides\": $SLIDES_JSON
}"

echo "$LAYOUT_REQUEST" > "$OUTPUT_DIR/layout_request.json"

# Use file-based curl to avoid "Argument list too long" with large HTML
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
echo "  SUCCESS! Round Table Test Complete"
echo "=============================================="
echo ""
echo "Presentation ID: $PRES_ID"
echo "URL: $URL"
echo ""
echo "Results: $SUCCESS_COUNT / ${#ROUND_TABLE_TESTS[@]} slides"
echo "Output:  $OUTPUT_DIR"
echo ""
echo "Review Checklist:"
echo "  [ ] All illustrations rendered correctly"
echo "  [ ] 8 elements visible around the table"
echo "  [ ] Labels and bullets properly sized"
echo "  [ ] No placeholder text remaining"
echo "  [ ] Generation times acceptable (<10s each)"
echo ""

# Open in browser
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
