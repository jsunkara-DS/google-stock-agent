"""
Integration Guide: How to Add LangChain/LangGraph to Your Stock Agent

Shows how to replace existing code with LangChain/LangGraph versions
"""

# ============================================================================
# BEFORE: Your Current Implementation (gemini_agent.py)
# ============================================================================

BEFORE_CODE = """
# OLD WAY (Current)
class GeminiAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.client = genai.Client()
    
    def analyze_stock(self, stock_data: Dict) -> Optional[str]:
        prompt = f'''Analyze {stock_data['symbol']} at ${stock_data['price']}
        Change: {stock_data['change_percent']}%
        
        Provide:
        1. Sentiment
        2. Trading signal
        3. Risk assessment'''
        
        response = genai.GenerativeModel("gemini-2.5-flash-lite").generate_content(prompt)
        return response.text

# Usage in main.py
agent = GeminiAgent(api_key)
analysis = agent.analyze_stock(quote)

# Problems:
# ❌ Hard to reuse prompts
# ❌ No error handling
# ❌ No conditional logic
# ❌ No decision framework
"""

# ============================================================================
# AFTER: LangChain Version (Drop-in Replacement)
# ============================================================================

AFTER_LANGCHAIN = """
# NEW WAY (LangChain)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

class LangChainStockAgent:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=api_key,
            temperature=0.7
        )
        
        # Reusable prompt template
        self.template = ChatPromptTemplate.from_template(
            '''Analyze {symbol} at ${price}
            Change: {change_percent}%
            
            Provide:
            1. Sentiment (bullish/bearish/neutral)
            2. Trading signal (buy/sell/hold)
            3. Risk (1-10)
            
            Be concise.'''
        )
    
    def analyze_stock(self, stock_data: Dict) -> Optional[str]:
        messages = self.template.format_messages(**stock_data)
        response = self.llm.invoke(messages)
        return response.content

# Usage in main.py (exactly the same!)
agent = LangChainStockAgent(api_key)
analysis = agent.analyze_stock(quote)

# Benefits:
# ✅ Prompt templates are reusable
# ✅ Better error handling
# ✅ Easy to modify prompts
# ✅ Foundation for LangGraph
"""

# ============================================================================
# ADVANCED: LangGraph Version (Smart Decision-Making)
# ============================================================================

AFTER_LANGGRAPH = """
# ADVANCED (LangGraph with Decision Logic)
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dataclasses import dataclass

@dataclass
class StockAnalysisState:
    symbol: str
    price: float
    change_percent: float
    # Intermediate
    sentiment: str = ""
    risk_level: int = 0
    # Final
    recommendation: str = ""
    reasoning: str = ""

class LangGraphStockAgent:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=api_key
        )
        self.workflow = self._build_graph()
    
    def _build_graph(self):
        graph = StateGraph(StockAnalysisState)
        
        # Define nodes
        graph.add_node("sentiment", self._analyze_sentiment)
        graph.add_node("risk", self._assess_risk)
        graph.add_node("buy", self._recommendation_buy)
        graph.add_node("sell", self._recommendation_sell)
        graph.add_node("hold", self._recommendation_hold)
        
        # Connect edges
        graph.add_edge("sentiment", "risk")
        graph.add_conditional_edges(
            "risk",
            self._route,
            {"buy": "buy", "sell": "sell", "hold": "hold"}
        )
        graph.add_edge("buy", END)
        graph.add_edge("sell", END)
        graph.add_edge("hold", END)
        
        graph.set_entry_point("sentiment")
        return graph.compile()
    
    def _analyze_sentiment(self, state):
        # LLM call to determine sentiment
        state.sentiment = "bullish" if state.change_percent > 0 else "bearish"
        return state
    
    def _assess_risk(self, state):
        # LLM call to assess risk
        state.risk_level = 5  # 1-10 scale
        return state
    
    def _route(self, state):
        if state.sentiment == "bullish" and state.risk_level < 5:
            return "buy"
        elif state.sentiment == "bearish" and state.risk_level > 6:
            return "sell"
        return "hold"
    
    def _recommendation_buy(self, state):
        state.recommendation = "BUY"
        state.reasoning = "Bullish sentiment with low risk"
        return state
    
    def _recommendation_sell(self, state):
        state.recommendation = "SELL"
        state.reasoning = "Bearish sentiment with high risk"
        return state
    
    def _recommendation_hold(self, state):
        state.recommendation = "HOLD"
        state.reasoning = "Mixed signals"
        return state
    
    def analyze_stock(self, stock_data: Dict) -> Dict:
        state = StockAnalysisState(
            symbol=stock_data["symbol"],
            price=stock_data["price"],
            change_percent=float(stock_data["change_percent"])
        )
        result = self.workflow.invoke(state)
        return {
            "symbol": result.symbol,
            "recommendation": result.recommendation,
            "reasoning": result.reasoning,
            "risk_level": result.risk_level
        }

# Usage in main.py
agent = LangGraphStockAgent(api_key)
result = agent.analyze_stock(quote)
print(result["recommendation"])  # "BUY", "SELL", or "HOLD"
"""

