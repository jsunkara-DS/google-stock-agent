# Architecture Guide

## System Design

```
┌──────────────────────────────────────────────────────────────┐
│                    Stock Agent Architecture                   │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│ Trigger Sources     │
├─────────────────────┤
│ • Cloud Scheduler   │  Cron: 8am, 1pm, 4pm (market hours)
│ • GitHub Actions    │  Alternative: Free CI/CD trigger
│ • HTTP API Calls    │  Manual/external triggers
└────────┬────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│         Google Cloud Run (Serverless)                │
│  Memory: 512Mi | CPU: 1 vCPU | Timeout: 120s       │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────────────────────────────────────┐   │
│  │  FastAPI Application (main.py)              │   │
│  │  ├─ Health checks                           │   │
│  │  ├─ Quote endpoints                         │   │
│  │  ├─ Analysis endpoints                      │   │
│  │  └─ Config/History endpoints                │   │
│  └────────────┬──────────────────┬─────────────┘   │
│               │                  │                  │
│  ┌────────────▼────┐  ┌──────────▼──────┐         │
│  │ Stock Fetcher   │  │ Gemini Agent    │         │
│  │ (src/stock_     │  │ (src/gemini_    │         │
│  │  fetcher.py)    │  │  agent.py)      │         │
│  │                 │  │                 │         │
│  │ • Rate limiting │  │ • AI analysis   │         │
│  │ • Caching       │  │ • Batch API     │         │
│  │ • Error handler │  │ • Cost optimize │         │
│  └─────────────────┘  └─────────────────┘         │
│                                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │  Storage Service (src/storage.py)            │   │
│  │  ├─ Local JSON (default)                     │   │
│  │  └─ Firestore (optional)                     │   │
│  └──────────────────────────────────────────────┘   │
│                                                       │
└────────┬─────────────────────┬──────────────────────┘
         │                     │
         ▼                     ▼
    ┌────────────┐      ┌──────────────┐
    │ Alpha      │      │ Google       │
    │ Vantage    │      │ Gemini API   │
    │ API        │      │              │
    └────────────┘      └──────────────┘
         │                     │
         │ Real-time quotes    │ Analysis
         │ (Rate limit: 5/min) │ (2 req/min free)
         │                     │

    ┌──────────────────────────────────────┐
    │ Data Storage                         │
    ├──────────────────────────────────────┤
    │ Local: data/{symbol}/analysis_*.json │
    │ Cloud: Firestore (optional)          │
    └──────────────────────────────────────┘
```

## Cost Optimization Strategy

### 1. Batch Processing
- **One request per 5 stocks** instead of one per stock
- **Savings**: 80% reduction in Gemini requests
- Implementation: `analyze/batch` endpoint

### 2. Rate Limit Handling
- **12-second stagger** between stock API calls (5 req/min limit)
- **Cache results** for 60 minutes (local)
- **Fallback**: Use cached data on API errors

### 3. Scheduling
- **3x daily** (8am, 1pm, 4pm ET) during market hours
- **Not 24/7** = 50% execution cost vs. real-time
- Uses Cloud Scheduler (free tier: 3 jobs)

### 4. Model Selection
- **Gemini 2.5 Flash-Lite**: $0.075 input / $0.30 output
- **15x cheaper** than Pro models
- Sufficient for stock analysis task

### 5. Cloud Run Efficiency
- **512Mi memory**: Minimal but sufficient
- **0 min instances**: Scale to zero when not running
- **Auto-shutdown**: 120s timeout prevents hanging
- **Free tier**: 180k vCPU-seconds/month covers ~4.5k requests

## Data Flow

### Single Stock Analysis
```
1. User calls POST /analyze/single/{symbol}
2. StockFetcher.fetch_quote(symbol)
   - Check cache (1 hour TTL)
   - If expired, fetch from Alpha Vantage
   - Rate limit: wait if needed
3. GeminiAgent.analyze_stock(quote)
   - Build prompt with price, change, volume
   - Call Gemini 2.5 Flash-Lite API
   - Return analysis text
4. StorageService.save_analysis(result)
   - Save to data/{symbol}/analysis_{timestamp}.json
5. Return StockAnalysis response
```

