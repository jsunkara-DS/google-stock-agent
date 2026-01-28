#!/usr/bin/env python3
"""
Quick Visual Reference: LangChain vs LangGraph
Run this file to see beautiful ASCII diagrams and comparisons
"""

def print_title(text):
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80)

def print_section(title):
    print(f"\n{'─'*80}")
    print(f"📌 {title}")
    print(f"{'─'*80}")

# ============================================================================
print_title("LANGCHAIN vs LANGGRAPH - QUICK VISUAL REFERENCE")

# ============================================================================
print_section("1. WHAT IS LANGCHAIN?")

langchain_visual = """
┌─────────────────────────────────────────────────────┐
│           LangChain: Prompt Management              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Your Code                                          │
│     │                                               │
│     ▼                                               │
│  ┌─────────────────────────────────────────────┐   │
│  │  ChatPromptTemplate                         │   │
│  │  "Analyze {symbol} at ${price}"             │   │
│  └──────────────┬──────────────────────────────┘   │
│                 │                                    │
│                 ▼                                    │
│  ┌─────────────────────────────────────────────┐   │
│  │  Format Messages                            │   │
│  │  {symbol: "AAPL", price: 185.50}            │   │
│  └──────────────┬──────────────────────────────┘   │
│                 │                                    │
│                 ▼                                    │
│  ┌─────────────────────────────────────────────┐   │
│  │  ChatGoogleGenerativeAI                     │   │
│  │  Gemini 2.5 Flash-Lite                      │   │
│  └──────────────┬──────────────────────────────┘   │
│                 │                                    │
│                 ▼                                    │
│         Analysis Output                             │
│  "AAPL shows bullish momentum..."                  │
│                                                     │
└─────────────────────────────────────────────────────┘

Key Points:
  ✓ Manages prompts with templates
  ✓ Formats input data
  ✓ Calls LLM
  ✓ Returns text
"""
print(langchain_visual)

# ============================================================================
print_section("2. WHAT IS LANGGRAPH?")

langgraph_visual = """
┌──────────────────────────────────────────────────────────┐
│      LangGraph: Intelligent Workflow Engine              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                    Input State                           │
│                  (symbol, price, ...)                    │
│                         │                                 │
│                         ▼                                 │
│              ┌──────────────────────┐                    │
│              │ Node 1: Analyze      │                    │
│              │ Sentiment            │                    │
│              │ (bullish/bearish)    │                    │
│              └──────────┬───────────┘                    │
│                         │                                 │
│                         ▼                                 │
│              ┌──────────────────────┐                    │
│              │ Node 2: Assess       │                    │
│              │ Risk (1-10)          │                    │
│              └──────────┬───────────┘                    │
│                         │                                 │
│                    Decision? ◇                           │
│            ┌─────────────┼──────────────┐                │
│            │             │              │                 │
│       High Risk     Medium Risk    Low Risk              │
│    (Risk > 7)      (4-6)         (< 4)                  │
│            │             │              │                 │
│            ▼             ▼              ▼                 │
│        ┌─────────┐  ┌─────────┐  ┌──────────┐            │
│        │ SELL    │  │ HOLD    │  │ BUY      │            │
│        │ AVOID   │  │ WAIT    │  │ STRONG   │            │
│        └────┬────┘  └────┬────┘  └────┬─────┘            │
│            │             │             │                  │
│            └─────────┬───┴─────────────┘                 │
│                      │                                    │
│                      ▼                                    │
│           Output Recommendation                          │
│      {                                                   │
│        "recommendation": "BUY",                          │
│        "risk_level": 3,                                  │
│        "entry": "$175",                                  │
│        "stop_loss": "$165",                              │
│        "target": "$195"                                  │
│      }                                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘

Key Points:
  ✓ Manages state across steps
  ✓ Conditional routing (if/else)
  ✓ Multiple nodes (functions)
  ✓ Decision-making
  ✓ Returns structured data
"""
print(langgraph_visual)