# ============================================================================
# STEP-BY-STEP INTEGRATION GUIDE
# ============================================================================

INTEGRATION_STEPS = """
╔═════════════════════════════════════════════════════════════════════════════╗
║         STEP-BY-STEP INTEGRATION GUIDE                                      ║
╚═════════════════════════════════════════════════════════════════════════════╝

STEP 1: Install packages
────────────────────────
$ pip install langchain langchain-google-genai langgraph
$ pip freeze > requirements.txt


STEP 2: Choose Your Level
──────────────────────────

Level 1 - Simple (Replace gemini_agent.py)
  Cost: 15 min
  Benefit: Better prompt management
  → Copy AFTER_LANGCHAIN code
  → Replace old analyze_stock()
  → No changes needed in main.py

Level 2 - Medium (Add decision logic)
  Cost: 45 min
  Benefit: Smart BUY/SELL/HOLD recommendations
  → Copy AFTER_LANGGRAPH code
  → Update API response models
  → Add new endpoints: /recommend/{symbol}

Level 3 - Advanced (Full workflow)
  Cost: 2-3 hours
  Benefit: Portfolio analysis, multi-step decisions
  → Add memory/state management
  → Create batch recommendation workflow
  → Update /analyze/batch to use graph


STEP 3: File Structure
──────────────────────
Current:
  src/
    ├── gemini_agent.py    ← Replace this
    ├── stock_fetcher.py
    └── storage.py

New (Level 1):
  src/
    ├── gemini_agent.py    ← Now uses LangChain
    ├── stock_fetcher.py
    └── storage.py

New (Level 2+):
  src/
    ├── gemini_agent.py    ← Old version (backup)
    ├── langgchain_agent.py ← NEW: LangChain version
    ├── langgraph_agent.py  ← NEW: LangGraph version
    ├── stock_fetcher.py
    └── storage.py


STEP 4: Update main.py
──────────────────────

FROM:
  from src.gemini_agent import GeminiAgent
  agent = GeminiAgent(settings.gemini_api_key)
  analysis = agent.analyze_stock(quote)

TO (Level 1 - LangChain):
  from src.langchain_agent import LangChainStockAgent
  agent = LangChainStockAgent(settings.gemini_api_key)
  analysis = agent.analyze_stock(quote)  # Same interface!

TO (Level 2 - LangGraph):
  from src.langgraph_agent import LangGraphStockAgent
  agent = LangGraphStockAgent(settings.gemini_api_key)
  result = agent.analyze_stock(quote)
  # result = {"recommendation": "BUY", "reasoning": "...", "risk_level": 5}


STEP 5: Update API Endpoints (if using LangGraph)
──────────────────────────────────────────────────

NEW ENDPOINT:
  POST /recommend/{symbol}
  Returns: {"recommendation": "BUY", "reasoning": "...", "confidence": 0.95}

EXISTING ENDPOINT (updated):
  POST /analyze/batch
  Returns: List of recommendations instead of just text


STEP 6: Test & Validate
────────────────────────

$ python -m pytest tests/
$ python verify_setup.py
$ curl -X POST http://localhost:8000/analyze/single/AAPL


STEP 7: Deploy
───────────────
$ gcloud builds submit --tag gcr.io/$PROJECT_ID/stock-agent
$ gcloud run deploy stock-agent --image ...
"""


