# Google Stock Agent

AI-powered stock data fetching and analysis using Google Gemini 2.5 Flash-Lite, optimized for minimal cost on Google Cloud Run.

## Features

- ⚡ **Real-time Stock Data**: Fetch current prices from Alpha Vantage API
- 🤖 **AI Analysis**: Analyze stocks using Google Gemini 2.5 Flash-Lite (cheapest production model)
- 📊 **Batch Processing**: Analyze multiple stocks in one API call (50% token savings with Batch API)
- 💾 **Flexible Storage**: Local JSON storage or Firestore integration
- 🔄 **Scheduled Runs**: Built-in scheduling support for cost-efficient batch processing
- 📈 **Cost Optimized**: < $1/month for typical usage (Gemini tokens only)
- 🐳 **Cloud Ready**: Docker + Cloud Run deployment configuration included

## Quick Start

### Prerequisites

- Python 3.11+
- Google AI Pro membership (for Gemini API key)
- Alpha Vantage API key (free tier)
- Docker (optional, for deployment)

### Local Development

1. **Clone and setup**:
   ```bash
   cd google-stock-agent
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # - GEMINI_API_KEY (from Google AI Studio)
   # - ALPHA_VANTAGE_API_KEY (from Alpha Vantage)
   ```

3. **Run the API**:
   ```bash
   python main.py
   ```
   
   API will be available at `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Docker Development

```bash
docker-compose up --build
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Get Stock Quote
```bash
GET /stocks/quote/{symbol}
# Example: curl http://localhost:8000/stocks/quote/AAPL
```

### Analyze Single Stock
```bash
POST /analyze/single/{symbol}
# Example: curl -X POST http://localhost:8000/analyze/single/AAPL
```

### Analyze Batch (All Configured Stocks)
```bash
POST /analyze/batch
# Example: curl -X POST http://localhost:8000/analyze/batch
```

### Get Analysis History
```bash
GET /history/{symbol}
# Example: curl http://localhost:8000/history/AAPL
```

### Get Configuration
```bash
GET /config
```

## Configuration

Edit `.env` to customize:

```env
# API Keys
GEMINI_API_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key

# Stocks to monitor (comma-separated)
STOCKS_TO_MONITOR=AAPL,MSFT,GOOGL,AMZN,NVDA

# Scheduling
CHECK_FREQUENCY_HOURS=4

# Firestore (optional)
USE_FIRESTORE=false
FIREBASE_CREDENTIALS_PATH=path/to/credentials.json
```

## Project Structure

```
google-stock-agent/
├── main.py                 # FastAPI application
├── src/
│   ├── config.py          # Configuration management
│   ├── stock_fetcher.py   # Alpha Vantage integration
│   ├── gemini_agent.py    # Gemini AI analysis
│   └── storage.py         # Data persistence
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Local development setup
├── requirements.txt       # Python dependencies
└── data/                  # Local storage (created at runtime)
```

## Deployment

### Google Cloud Run (Recommended)

1. **Build and push image**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/stock-agent
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy stock-agent \
     --image gcr.io/PROJECT_ID/stock-agent \
     --region us-central1 \
     --platform managed \
     --memory 512Mi \
     --set-env-vars GEMINI_API_KEY=xxx,ALPHA_VANTAGE_API_KEY=yyy
   ```

3. **Schedule runs with Cloud Scheduler** (optional):
   ```bash
   gcloud scheduler jobs create http stock-agent-batch \
     --schedule="0 8,13,16 * * 1-5" \
     --uri=https://YOUR_CLOUD_RUN_URL/analyze/batch \
     --http-method=POST \
     --oidc-service-account-email=YOUR_SERVICE_ACCOUNT@appspot.gserviceaccount.com
   ```

### Vercel (Optional Frontend)

Deploy a React dashboard to display results on Vercel's free hobby plan.

## Cost Estimation

### Minimal Setup (10 stocks, 1x daily)
- Gemini tokens: **$0.19/month**
- Stock APIs: **$0** (free tier)
- Cloud Run: **$0** (free tier covers ~900k vCPU-seconds/month)
- **Total: $0.19/month**

### Moderate Setup (50 stocks, 3x daily)
- Gemini tokens: **$0.95/month**
- Stock APIs: **$0** (free tier)
- Cloud Run: **$0** (free tier)
- **Total: $0.95/month**

### Cost Reduction Tips
1. Use **Batch API** for 50% token discount (for non-urgent analysis)
2. **Cache results** locally for 1 hour to reduce redundant calls
3. **Batch multiple symbols** per Gemini request
4. Run during **off-peak hours** (Cloud Run cheaper)
5. Monitor **actual usage** via Cloud Logging

## Architecture

```
Scheduled Event (Cloud Scheduler / GitHub Actions)
        ↓
  Cloud Run Service
        ↓
  ┌─────────────────┬────────────────┐
  ↓                 ↓                 ↓
Stock Data      Gemini API     Storage (Local/Firestore)
(Alpha Vantage)  (Analysis)
```

## Models & APIs

- **Gemini Model**: `gemini-2.5-flash-lite` ($0.075 input / $0.30 output per 1M tokens)
- **Stock Data**: Alpha Vantage (5 req/min, real-time, free tier)
- **Alternative**: Finnhub, Yahoo Finance, Alpaca

## Limitations

- **Rate Limits**: Alpha Vantage 5 req/min (staggered with 12-second delays)
- **Gemini**: 2 requests/minute free tier (can process ~120 stocks/hour)
- **Execution Time**: Cloud Run 60-minute timeout
- **Data Freshness**: Market-hours only (NYSE: 9:30am - 4:00pm ET)

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black src/ main.py
isort src/ main.py
```

## Troubleshooting

### API Key Issues
- Ensure API keys are in `.env` and not committed to git
- Check `.gitignore` includes `.env`
- Use `Secret Manager` in production (not env vars)

### Rate Limit Errors
- Alpha Vantage: Stagger requests by 12 seconds minimum
- Gemini: Use batch requests to process multiple stocks
- Check Cloud Logging for error details

### Storage Issues
- Local: Ensure `data/` directory is writable
- Firestore: Check Firebase credentials and permissions

## Contributing

Contributions welcome! Areas for improvement:
- [ ] More stock data sources (Finnhub, IEX Cloud, Alpaca)
- [ ] WebSocket support for real-time data
- [ ] Advanced portfolio analysis
- [ ] Web dashboard (React/Next.js)
- [ ] Unit tests and CI/CD integration
- [ ] Prometheus metrics for monitoring

## License

MIT

## Support

For issues, questions, or suggestions:
1. Check existing [GitHub Issues](https://github.com/yourusername/google-stock-agent/issues)
2. Review the [Architecture Guide](ARCHITECTURE.md)
3. Check [Google Cloud Run Docs](https://cloud.google.com/run/docs)

## Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
