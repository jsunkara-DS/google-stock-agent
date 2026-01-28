#!/bin/bash
# Deployment script for Google Cloud Run

set -e

PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="stock-agent"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Stock Agent to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not installed. Please install it first."
    exit 1
fi

# Check if required env vars are set
if [ -z "$GEMINI_API_KEY" ] || [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
    echo "❌ Missing API keys. Set GEMINI_API_KEY and ALPHA_VANTAGE_API_KEY environment variables."
    exit 1
fi

# Build and push image to Container Registry
echo "📦 Building Docker image..."
gcloud builds submit \
    --project=$PROJECT_ID \
    --tag=${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --project=${PROJECT_ID} \
    --image=${IMAGE_NAME}:latest \
    --region=${REGION} \
    --platform=managed \
    --memory=512Mi \
    --cpu=1 \
    --timeout=120 \
    --allow-unauthenticated \
    --set-env-vars="GEMINI_API_KEY=${GEMINI_API_KEY},ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY},STOCKS_TO_MONITOR=${STOCKS_TO_MONITOR:-AAPL,MSFT,GOOGL,AMZN,NVDA},ENVIRONMENT=production" \
    --min-instances=0 \
    --max-instances=10

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --format='value(status.url)')

echo ""
echo "✅ Deployment successful!"
echo ""
echo "Service URL: $SERVICE_URL"
echo "API Docs: ${SERVICE_URL}/docs"
echo ""
echo "Test the service:"
echo "  curl $SERVICE_URL/health"
echo "  curl -X POST $SERVICE_URL/analyze/batch"
echo ""
echo "To set up Cloud Scheduler:"
echo "  gcloud scheduler jobs create http stock-agent-batch \\
    --project=$PROJECT_ID \\
    --schedule='0 8,13,16 * * 1-5' \\
    --uri=${SERVICE_URL}/analyze/batch \\
    --http-method=POST"
