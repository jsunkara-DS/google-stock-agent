"""
LangChain and LangGraph Examples for Stock Analysis Agent

This file demonstrates:
1. LangChain: Simple chains and prompts for stock analysis
2. LangGraph: Complex workflows with branching logic
"""

# ============================================================================
# PART 1: LANGCHAIN - Simple, Linear Workflows
# ============================================================================

"""
LangChain is like a conveyor belt:
  Input → Processing → Output
  
It helps you:
- Structure prompts with templates
- Chain multiple API calls together
- Handle memory and conversation history
- Connect LLM with tools/functions
"""

# Example 1: Basic LangChain Setup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from typing import Dict, Optional


class StockAnalysisChain:
    """LangChain example: Simple linear stock analysis."""
    
    def __init__(self, gemini_api_key: str):
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=gemini_api_key,
            temperature=0.7
        )
        
        # Create a prompt template (reusable template with variables)
        self.analysis_prompt = ChatPromptTemplate.from_template(
            """You are a stock analyst. Analyze this stock data:
            
Symbol: {symbol}
Current Price: ${price:.2f}
Change: {change:.2f} ({change_percent}%)
Previous Close: ${previous_close:.2f}
Volume: {volume}

Provide:
1. Market sentiment (bullish/bearish/neutral)
2. Key drivers of the move
3. Trading signal (buy/sell/hold)
4. Risk level (1-10)

Be concise and actionable."""
        )
    
    def analyze(self, stock_data: Dict) -> str:
        """Chain: Format prompt → Call LLM → Return analysis."""
        
        # Step 1: Format the prompt with data
        messages = self.analysis_prompt.format_messages(**stock_data)
        
        # Step 2: Call LLM
        response = self.llm.invoke(messages)
        
        # Step 3: Return result
        return response.content


# Example 2: Chained Operations (Multiple Steps)
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class ChainedStockAnalysis:
    """LangChain: Chain multiple operations together."""
    
    def __init__(self, gemini_api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=gemini_api_key
        )
    
    def analyze_with_multiple_steps(self, stock_data: Dict) -> Dict:
        """
        LangChain workflow:
        1. Generate initial analysis
        2. Extract investment thesis
        3. Generate trading strategy
        """
        
        # Step 1: Initial Analysis
        analysis_prompt = PromptTemplate(
            input_variables=["symbol", "price", "change_percent"],
            template="""Analyze {symbol} at ${price} ({change_percent}%).
            Provide a brief market sentiment."""
        )
        
        chain1 = LLMChain(llm=self.llm, prompt=analysis_prompt)
        sentiment = chain1.run(
            symbol=stock_data["symbol"],
            price=stock_data["price"],
            change_percent=stock_data["change_percent"]
        )
        
        # Step 2: Extract Investment Thesis
        thesis_prompt = PromptTemplate(
            input_variables=["sentiment"],
            template="""Based on this sentiment: {sentiment}
            
What is the investment thesis? List key reasons."""
        )
        
        chain2 = LLMChain(llm=self.llm, prompt=thesis_prompt)
        thesis = chain2.run(sentiment=sentiment)
        
        # Step 3: Generate Strategy
        strategy_prompt = PromptTemplate(
            input_variables=["thesis"],
            template="""Given this thesis: {thesis}
            
Recommend a trading strategy (entry point, stop loss, target)."""
        )
        
        chain3 = LLMChain(llm=self.llm, prompt=strategy_prompt)
        strategy = chain3.run(thesis=thesis)
        
        return {
            "symbol": stock_data["symbol"],
            "sentiment": sentiment,
            "thesis": thesis,
            "strategy": strategy
        }


# ============================================================================
# PART 2: LANGGRAPH - Complex Workflows with Decision Logic
# ============================================================================

"""
LangGraph is like a flowchart:
  Start → Decision → Path A or B → Another Decision → End
  
It helps you:
- Create conditional workflows
- Handle multiple paths (if/else logic)
- Maintain state across steps
- Create agent-like behaviors
"""

from langgraph.graph import StateGraph, END
from typing import Literal
from enum import Enum


