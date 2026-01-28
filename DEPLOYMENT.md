# Cloud Run Deployment Commands

This file contains all the gcloud commands needed to deploy the Stock Agent.

## Prerequisites

```bash
# Set your Google Cloud project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

## 1. Create Secret Manager Secrets

```bash
# Create secrets for API keys
echo -n "your-gemini-api-key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "your-alpha-vantage-key" | gcloud secrets create alpha-vantage-api-key --data-file=-

# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding alpha-vantage-api-key \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 2. Build and Deploy to Cloud Run

```bash
# Build the image
gcloud builds submit --tag gcr.io/$PROJECT_ID/stock-agent:latest

# Deploy to Cloud Run
gcloud run deploy stock-agent \
  --image gcr.io/$PROJECT_ID/stock-agent:latest \
  --region us-central1 \
  --platform managed \
  --memory 512Mi \
  --cpu 1 \
  --timeout 120 \
  --set-env-vars "STOCKS_TO_MONITOR=AAPL,MSFT,GOOGL,AMZN,NVDA,ENVIRONMENT=production" \
  --update-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --update-secrets ALPHA_VANTAGE_API_KEY=alpha-vantage-api-key:latest \
  --min-instances 0 \
  --max-instances 10 \
  --allow-unauthenticated
```

## 3. Get the Service URL

```bash
SERVICE_URL=$(gcloud run services describe stock-agent \
  --region us-central1 \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"
```

## 4. Set Up Cloud Scheduler (Optional)

```bash
# Create a Cloud Scheduler job to trigger batch processing
gcloud scheduler jobs create http stock-agent-batch \
  --schedule="0 8,13,16 * * 1-5" \
  --uri="$SERVICE_URL/analyze/batch" \
  --http-method POST \
  --time-zone "America/New_York" \
  --location us-central1

# Test the job
gcloud scheduler jobs run stock-agent-batch --location us-central1
```

## 5. Monitor Logs

```bash
# Stream live logs
gcloud run logs read stock-agent --limit 50 --region us-central1 --follow

# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=stock-agent" \
  --limit 100 \
  --format json
```

## 6. View Metrics

```bash
# View Cloud Run metrics in Cloud Console
gcloud console run list
```

## Cost Tracking

```bash
# Set up billing alerts
gcloud billing budgets create \
  --billing-account BILLING_ACCOUNT_ID \
  --display-name "Stock Agent Budget" \
  --budget-amount 5 \
  --threshold-rule percent=100
```

## Clean Up

```bash
# Delete Cloud Run service
gcloud run services delete stock-agent --region us-central1

# Delete Cloud Scheduler job
gcloud scheduler jobs delete stock-agent-batch --location us-central1

# Delete secrets
gcloud secrets delete gemini-api-key
gcloud secrets delete alpha-vantage-api-key
```

## Testing

```bash
# Test health endpoint
curl "$SERVICE_URL/health"

# Test single stock analysis
curl -X POST "$SERVICE_URL/analyze/single/AAPL"

# Test batch analysis
curl -X POST "$SERVICE_URL/analyze/batch"

# View interactive docs
open "$SERVICE_URL/docs"
```

## Estimated Monthly Costs

Based on typical usage (50 stocks, 3x daily analysis):

| Service | Usage | Cost |
|---------|-------|------|
| Gemini API | 3.15M tokens | $0.95 |
| Cloud Run | 9k vCPU-sec | $0 (within free tier) |
| Cloud Logging | ~5GB | $0 (within free tier) |
| **Total** | | **$0.95/month** |

## Troubleshooting

### High Latency

```bash
# Check if Cloud Run is scaling to zero
gcloud run describe stock-agent --region us-central1 --format='value(spec.template.spec.containerConcurrency)'

# Increase min instances (costs more)
gcloud run deploy stock-agent \
  --region us-central1 \
  --min-instances 1
```

### Rate Limiting

Alpha Vantage limits to 5 requests/minute. The code automatically handles this with delays.
If you need real-time data for many stocks, consider Finnhub or other APIs.

### Memory Issues

```bash
# Increase Cloud Run memory
gcloud run deploy stock-agent \
  --region us-central1 \
  --memory 1Gi
```

### Firestore Setup

If using Firestore instead of local storage:

```bash
# Enable Firestore API
gcloud services enable firestore.googleapis.com

# Create a Firestore database
gcloud firestore databases create --region=us-central1

# Update env var in Cloud Run
gcloud run deploy stock-agent \
  --region us-central1 \
  --set-env-vars USE_FIRESTORE=true
```
