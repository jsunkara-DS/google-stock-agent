# LangChain vs LangGraph: Visual Guide

## 1. LangChain - Linear Workflows

### Simple Flowchart
```
┌─────────────┐
│   Stock     │
│   Data      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  LangChain PromptTemplate       │
│  Format: "Analyze {symbol}      │
│  at ${price} ({change}%)"       │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  LLM (Gemini)                   │
│  Single API call                │
│  Temperature: 0.7               │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐
│  Analysis   │
│  Output     │
└─────────────┘
```

### Code Example
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Step 1: Create template
prompt = ChatPromptTemplate.from_template(
    """Analyze {symbol} at ${price}
    Change: {change_percent}%
    
    Provide sentiment and action."""
)

# Step 2: Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

# Step 3: Format and run
messages = prompt.format_messages(
    symbol="AAPL",
    price=185.50,
    change_percent="1.17%"
)

# Step 4: Get response
result = llm.invoke(messages)
print(result.content)
```

---

## 2. LangGraph - Decision-Based Workflows

### Complex Flowchart with Branching
```
                    ┌──────────────────┐
                    │  Start: Stock    │
                    │  Data Input      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Node 1: Analyze  │
                    │ Sentiment        │
                    │ (Bullish/Bearish)│
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Node 2: Assess   │
                    │ Risk Level       │
                    │ (1-10)           │
                    └────────┬─────────┘
                             │
                    ┌────────┴────────┐
                    │   Decision      │
                    │   Router        │
                    └────┬────────┬───┘
         ┌──────────────┘ │        └──────────────┐
         │                │                       │
         ▼                ▼                       ▼
    High Risk      Neutral/Mixed           Low Risk
    (Risk>7)       (Risk 4-6)              (Risk<4)
         │                │                       │
         ▼                ▼                       ▼
    ┌─────────┐    ┌──────────┐            ┌──────────┐
    │ AVOID   │    │ HOLD     │            │ BUY      │
    │ SELL    │    │ WAIT     │            │ STRONG   │
    └────┬────┘    └────┬─────┘            └────┬─────┘
         │              │                       │
         └──────────┬───┴───────────────────────┘
                    │
                    ▼
          ┌──────────────────────┐
          │ End: Final Action    │
          │ + Reasoning          │
          └──────────────────────┘
```

### Code Example
```python
from langgraph.graph import StateGraph, END

# Step 1: Define State
class StockState:
    symbol: str
    price: float
    sentiment: str  # "bullish" or "bearish"
    risk_level: int  # 1-10
    action: str  # "BUY", "SELL", "HOLD"

# Step 2: Define Nodes (functions)
def analyze_sentiment(state):
    # Call LLM to determine sentiment
    state.sentiment = "bullish" if state.price > 100 else "bearish"
    return state

def assess_risk(state):
    # Calculate risk (simplified)
    state.risk_level = 5 if state.sentiment == "bullish" else 8
    return state

# Step 3: Define Router (conditional logic)
def route_decision(state):
    if state.risk_level > 7:
        return "high_risk"
    elif state.risk_level < 4:
        return "low_risk"
    else:
        return "neutral"

def handle_high_risk(state):
    state.action = "AVOID"
    return state

def handle_low_risk(state):
    state.action = "BUY"
    return state

# Step 4: Build Graph
graph = StateGraph(StockState)

# Add nodes
graph.add_node("analyze", analyze_sentiment)
graph.add_node("risk", assess_risk)
graph.add_node("buy", handle_low_risk)
graph.add_node("avoid", handle_high_risk)

# Connect nodes
graph.add_edge("analyze", "risk")
graph.add_conditional_edges(
    "risk",
    route_decision,
    {"high_risk": "avoid", "low_risk": "buy"}
)
graph.add_edge("buy", END)
graph.add_edge("avoid", END)

# Set entry point and compile
graph.set_entry_point("analyze")
workflow = graph.compile()

# Step 5: Run
result = workflow.invoke(initial_state)
print(result.action)  # "BUY" or "AVOID"
```

---

## 3. Real Stock Agent Examples

### Scenario: Should I buy TSLA?

#### With LangChain (Simple)
```
1. Get TSLA price: $250
2. Create prompt: "TSLA is $250, up 2.5%. Analyze."
3. Send to Gemini
4. Output: "TSLA shows bullish momentum..."