# Step 1: Define the State (what data flows through the graph)
class StockAnalysisState:
    """State object passed through the graph."""
    
    def __init__(self):
        self.symbol: str = ""
        self.price: float = 0.0
        self.change_percent: float = 0.0
        self.sentiment: str = ""  # bullish, bearish, neutral
        self.risk_level: int = 0  # 1-10
        self.action: str = ""  # buy, sell, hold
        self.reasoning: str = ""


# Step 2: Define Nodes (functions that do work)
def analyze_sentiment(state: StockAnalysisState, llm) -> StockAnalysisState:
    """Node 1: Determine if stock is bullish or bearish."""
    prompt = f"""Stock: {state.symbol}
Price change: {state.change_percent}%

Is this bullish, bearish, or neutral?
Return only one word: bullish | bearish | neutral"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    state.sentiment = response.content.strip().lower()
    return state


def assess_risk(state: StockAnalysisState, llm) -> StockAnalysisState:
    """Node 2: Assess risk level."""
    prompt = f"""Stock: {state.symbol}
Sentiment: {state.sentiment}
Price change: {state.change_percent}%

Rate the risk level 1-10 (1=safe, 10=risky).
Return only the number."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    state.risk_level = int(response.content.strip())
    return state


def decide_action(state: StockAnalysisState) -> Literal["high_risk", "low_risk", "hold"]:
    """Node 3: Routing node - decide which path to take."""
    
    # Decision logic
    if state.sentiment == "bearish" and state.risk_level > 7:
        return "high_risk"
    elif state.sentiment == "bullish" and state.risk_level < 4:
        return "low_risk"
    else:
        return "hold"


def handle_high_risk(state: StockAnalysisState, llm) -> StockAnalysisState:
    """Node 4a: High risk path - generate caution message."""
    prompt = f"""This {state.symbol} is {state.sentiment} with high risk ({state.risk_level}/10).
Advise against this trade with reasoning."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    state.action = "SELL/AVOID"
    state.reasoning = response.content
    return state


def handle_low_risk(state: StockAnalysisState, llm) -> StockAnalysisState:
    """Node 4b: Low risk path - generate buy recommendation."""
    prompt = f"""This {state.symbol} is {state.sentiment} with low risk ({state.risk_level}/10).
Recommend entry strategy with target and stop loss."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    state.action = "BUY"
    state.reasoning = response.content
    return state


def hold_decision(state: StockAnalysisState, llm) -> StockAnalysisState:
    """Node 4c: Hold path - wait and see."""
    state.action = "HOLD"
    state.reasoning = f"Neutral sentiment ({state.sentiment}) with medium risk ({state.risk_level}/10). Waiting for clarity."
    return state


# Step 3: Build the Graph
def build_stock_analysis_graph(gemini_api_key: str):
    """Create a LangGraph workflow."""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=gemini_api_key
    )
    
    # Create the graph
    graph = StateGraph(StockAnalysisState)
    
    # Add nodes
    graph.add_node("analyze_sentiment", lambda s: analyze_sentiment(s, llm))
    graph.add_node("assess_risk", lambda s: assess_risk(s, llm))
    graph.add_node("high_risk", lambda s: handle_high_risk(s, llm))
    graph.add_node("low_risk", lambda s: handle_low_risk(s, llm))
    graph.add_node("hold", lambda s: hold_decision(s, llm))
    
    # Define edges (connections between nodes)
    graph.add_edge("analyze_sentiment", "assess_risk")
    
    # Conditional edge: decide_action decides where to go next
    graph.add_conditional_edges(
        "assess_risk",
        decide_action,
        {
            "high_risk": "high_risk",
            "low_risk": "low_risk",
            "hold": "hold"
        }
    )
    
    # All paths lead to END
    graph.add_edge("high_risk", END)
    graph.add_edge("low_risk", END)
    graph.add_edge("hold", END)
    
    # Set entry point
    graph.set_entry_point("analyze_sentiment")
    
    # Compile into runnable
    return graph.compile()


# ============================================================================
# PART 3: PRACTICAL USAGE EXAMPLES
# ============================================================================

def example_langchain_basic():
    """Example 1: Use LangChain for simple stock analysis."""
    import os
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    chain = StockAnalysisChain(api_key)
    
    stock_data = {
        "symbol": "AAPL",
        "price": 185.50,
        "change": 2.15,
        "change_percent": "1.17%",
        "previous_close": 183.35,
        "volume": "45231000"
    }
    
    analysis = chain.analyze(stock_data)
    print("LangChain Basic Analysis:")
    print(analysis)
    print()