# ============================================================================
print_section("3. SIDE-BY-SIDE CODE COMPARISON")

comparison_code = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LANGCHAIN (Simple)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  from langchain_google_genai import ChatGoogleGenerativeAI                 │
│  from langchain.prompts import ChatPromptTemplate                          │
│                                                                             │
│  # Create template                                                          │
│  prompt = ChatPromptTemplate.from_template(                                │
│      "Analyze {symbol} at ${price}. Sentiment?"                            │
│  )                                                                           │
│                                                                             │
│  # Initialize LLM                                                           │
│  llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")               │
│                                                                             │
│  # Use it                                                                   │
│  messages = prompt.format_messages(symbol="AAPL", price=185)               │
│  result = llm.invoke(messages)                                              │
│  print(result.content)                                                      │
│                                                                             │
│  OUTPUT: "AAPL shows strong bullish momentum..."                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         LANGGRAPH (Advanced)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  from langgraph.graph import StateGraph, END                               │
│  from langchain_google_genai import ChatGoogleGenerativeAI                 │
│  from dataclasses import dataclass                                         │
│                                                                             │
│  @dataclass                                                                │
│  class StockState:                                                          │
│      symbol: str                                                            │
│      price: float                                                           │
│      sentiment: str = ""                                                    │
│      risk_level: int = 0                                                    │
│      recommendation: str = ""                                               │
│                                                                             │
│  # Define nodes                                                             │
│  def analyze_sentiment(state):                                              │
│      # Call LLM to determine sentiment                                      │
│      state.sentiment = "bullish"  # or "bearish"                           │
│      return state                                                           │
│                                                                             │
│  def assess_risk(state):                                                    │
│      # Calculate risk                                                       │
│      state.risk_level = 4                                                   │
│      return state                                                           │
│                                                                             │
│  def router(state):                                                         │
│      # Decide path based on risk                                            │
│      if state.risk_level < 5:                                              │
│          return "buy"                                                       │
│      else:                                                                  │
│          return "sell"                                                      │
│                                                                             │
│  # Build graph                                                              │
│  graph = StateGraph(StockState)                                             │
│  graph.add_node("sentiment", analyze_sentiment)                             │
│  graph.add_node("risk", assess_risk)                                        │
│  graph.add_edge("sentiment", "risk")                                        │
│  graph.add_conditional_edges("risk", router, {"buy": "buy_node"})          │
│  workflow = graph.compile()                                                 │
│                                                                             │
│  # Use it                                                                   │
│  state = StockState(symbol="AAPL", price=185)                              │
│  result = workflow.invoke(state)                                            │
│  print(result.recommendation)                                               │
│                                                                             │
│  OUTPUT: "BUY" (with risk assessment)                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""
print(comparison_code)

# ============================================================================
print_section("4. FEATURE MATRIX")

feature_matrix = """
Feature                  │  LangChain  │  LangGraph  │  Current Code
─────────────────────────┼─────────────┼─────────────┼─────────────────────
Prompt Management        │     ✓✓      │     ✓✓      │      ✗
Reusable Templates       │     ✓✓      │     ✓✓      │      ✗
Multiple Steps           │     ✓       │     ✓✓      │      ✗
Conditional Logic        │     ✗       │     ✓✓      │      ✗
Decision Making          │     ✗       │     ✓✓      │      ✗
State Management         │     ✓       │     ✓✓      │      ✗
Branching Workflows      │     ✗       │     ✓✓      │      ✗
Memory Across Steps      │     ✓       │     ✓✓      │      ✗
─────────────────────────┼─────────────┼─────────────┼─────────────────────
Difficulty              │     Easy    │   Medium    │     Easy
Lines of Code           │     20      │     100     │      15
Setup Time              │    5 min    │   30 min    │       0
Breaking Changes        │     No      │     No      │       -
New Endpoints Needed    │     No      │     Yes     │       -
"""
print(feature_matrix)

# ============================================================================
print_section("5. DECISION TREE: WHICH ONE TO USE?")