# ============================================================================
# DETAILED EXAMPLE: Modify main.py
# ============================================================================

MAIN_PY_MODIFICATION = """
# main.py - BEFORE
from src.gemini_agent import GeminiAgent

# Initialize
gemini_agent = GeminiAgent(settings.gemini_api_key)

# Use
analysis = gemini_agent.analyze_stock(quote)


# main.py - AFTER (with LangGraph)
# from src.gemini_agent import GeminiAgent  # OLD
from src.langgraph_agent import LangGraphStockAgent  # NEW

# Initialize
gemini_agent = LangGraphStockAgent(settings.gemini_api_key)

# Use (same interface, better logic)
result = gemini_agent.analyze_stock(quote)

# Now result includes:
# {
#   "symbol": "AAPL",
#   "recommendation": "BUY",
#   "reasoning": "Bullish sentiment...",
#   "risk_level": 4,
#   "entry_price": 185,
#   "stop_loss": 170,
#   "target": 200
# }

# Add new endpoint
@app.post("/recommend/{symbol}")
async def get_recommendation(symbol: str):
    quote = stock_fetcher.fetch_quote(symbol)
    result = gemini_agent.analyze_stock(quote)
    return {
        "symbol": result["symbol"],
        "recommendation": result["recommendation"],
        "reasoning": result["reasoning"],
        "confidence": "high" if result["risk_level"] < 5 else "medium"
    }
"""


# ============================================================================
# COMPARISON TABLE
# ============================================================================

COMPARISON = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        INTEGRATION COMPARISON                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║ Aspect          │  Current        │  LangChain      │  LangGraph             ║
║ ────────────────┼─────────────────┼─────────────────┼──────────────────────  ║
║ Setup Time      │ 0 min           │ 5 min           │ 30 min                 ║
║ Code Changes    │ None            │ Minimal         │ Moderate               ║
║ API Changes     │ None            │ None            │ Yes (+new endpoint)    ║
║ Intelligence    │ Basic           │ Better          │ Smart ✓✓               ║
║ Features        │ Text only       │ Templates       │ Decision logic         ║
║ Decision Logic  │ No              │ No              │ Yes (BUY/SELL/HOLD) ✓ ║
║ Cost Impact     │ ~$1/month       │ ~$1/month       │ ~$1/month              ║
║ Learning Curve  │ Easy            │ Easy            │ Medium                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

RECOMMENDATION:
  • Start with LangChain (Level 1)
  • Upgrade to LangGraph (Level 2) after 2 weeks
  • Add memory/state for Level 3 later
"""


if __name__ == "__main__":
    import sys
    
    sections = {
        "1": ("BEFORE (Current Code)", BEFORE_CODE),
        "2": ("AFTER - LangChain", AFTER_LANGCHAIN),
        "3": ("AFTER - LangGraph", AFTER_LANGGRAPH),
        "4": ("Integration Steps", INTEGRATION_STEPS),
        "5": ("Update main.py", MAIN_PY_MODIFICATION),
        "6": ("Comparison Table", COMPARISON),
        "all": ("All Sections", None)
    }
    
    print("\n" + "="*80)
    print("INTEGRATION GUIDE: LangChain & LangGraph")
    print("="*80)
    print("\nChoose section to view:")
    print("\n  1. BEFORE (Your current code)")
    print("  2. AFTER - LangChain (Simple replacement)")
    print("  3. AFTER - LangGraph (Smart version)")
    print("  4. Integration Steps (How-to)")
    print("  5. Update main.py (Code changes)")
    print("  6. Comparison Table (Decision matrix)")
    print("  all. View everything")
    
    choice = input("\nEnter choice (1-6 or 'all'): ").strip()
    
    if choice == "all":
        for key in ["1", "2", "3", "4", "5", "6"]:
            title, content = sections[key]
            print("\n" + "="*80)
            print(title)
            print("="*80)
            print(content if content else "")
    elif choice in sections:
        title, content = sections[choice]
        print("\n" + "="*80)
        print(title)
        print("="*80)
        print(content if content else "")
    else:
        print("Invalid choice. Showing comparison...")
        print(COMPARISON)