def example_langchain_chained():
    """Example 2: Use LangChain for multi-step analysis."""
    import os
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    chain = ChainedStockAnalysis(api_key)
    
    stock_data = {
        "symbol": "MSFT",
        "price": 420.75,
        "change": -3.25,
        "change_percent": "-0.77%"
    }
    
    result = chain.analyze_with_multiple_steps(stock_data)
    print("LangChain Chained Analysis:")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Thesis: {result['thesis']}")
    print(f"Strategy: {result['strategy']}")
    print()


def example_langgraph_workflow():
    """Example 3: Use LangGraph for complex decision workflow."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Build the graph
    graph = build_stock_analysis_graph(api_key)
    
    # Create initial state
    state = StockAnalysisState()
    state.symbol = "NVDA"
    state.price = 875.30
    state.change_percent = 5.2
    
    # Run the workflow
    print("LangGraph Workflow:")
    print(f"Analyzing {state.symbol}...")
    print()
    
    # Execute the graph
    final_state = graph.invoke(state)
    
    print(f"Sentiment: {final_state.sentiment}")
    print(f"Risk Level: {final_state.risk_level}/10")
    print(f"Action: {final_state.action}")
    print(f"Reasoning: {final_state.reasoning}")
    print()


# ============================================================================
# COMPARISON: LangChain vs LangGraph
# ============================================================================

COMPARISON = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    LANGCHAIN vs LANGGRAPH                                  ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  LANGCHAIN                          │  LANGGRAPH                           ║
║  ──────────────────────────────────┼──────────────────────────────────  ║
║  ✓ Simple, linear workflows         │  ✓ Complex, conditional workflows    ║
║  ✓ Step-by-step processing          │  ✓ Decision trees and branching     ║
║  ✓ Easy to chain prompts            │  ✓ State management                 ║
║  ✓ Good for: Q&A, summaries         │  ✓ Good for: Agents, workflows      ║
║                                     │                                      ║
║  Example:                           │  Example:                            ║
║  Input → LLM → Output               │  Input → Decision → Path A/B → Output║
║                                     │                                      ║
║  USE CASE:                          │  USE CASE:                           ║
║  "Summarize this article"           │  "Should I buy this stock? It       ║
║  "Translate to Spanish"             │   depends on risk, sentiment, price" ║
║  "Generate 5 ideas"                 │                                      ║
║                                     │  Multiple decisions needed:          ║
║                                     │  - Analyze sentiment                 ║
║                                     │  - Check risk level                  ║
║                                     │  - Make final decision               ║
║                                     │                                      ║
║                                    ║  Can loop back or retry              ║
║                                     │  based on intermediate results       ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

STOCK AGENT EXAMPLES:

1. LangChain Example (Simple):
   "Analyze AAPL" 
   → Fetch data 
   → Create prompt 
   → Call Gemini 
   → Return analysis
   
   Code: One-liner chain

2. LangGraph Example (Complex):
   "Decide whether to buy AAPL"
   → Check sentiment
   → If negative: Check if oversold? 
     → If oversold: BUY signal
     → If not: SELL signal
   → If positive: Check risk level?
     → If low risk: BUY signal
     → If high risk: HOLD signal
   → Return final decision with reasoning
   
   Code: State graph with multiple paths
"""

print(COMPARISON)


if __name__ == "__main__":
    print("=" * 80)
    print("LANGCHAIN & LANGGRAPH EXAMPLES FOR STOCK AGENT")
    print("=" * 80)
    print()
    
    # Run examples (comment out if API keys not set)
    # example_langchain_basic()
    # example_langchain_chained()
    # example_langgraph_workflow()
    
    print("See functions above for usage:")
    print("- example_langchain_basic()")
    print("- example_langchain_chained()")
    print("- example_langgraph_workflow()")
    print()
    print("To use in your stock agent:")
    print("1. Install: pip install langchain langgraph langchain-google-genai")
    print("2. Replace gemini_agent.py with LangChain/LangGraph version")
    print("3. Update main.py to use new agent")