### Batch Analysis
```
1. User calls POST /analyze/batch
2. For each configured stock (e.g., 50):
   StockFetcher.fetch_multiple(symbols)
   - Fetch all quotes respecting rate limits
   - Results: {AAPL: {...}, MSFT: {...}, ...}
3. GeminiAgent.analyze_multiple(all_quotes)
   - Single Gemini request with all 50 stocks
   - Batch response: All analyses in one call
4. StorageService.save_batch_analysis(results)
   - Save all 50 results to local storage
5. Return summary with all analyses
```

## Configuration Management

```python
# src/config.py uses pydantic-settings
settings = Settings()  # Auto-loads from .env

Key configs:
├─ API Keys
│  ├─ GEMINI_API_KEY
│  └─ ALPHA_VANTAGE_API_KEY
├─ Stock List
│  ├─ STOCKS_TO_MONITOR
│  └─ CHECK_FREQUENCY_HOURS
├─ Storage
│  ├─ USE_FIRESTORE
│  └─ FIREBASE_CREDENTIALS_PATH
└─ Environment
   ├─ ENVIRONMENT (dev/prod)
   └─ LOG_LEVEL
```

## Error Handling & Resilience

### Stock Fetcher Errors
```
Rate limit (Note in response)
  → Log warning, return None
  → Caller uses cached value

Invalid API key
  → Log error, return None
  → Skip stock in batch

Network timeout
  → Retry with exponential backoff
  → Use cached data if available
```

### Gemini API Errors
```
Auth failure
  → Check API key in logs
  → Gracefully skip analysis

Rate limit (2 req/min)
  → Free tier: Serialize requests
  → Batch API reduces frequency

Token limit exceeded
  → Reduce prompt size
  → Analyze fewer symbols per batch
```

## Performance Characteristics

| Operation | Time | Cost | Notes |
|-----------|------|------|-------|
| Fetch 1 quote | 2s | $0 | Rate limited by Alpha Vantage |
| Analyze 1 stock | 5s | $0.004 | Gemini request + tokens |
| Batch 50 stocks | 120s | $0.02 | 50 fetches + 1 analysis call |
| 3x daily batch | N/A | $0.60 | 50 stocks, 3 batches/day |

## Scaling Considerations

### Current Design (50 stocks, 3x daily)
- Cloud Run: 9k vCPU-seconds/month (free)
- Gemini: 3.15M tokens/month ($0.95)
- Storage: <5MB/month (free)
- **Total: $0.95/month**

### If Scaling to 500 Stocks
- Cloud Run: 90k vCPU-seconds/month (free)
- Gemini: 31.5M tokens/month ($9.50)
- Add Firestore: ~$5/month
- **Total: ~$15/month**

### If Real-Time (Every 5 minutes)
- Cloud Run: 2.6M vCPU-seconds/month ($60)
- Gemini: 450M tokens/month ($135)
- **Total: ~$200+/month**

## Monitoring & Observability

### Logs
```bash
# Cloud Logging (free tier: 50GB ingestion)
gcloud logging read resource.type=cloud_run_revision
```

### Metrics
- **Execution time**: Track slow requests
- **Error rate**: Monitor API failures
- **Token usage**: Track Gemini costs
- **Cache hit rate**: Measure effectiveness

### Alerts
```bash
# Set up in Cloud Console
- If error rate > 5%
- If avg execution time > 30s
- If cost projection > budget
```

## Future Enhancements

1. **Real-time WebSocket**: Use Alpha Vantage websocket for streaming data
2. **Advanced Analysis**: Multi-stock correlation, portfolio analysis
3. **Portfolio Tracking**: Store user portfolios, track performance
4. **Alerts**: Notify on price targets, volume spikes
5. **ML Models**: Predict price movements (needs more compute)
6. **Multiple Providers**: Finnhub, IEX, Alpaca integration
7. **Dashboard**: React frontend with real-time updates
8. **Mobile App**: iOS/Android for on-the-go analysis

## Security Best Practices

✅ **Implemented**
- Environment variables for secrets (not hardcoded)
- Cloud Secret Manager ready (see DEPLOYMENT.md)
- Rate limiting to prevent abuse
- Input validation (pydantic models)
- CORS middleware for web safety

⚠️ **TODO**
- Authentication (API keys for public deployment)
- Request signing (verify Cloud Scheduler calls)
- SQL injection prevention (if adding database)
- Rate limiting per user (if multi-tenant)
- Data encryption at rest (Firestore native)

## Compliance Notes

- **Data**: Stock prices are public, no PII handling
- **Terms**: Respect Alpha Vantage, Gemini API terms
- **Attribution**: Display API credits as required
- **Archival**: Consider 30-day retention for local data