decision_tree = """
                            START HERE
                                 │
                                 ▼
                    What do you need to do?
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
           Simple Q&A      Multiple Steps    Make Decisions
        ("Analyze this")  ("Step 1→Step 2")  ("Buy or Sell?")
                │                │                │
                │                │                │
                ▼                ▼                ▼
          Use Current       Use LangChain    Use LangGraph
          (Keep As Is)      (Better Code)    (Smart Logic)
                │                │                │
                │                │                │
                └────────────────┼────────────────┘
                                 │
                                 ▼
                        YOUR SOLUTION!
"""
print(decision_tree)

# ============================================================================
print_section("6. YOUR STOCK AGENT ROADMAP")

roadmap = """
╔════════════════════════════════════════════════════════════════════════════╗
║                        3-WEEK IMPLEMENTATION PLAN                          ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  WEEK 1: LangChain (Better Code)                                          ║
║  ┌──────────────────────────────────────────────────────────────────┐    ║
║  │ Mon: Learn LangChain basics                                       │    ║
║  │ Tue: Create src/langchain_agent.py                               │    ║
║  │ Wed: Integrate into main.py                                      │    ║
║  │ Thu: Test and validate                                           │    ║
║  │ Fri: Deploy and monitor                                          │    ║
║  │                                                                  │    ║
║  │ Result: Same functionality, cleaner code ✓                       │    ║
║  └──────────────────────────────────────────────────────────────────┘    ║
║                                                                            ║
║  WEEK 2: LangGraph Phase 1 (Basic Decisions)                              ║
║  ┌──────────────────────────────────────────────────────────────────┐    ║
║  │ Mon: Learn LangGraph concepts                                    │    ║
║  │ Tue: Create nodes (analyze, assess)                              │    ║
║  │ Wed: Add routing logic                                           │    ║
║  │ Thu: Build workflow graph                                        │    ║
║  │ Fri: Test new endpoint: /recommend/{symbol}                      │    ║
║  │                                                                  │    ║
║  │ Result: BUY/SELL/HOLD recommendations ✓✓                         │    ║
║  └──────────────────────────────────────────────────────────────────┘    ║
║                                                                            ║
║  WEEK 3: LangGraph Phase 2 (Advanced Features)                            ║
║  ┌──────────────────────────────────────────────────────────────────┐    ║
║  │ Mon: Add risk assessment                                         │    ║
║  │ Tue: Add entry/stop-loss/target prices                           │    ║
║  │ Wed: Add confidence scores                                       │    ║
║  │ Thu: Add portfolio analysis                                      │    ║
║  │ Fri: Polish and deploy                                           │    ║
║  │                                                                  │    ║
║  │ Result: Professional-grade recommendations ✓✓✓                   │    ║
║  └──────────────────────────────────────────────────────────────────┘    ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
print(roadmap)

# ============================================================================
print_section("7. KEY FILES IN YOUR PROJECT")

files_guide = """
File Name                           │  Purpose                │  Read Time
────────────────────────────────────┼────────────────────────┼────────────
CHEATSHEET.md                       │  Quick reference       │   5 min
LANGCHAIN_GUIDE.md                  │  Detailed guide        │  30 min
practical_langchain_langgraph.py    │  Working examples      │  20 min
INTEGRATION_GUIDE.md                │  Integration steps     │  15 min
langchain_examples.py               │  Production code       │  30 min
LANGCHAIN_LANGGRAPH_SUMMARY.md      │  Complete overview     │  10 min

Recommendation: Start with CHEATSHEET.md, then run practical_langchain_langgraph.py
"""
print(files_guide)

# ============================================================================
print_section("8. INSTALLATION & QUICK START")

quickstart = """
Step 1: Install
  $ pip install langchain langchain-google-genai langgraph

Step 2: Verify .env has API keys
  $ cat .env
  # Should see: GEMINI_API_KEY=...

Step 3: Try an example
  $ python practical_langchain_langgraph.py
  # Choose option 1, 2, or 3

