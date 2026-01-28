# LangChain vs LangGraph - Quick Cheat Sheet

## One-Minute Explanation

### LangChain = Prompt Management
```
Your Prompt → Template → Format Data → Send to LLM → Get Answer
```
**Good for:** Q&A, summarization, simple analysis
**Complexity:** Low
**Lines of code:** 10-20

### LangGraph = Workflow Engine  
```
Start → Step 1 → Decision → Step 2A or 2B → Step 3 → End
```
**Good for:** Decisions, agents, complex workflows
**Complexity:** Medium
**Lines of code:** 50-100

---

## Stock Agent Example

### Using LangChain (Simple)
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Create template
prompt = ChatPromptTemplate.from_template(
    "Analyze {symbol} at ${price}. Sentiment?"
)

# Use it
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
result = llm.invoke(prompt.format_messages(symbol="AAPL", price=185))
print(result.content)  # "AAPL shows bullish momentum..."
```
**Result:** Text analysis ✓

### Using LangGraph (Smart)
```python
from langgraph.graph import StateGraph, END

class State:
    symbol: str
    sentiment: str
    risk_level: int
    recommendation: str

# Build workflow
graph = StateGraph(State)
graph.add_node("analyze", my_analyze_func)
graph.add_node("assess", my_assess_func)
graph.add_node("decide", my_decide_func)
graph.add_edge("analyze", "assess")
graph.add_conditional_edges("assess", router, {"buy": "decide"})
workflow = graph.compile()

# Use it
result = workflow.invoke(initial_state)
print(result.recommendation)  # "BUY" ✓
```
**Result:** Recommendation + reasoning + risk level ✓✓✓

---

## Side-by-Side Comparison

| Feature | LangChain | LangGraph |
|---------|-----------|-----------|
| **Setup** | 5 min | 30 min |
| **Lines** | ~20 | ~100 |
| **Learns?** | No | Yes (conditional) |
| **Makes decisions?** | No | Yes |
| **Can branch?** | No | Yes |
| **Best for** | Q&A | Decisions |
| **Cost** | Same | Same |

---

## Quick Decision Tree

```
Do you need...

├─ Simple text analysis?
│  └─ Use LangChain ✓
│
├─ Multiple analysis steps?
│  └─ Use LangChain + chains ✓✓
│
├─ If/else logic?
│  └─ Use LangGraph ✓✓✓
│
├─ Different outputs based on conditions?
│  └─ Use LangGraph ✓✓✓
│
└─ Smart agent that makes decisions?
   └─ Use LangGraph ✓✓✓✓
```

---

## For Your Stock Agent

### Now (Day 1)
```python
# Use LangChain to manage prompts
from langchain.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template("Analyze {symbol}...")
# Easy win: Better prompt organization
```

### Later (Week 1)
```python
# Use LangGraph for decisions
from langgraph.graph import StateGraph
graph = StateGraph(StockState)
# Add: workflow, routing, logic
# Result: BUY/SELL/HOLD recommendations
```

### Advanced (Week 2+)
```python
# Add memory and multi-stock analysis
# Maintain state across multiple stocks
# Build portfolio recommendations
```

---

## Installation

```bash
# One command
pip install langchain langchain-google-genai langgraph

# Already have google.generativeai?
# No problem! LangChain wraps it nicely.
```

---

## Key Differences at a Glance

### LangChain
- **What:** Prompt templates + Chain execution
- **When:** You need structured prompts, sequential steps
- **Example:** "Summarize earnings", "Translate to Spanish"
- **Code:** Functional, easy to read
- **Integration:** Drop-in replacement for gemini_agent.py

### LangGraph
- **What:** State machine for workflows
- **When:** You need conditional logic, decision trees
- **Example:** "Should I buy this stock?", "Route based on risk"
- **Code:** Graph-based, nodes and edges
- **Integration:** New abstraction layer

---

## Your Stock Agent Roadmap

```
Week 1: LangChain
├─ Learn prompt templates
├─ Replace gemini_agent.py
├─ Same functionality, better code
└─ Zero risk (drop-in replacement)

Week 2: LangGraph
├─ Learn StateGraph
├─ Add sentiment analysis node
├─ Add risk assessment node
├─ Add decision router
└─ New /recommend endpoint

Week 3+: Advanced
├─ Add memory/history
├─ Multi-stock workflows
├─ Portfolio analysis
└─ Custom agents
```

---

## Real Examples

### LangChain Example Output
```
Input: "Analyze AAPL at $185.50, up 1.17%"
Output: "AAPL shows bullish momentum with strong volume.
         Potential breakout expected. Consider small position."
```

### LangGraph Example Output
```
Input: AAPL at $185.50, up 1.17%, volume 45M
Step 1: Analyze Sentiment → BULLISH
Step 2: Assess Risk → 4/10 (Low)
Step 3: Route Decision → Buy Path
Output: {
  "recommendation": "🟢 BUY",
  "entry": "$185",
  "stop_loss": "$170",
  "target": "$210",
  "confidence": "HIGH"
}
```

---

## Files to Check Out

### Simple (LangChain)
- [`langchain_examples.py`](langchain_examples.py) - Basic examples
- [`LANGCHAIN_GUIDE.md`](LANGCHAIN_GUIDE.md) - Full guide

### Advanced (LangGraph)  
- [`practical_langchain_langgraph.py`](practical_langchain_langgraph.py) - Working code
- [`INTEGRATION_GUIDE.md`](INTEGRATION_GUIDE.md) - Integration steps

---

## FAQ

**Q: Will this break my current code?**
A: LangChain is a drop-in replacement. No breaking changes.

**Q: Do I need both?**
A: No. Start with LangChain, upgrade to LangGraph if needed.

**Q: What about costs?**
A: Same API calls = same cost. No price difference.

**Q: Can I use just LangGraph without LangChain?**
A: Yes, but LangChain is still useful for prompts.

**Q: How long to implement?**
A: LangChain: 30 min. LangGraph: 2-3 hours.

**Q: Is it worth it?**
A: If you want smart recommendations (BUY/SELL/HOLD) → YES
  If you just need text → Maybe not yet

---

## Next Steps

1. **Today:** Read this cheat sheet ✓
2. **Tomorrow:** Try LangChain example
3. **This week:** Integrate into your agent
4. **Next week:** Add LangGraph for decisions
5. **Going forward:** Build advanced workflows

---

## Quick Start Commands

```bash
# Install
pip install langchain langchain-google-genai langgraph

# Try example
python practical_langchain_langgraph.py

# Add to requirements
pip freeze > requirements.txt

# Test with API
curl -X POST http://localhost:8000/analyze/single/AAPL
```

---

## Remember

- **LangChain** = Better prompts
- **LangGraph** = Smart decisions  
- **Together** = Powerful AI workflows

Choose based on your needs. Start simple, scale as needed.

🚀 Ready to upgrade your stock agent?
