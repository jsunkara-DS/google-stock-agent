# Quick Start Guide

Get your Google AI stock agent running in 5 minutes.

## Step 1: Get API Keys (5 min)

### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

### Alpha Vantage API Key
1. Go to [Alpha Vantage](https://www.alphavantage.co/api/)
2. Enter your email, get instant API key
3. Copy the key

## Step 2: Clone & Setup (2 min)

### Windows
```cmd
# Open Command Prompt, navigate to where you want the project
cd C:\projects

# Clone or create the folder
git clone https://github.com/yourusername/google-stock-agent.git
cd google-stock-agent

# Run setup
setup.bat

# Activate virtual environment
venv\Scripts\activate.bat
```

### macOS/Linux
```bash
cd ~/projects
git clone https://github.com/yourusername/google-stock-agent.git
cd google-stock-agent

chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

## Step 3: Configure API Keys (1 min)

```bash
# Copy example env file
cp .env.example .env

# Edit .env file and paste your API keys
# Windows: notepad .env
# macOS/Linux: nano .env
```

Your `.env` should look like:
```env
GEMINI_API_KEY=sk-Rz...(your gemini key)
ALPHA_VANTAGE_API_KEY=XXXXX...(your alpha vantage key)
STOCKS_TO_MONITOR=AAPL,MSFT,GOOGL,AMZN,NVDA
CHECK_FREQUENCY_HOURS=4
```

## Step 4: Run Locally (2 min)

### Option A: Direct Python
```bash
# Make sure venv is activated
python main.py
```

Output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Option B: Docker (if installed)
```bash
docker-compose up --build
```

## Step 5: Test the API

Open your browser or use curl:

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-24T15:30:45.123456",
  "services": {
    "stock_fetcher": "ready",
    "gemini_agent": "ready",
    "storage": "ready"
  }
}
```

### Get Stock Quote
```bash
curl http://localhost:8000/stocks/quote/AAPL
```

Response:
```json
{
  "symbol": "AAPL",
  "price": 185.50,
  "change": 2.15,
  "change_percent": "1.17%",
  "timestamp": "2026-01-24T15:30:45.123456",
  "volume": "45231000",
  "previous_close": 183.35
}
```

### Analyze Single Stock
```bash
curl -X POST http://localhost:8000/analyze/single/AAPL
```

Response:
```json
{
  "symbol": "AAPL",
  "price": 185.50,
  "change_percent": "1.17%",
  "analysis": "AAPL shows strong bullish momentum with a 1.17% gain...",
  "timestamp": "2026-01-24T15:30:45.123456"
}
```

### Analyze All Stocks (Batch)
```bash
curl -X POST http://localhost:8000/analyze/batch
```

## Interactive Documentation

Open your browser to: **http://localhost:8000/docs**

This gives you a beautiful interactive API explorer where you can:
- See all endpoints
- Read parameter descriptions
- Test requests directly
- View response schemas

## Project Structure

```
google-stock-agent/
├── main.py              # FastAPI application (START HERE)
├── requirements.txt     # Python dependencies
├── .env.example        # Example config (COPY TO .env)
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── README.md           # Full documentation
├── DEPLOYMENT.md       # Cloud Run deployment guide
├── ARCHITECTURE.md     # System design details
│
├── src/
│   ├── config.py       # Configuration management
│   ├── stock_fetcher.py # Alpha Vantage API integration
│   ├── gemini_agent.py  # Gemini AI analysis
│   ├── storage.py      # Data persistence
│   └── batch_processor.py # Batch processing utilities
│
├── config/
│   ├── cloud-run-service.yaml      # Kubernetes config
│   └── cloud-scheduler-job.yaml    # Scheduler config
│
└── data/               # Local storage (created at runtime)
```

## Next Steps

### Option 1: Local Development
1. ✅ You're running locally
2. Explore the API via http://localhost:8000/docs
3. Modify stocks in `.env` to monitor different symbols
4. Implement additional features

### Option 2: Deploy to Cloud Run
1. Follow the [DEPLOYMENT.md](DEPLOYMENT.md) guide
2. Takes 15 minutes to deploy
3. Costs ~$1/month to run
4. Set up Cloud Scheduler for automatic runs
5. Estimated setup time: 30 minutes

### Option 3: Deploy to GitHub + Actions
1. Push to GitHub
2. Use GitHub Actions to run scheduled jobs
3. Free tier covers everything
4. See [DEPLOYMENT.md](DEPLOYMENT.md) for setup

## Customization

### Change Stocks to Monitor
Edit `.env`:
```env
STOCKS_TO_MONITOR=TSLA,AMZN,META,NVDA
```

### Change Check Frequency
Edit `.env`:
```env
CHECK_FREQUENCY_HOURS=2  # Check every 2 hours instead of 4
```

### Add More Stocks
Simply add to the comma-separated list:
```env
STOCKS_TO_MONITOR=AAPL,MSFT,GOOGL,AMZN,NVDA,TSLA,META,NVDA,AMD,INTC
```

### Enable Firestore
1. Set up Firebase project
2. Download credentials JSON
3. Edit `.env`:
```env
USE_FIRESTORE=true
FIREBASE_CREDENTIALS_PATH=path/to/credentials.json
```

## Common Issues

### ModuleNotFoundError
Make sure virtual environment is activated:
```bash
# Windows
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

### API Key Invalid
```bash
# Check .env file exists and has correct keys
cat .env

# Verify keys work (Gemini)
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY')"
```

### Port 8000 Already in Use
```bash
# Use a different port
python main.py --port 8001
# Or kill the process using it (Windows):
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Rate Limit Errors
Normal when testing. The API automatically handles rate limits by:
- Waiting between requests (Alpha Vantage: 12 seconds)
- Caching results (60 minute TTL)
- Gracefully skipping failed symbols

## Monitoring Costs

### Local Development
- **Free** (you're just testing)

### Cloud Run
Check your actual costs:
```bash
gcloud billing accounts list
gcloud compute billing-accounts describe [ACCOUNT_ID]
```

### Expected Monthly Costs
- **10 stocks, 1x daily**: $0.19
- **50 stocks, 3x daily**: $0.95
- **100 stocks, 5x daily**: $3.17

These are Gemini API costs only (stock data is free).

## Support & Resources

### Documentation
- [README.md](README.md) - Full reference
- [DEPLOYMENT.md](DEPLOYMENT.md) - Cloud Run setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design

### Official Docs
- [Google Gemini API](https://ai.google.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [Cloud Run](https://cloud.google.com/run/docs)

### Sample API Calls

**Get quotes for multiple stocks:**
```bash
curl http://localhost:8000/stocks/quote/AAPL
curl http://localhost:8000/stocks/quote/MSFT
curl http://localhost:8000/stocks/quote/GOOGL
```

**Analyze multiple stocks (batch is more efficient):**
```bash
curl -X POST http://localhost:8000/analyze/batch
```

**Check configuration:**
```bash
curl http://localhost:8000/config
```

## Tips for Success

✅ **Do**
- Keep API keys in `.env` (never commit to git)
- Use batch endpoint for multiple stocks (cheaper)
- Monitor costs in first week of Cloud deployment
- Review logs regularly for errors

❌ **Don't**
- Commit `.env` to version control
- Try to fetch data outside market hours (9:30am - 4:00pm ET)
- Use real-time mode without proper planning (expensive)
- Exceed Alpha Vantage rate limits (5 req/min)

## Performance Tips

1. **Batch processing is cheaper**: 1 Gemini request for 50 stocks vs. 50 requests
2. **Cache local data**: Reuse results within 1 hour (60-minute TTL)
3. **Run during market hours**: 3 times daily (8am, 1pm, 4pm ET)
4. **Monitor volume**: High volume days may see rate limiting

## Next Level: Enhancements

Once running, consider adding:
- [ ] Web dashboard (React frontend on Vercel)
- [ ] Email/SMS alerts on price targets
- [ ] Portfolio tracking
- [ ] Historical data archival
- [ ] Multiple data sources (Finnhub, Alpaca)
- [ ] Machine learning predictions
- [ ] Mobile app

Ready to start? Run `python main.py` and visit http://localhost:8000/docs! 🚀