Step 4: Understand the output
  Read the generated analysis or recommendation

Step 5: Integrate into your code
  Follow INTEGRATION_GUIDE.md step-by-step

That's it! 🚀
"""
print(quickstart)

# ============================================================================
print_section("9. FINAL COMPARISON TABLE")

final_comparison = """
┌──────────────────────────────────────────────────────────────────────────┐
│                     COMPLETE FEATURE COMPARISON                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│ Aspect          │ Current Code │ LangChain    │ LangGraph               │
│ ─────────────────┼──────────────┼──────────────┼──────────────────────── │
│ Setup Time      │ 0 min        │ 5 min        │ 30 min                 │
│ Learning Curve  │ None         │ Easy         │ Medium                 │
│ Code Clarity    │ Good         │ Great        │ Excellent              │
│ Reusable Parts  │ No           │ Yes (temps)  │ Yes (nodes)            │
│ Error Handling  │ Basic        │ Better       │ Best                   │
│ Decision Logic  │ No           │ No           │ Yes                    │
│ Intelligence    │ Low          │ Medium       │ High                   │
│ Output Quality  │ Text         │ Text         │ Structured             │
│ Cost Impact     │ $1/mo        │ $1/mo        │ $1/mo                  │
│ Time to Deploy  │ Now          │ 1 week       │ 2 weeks                │
│ Production Ready│ Yes          │ Yes          │ Yes                    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

BOTTOM LINE:
  • Current code: Works, but basic
  • LangChain: Better organization, easier to maintain
  • LangGraph: Smart decisions, professional-grade
"""
print(final_comparison)

# ============================================================================
print_section("10. WHAT YOU'LL ACHIEVE")

achievements = """
After implementing LangChain & LangGraph:

BEFORE:
  ┌─────────────────────────────┐
  │ Stock Agent v1.0            │
  ├─────────────────────────────┤
  │ • Fetch prices              │
  │ • Generate text analysis    │
  │ • Store results             │
  └─────────────────────────────┘
  
  Status: ✓ Works, but basic

AFTER Phase 1 (LangChain):
  ┌─────────────────────────────┐
  │ Stock Agent v1.5            │
  ├─────────────────────────────┤
  │ • Clean prompt templates    │
  │ • Better code organization │
  │ • Reusable components       │
  │ • Easier maintenance        │
  └─────────────────────────────┘
  
  Status: ✓✓ Better code quality

AFTER Phase 2 (LangGraph):
  ┌──────────────────────────────────────┐
  │ Stock Agent v2.0 - Professional      │
  ├──────────────────────────────────────┤
  │ • Smart BUY/SELL/HOLD decisions      │
  │ • Risk assessment                    │
  │ • Entry/stop-loss/target prices      │
  │ • Confidence scores                  │
  │ • Multi-factor analysis              │
  │ • Conditional routing                │
  │ • Professional recommendations       │
  └──────────────────────────────────────┘
  
  Status: ✓✓✓ Production-ready, intelligent
"""
print(achievements)

# ============================================================================
print_title("YOU'RE READY TO LEVEL UP YOUR STOCK AGENT! 🚀")

final_message = """
Next steps:
  1. Read: CHEATSHEET.md (5 minutes)
  2. Try: python practical_langchain_langgraph.py
  3. Learn: LANGCHAIN_GUIDE.md
  4. Build: Follow INTEGRATION_GUIDE.md
  5. Deploy: Update main.py and test

Timeline:
  Week 1: LangChain (30 min to implement)
  Week 2: LangGraph (2-3 hours to implement)
  Result: Professional stock analysis agent!

Questions? Check:
  • CHEATSHEET.md - Quick answers
  • LANGCHAIN_GUIDE.md - Detailed explanations
  • practical_langchain_langgraph.py - Working code
  • INTEGRATION_GUIDE.md - Step-by-step setup

Good luck! 🎯
"""
print(final_message)

print("\n" + "="*80)