Result: Text analysis (no decision logic)
```

#### With LangGraph (Smart)
```
1. Get TSLA price: $250, change: +2.5%

2. ANALYZE SENTIMENT
   → "This is +2.5%, looks bullish"

3. ASSESS RISK
   → "Check trading volume, volatility"
   → Risk level: 5/10 (medium)

4. DECISION LOGIC
   Question: "Is this safe to buy?"
   → Sentiment = BULLISH ✓
   → Risk = MEDIUM (5) ✓
   → Decision: "BUY signal with 15% stop loss"

5. OUTPUT WITH REASONING
   {
     "action": "BUY",
     "entry": "$250",
     "stop_loss": "$212",
     "target": "$300",
     "confidence": "High (bullish sentiment + medium risk)"
   }
```

---

## 4. Key Differences Table

| Feature | LangChain | LangGraph |
|---------|-----------|-----------|
| **Use Case** | Sequential prompting | Agent workflows |
| **Complexity** | Simple (5 lines) | Complex (50+ lines) |
| **Decision Making** | No branching | If/else logic |
| **Memory** | Per chain | Across workflow |
| **Best For** | Q&A, Summarization | Decisions, Agents |
| **Example** | "Translate this" | "Should I buy?" |

---

## 5. Stock Agent Implementation Roadmap

### Phase 1: LangChain (Now)
```python
# Replace this:
analysis = gemini_agent.analyze_stock(quote)

# With this:
chain = StockAnalysisChain(api_key)
analysis = chain.analyze(quote)

Benefits:
- Prompt management easier
- Reusable templates
- Better error handling
```

### Phase 2: LangGraph (Advanced)
```python
# Add decision workflow:
graph = build_stock_analysis_graph(api_key)
result = graph.invoke(stock_state)

# Result includes:
- sentiment: "bullish"
- risk_level: 4
- action: "BUY"
- reasoning: "..."
- entry_price: 185
- stop_loss: 170
- target: 200

Benefits:
- Intelligent decision making
- Multiple analysis steps
- Conditional branching
- Better for portfolio decisions
```

---

## 6. Installation

```bash
# Install required packages
pip install langchain langchain-google-genai langgraph

# Update requirements.txt
pip freeze > requirements.txt
```

---

## 7. When to Use What

### Use LangChain When:
- ✅ Simple prompt → LLM → Output
- ✅ Chaining multiple sequential steps
- ✅ Want prompt templates and management
- ✅ No complex decision logic needed

**Examples:**
- Summarize earnings report
- Generate 3 trading ideas
- Format analysis into JSON

### Use LangGraph When:
- ✅ Multiple decision points
- ✅ Different outcomes based on conditions
- ✅ Agent-like behavior
- ✅ Complex workflow orchestration

**Examples:**
- Decide to buy/sell/hold
- Multi-factor analysis with branching
- Portfolio rebalancing rules
- Risk assessment workflow

---

## 8. Integration with Your Stock Agent

### Current Structure
```
main.py
├── StockFetcher (Alpha Vantage)
├── GeminiAgent (Basic prompt)
└── StorageService (Save results)
```

### With LangChain
```
main.py
├── StockFetcher
├── StockAnalysisChain (LangChain)
│   ├── PromptTemplate
│   └── ChatGoogleGenerativeAI
└── StorageService
```

### With LangGraph
```
main.py
├── StockFetcher
├── IntelligentAnalysisGraph (LangGraph)
│   ├── analyze_sentiment (Node)
│   ├── assess_risk (Node)
│   ├── route_decision (Router)
│   ├── high_risk_handler (Node)
│   └── low_risk_handler (Node)
└── StorageService
```

---

## 9. Quick Start Code

```python
# Install
pip install langchain langchain-google-genai

# Quick LangChain example
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Create template
template = """Analyze {stock}:
Price: ${price}
Change: {change}%
Recommend: buy/sell/hold?"""

prompt = ChatPromptTemplate.from_template(template)

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

# Format and run
messages = prompt.format_messages(
    stock="AAPL",
    price=185,
    change=1.2
)

result = llm.invoke(messages)
print(result.content)
```

This is the foundation. LangGraph adds the decision logic on top!
