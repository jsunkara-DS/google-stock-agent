#!/bin/bash
# API Testing Script - Common curl commands for testing

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
SYMBOL="${1:-AAPL}"

echo "🧪 Stock Agent API Testing"
echo "Base URL: $BASE_URL"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Health Check
echo -e "${BLUE}1. Health Check${NC}"
curl -s "$BASE_URL/health" | jq '.' || echo "Failed"
echo ""

# Get Config
echo -e "${BLUE}2. Get Configuration${NC}"
curl -s "$BASE_URL/config" | jq '.' || echo "Failed"
echo ""

# Get Stock Quote
echo -e "${BLUE}3. Get Stock Quote ($SYMBOL)${NC}"
curl -s "$BASE_URL/stocks/quote/$SYMBOL" | jq '.' || echo "Failed"
echo ""

# Analyze Single Stock
echo -e "${BLUE}4. Analyze Single Stock ($SYMBOL)${NC}"
echo "Note: This calls Gemini API (may take 5-10 seconds)"
curl -s -X POST "$BASE_URL/analyze/single/$SYMBOL" | jq '.' || echo "Failed"
echo ""

# Get History
echo -e "${BLUE}5. Get Analysis History ($SYMBOL)${NC}"
curl -s "$BASE_URL/history/$SYMBOL" | jq '.' || echo "Failed"
echo ""

# Batch Analysis
echo -e "${BLUE}6. Batch Analysis (All Configured Stocks)${NC}"
echo "Note: This calls Gemini API (may take 10-30 seconds)"
curl -s -X POST "$BASE_URL/analyze/batch" | jq '.' || echo "Failed"
echo ""

echo -e "${GREEN}✓ Testing complete!${NC}"
echo ""
echo "Interactive API docs: $BASE_URL/docs"
