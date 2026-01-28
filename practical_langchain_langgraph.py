"""
Practical LangChain & LangGraph Implementation
Ready to use with your stock agent
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# IMPORTANT: Install required packages first
# pip install langchain langchain-google-genai langgraph
# ============================================================================


# ============================================================================
# PART 1: PRACTICAL LANGCHAIN EXAMPLE (Easy to integrate)
# ============================================================================

def example_langchain():
    """
    This replaces your current gemini_agent.py with LangChain version
    Simple, clean, easy to understand
    """
    
    print("\n" + "="*80)
    print("PART 1: LANGCHAIN - Simple Linear Workflow")
    print("="*80)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.prompts import ChatPromptTemplate
        from langchain.schema import HumanMessage
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not set. See .env")
            return
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=api_key,
            temperature=0.7
        )
        
        # Create reusable prompt template
        analysis_template = ChatPromptTemplate.from_template(
            """You are a stock analyst. Analyze this stock:

Symbol: {symbol}
Price: ${price:.2f}
Change: {change:.2f} ({change_percent}%)
Volume: {volume}

Provide:
1. Sentiment (bullish/bearish/neutral)
2. Key reason for the move
3. Trading signal (buy/sell/hold)

Be concise."""
        )
        
        # Sample stock data
        stock_data = {
            "symbol": "AAPL",
            "price": 185.50,
            "change": 2.15,
            "change_percent": "1.17%",
            "volume": "45231000"
        }
        
        # Step 1: Format the prompt
        messages = analysis_template.format_messages(**stock_data)
        
        # Step 2: Call LLM
        print(f"\n📊 Analyzing {stock_data['symbol']}...")
        response = llm.invoke(messages)
        
        # Step 3: Display result
        print(f"\n✅ Analysis:")
        print(response.content)
        
        return response.content
        
    except ImportError:
        print("❌ LangChain not installed. Run: pip install langchain langchain-google-genai")
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# PART 2: PRACTICAL LANGGRAPH EXAMPLE (Smart decision-making)
# ============================================================================

def example_langgraph():
    """
    This shows how to build an intelligent decision workflow
    Better than simple prompting - has conditional logic
    """
    
    print("\n" + "="*80)
    print("PART 2: LANGGRAPH - Smart Decision Workflow")
    print("="*80)
    
    try:
        from langgraph.graph import StateGraph, END
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.schema import HumanMessage
        from typing import Literal
        from dataclasses import dataclass, field
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not set. See .env")
            return
        
        # Initialize LLM once
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=api_key,
            temperature=0.5
        )
        
        # Step 1: Define State (data that flows through the graph)
        @dataclass
        class StockDecisionState:
            symbol: str
            price: float
            change_percent: float
            volume: str
            # Intermediate results
            sentiment: str = ""  # "bullish", "bearish", "neutral"
            risk_score: int = 0  # 1-10
            # Final result
            recommendation: str = ""  # "BUY", "SELL", "HOLD"
            reasoning: str = ""
        
        # Step 2: Define Node Functions
        
        def node_analyze_sentiment(state: StockDecisionState) -> StockDecisionState:
            """Analyze if the stock is bullish, bearish, or neutral."""
            
            prompt = HumanMessage(
                content=f"""Stock: {state.symbol}
Change: {state.change_percent}%
Volume: {state.volume}

Determine sentiment in ONE WORD: bullish, bearish, or neutral"""
            )
            
            response = llm.invoke([prompt])
            state.sentiment = response.content.strip().lower()
            
            print(f"  1️⃣ Sentiment Analysis: {state.sentiment}")
            return state
        
        
        def node_assess_risk(state: StockDecisionState) -> StockDecisionState:
            """Calculate risk score based on volatility and movement."""
            
            prompt = HumanMessage(
                content=f"""Stock: {state.symbol}
Sentiment: {state.sentiment}
Change: {state.change_percent}%

Rate risk 1-10 (1=safe, 10=risky). Return ONLY number."""
            )
            
            response = llm.invoke([prompt])
            try:
                state.risk_score = int(response.content.strip())
            except:
                state.risk_score = 5  # Default to medium risk
            
            print(f"  2️⃣ Risk Assessment: {state.risk_score}/10")
            return state
        
        
        def router_decision(state: StockDecisionState) -> Literal["buy_path", "sell_path", "hold_path"]:
            """Route to different paths based on sentiment + risk."""
            
            print(f"  🔀 Routing decision...")
            
            # Simple decision logic
            if state.sentiment == "bullish" and state.risk_score < 5:
                return "buy_path"
            elif state.sentiment == "bearish" and state.risk_score > 6:
                return "sell_path"
            else:
                return "hold_path"
        
        
        def node_buy_path(state: StockDecisionState) -> StockDecisionState:
            """Generate BUY recommendation."""
            
            prompt = HumanMessage(
                content=f"""Stock {state.symbol}: {state.sentiment}, Risk: {state.risk_score}/10

Generate a BUY recommendation with:
- Entry price (current or wait)
- Stop loss (10% below entry)
- Target (20% above entry)
- Timeframe"""
            )
            
            response = llm.invoke([prompt])
            state.recommendation = "🟢 BUY"
            state.reasoning = response.content
            
            print(f"  3️⃣ Decision: BUY")
            return state
        
        
        def node_sell_path(state: StockDecisionState) -> StockDecisionState:
            """Generate SELL recommendation."""
            
            prompt = HumanMessage(
                content=f"""Stock {state.symbol}: {state.sentiment}, Risk: {state.risk_score}/10

Generate a SELL/AVOID recommendation with:
- Why to avoid
- Support levels if oversold
- Risk assessment"""
            )
            
            response = llm.invoke([prompt])
            state.recommendation = "🔴 SELL/AVOID"
            state.reasoning = response.content
            
            print(f"  3️⃣ Decision: SELL/AVOID")
            return state
        
        
        def node_hold_path(state: StockDecisionState) -> StockDecisionState:
            """Generate HOLD recommendation."""
            
            state.recommendation = "🟡 HOLD"
            state.reasoning = f"Mixed signals detected. {state.sentiment} sentiment with {state.risk_score}/10 risk. Wait for clarity."
            
            print(f"  3️⃣ Decision: HOLD")
            return state
        
        
        # Step 3: Build the Graph
        print("\n🏗️  Building decision graph...")
        
        graph = StateGraph(StockDecisionState)
        
        # Add all nodes
        graph.add_node("analyze_sentiment", node_analyze_sentiment)
        graph.add_node("assess_risk", node_assess_risk)
        graph.add_node("buy", node_buy_path)
        graph.add_node("sell", node_sell_path)
        graph.add_node("hold", node_hold_path)
        
        # Connect nodes in sequence
        graph.add_edge("analyze_sentiment", "assess_risk")
        
        # Conditional routing based on router_decision output
        graph.add_conditional_edges(
            "assess_risk",
            router_decision,
            {
                "buy_path": "buy",
                "sell_path": "sell",
                "hold_path": "hold"
            }
        )
        
        # All paths end
        graph.add_edge("buy", END)
        graph.add_edge("sell", END)
        graph.add_edge("hold", END)
        
        # Set entry point
        graph.set_entry_point("analyze_sentiment")
        
        # Compile
        workflow = graph.compile()
        
        print("✅ Graph ready!\n")
        
        # Step 4: Create initial state
        print("📈 Processing stock decision...\n")
        
        state = StockDecisionState(
            symbol="NVDA",
            price=875.30,
            change_percent=5.2,
            volume="52341000"
        )
        
        # Step 5: Execute workflow
        result = workflow.invoke(state)
        
        # Step 6: Display final result
        print("\n" + "="*60)
        print(f"📋 FINAL RECOMMENDATION: {result.recommendation}")
        print("="*60)
        print(f"\nAnalysis:")
        print(result.reasoning)
        print("="*60)
        
        return result
        
    except ImportError:
        print("❌ LangGraph not installed. Run: pip install langgraph")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# PART 3: ADVANCED - LangGraph with Memory (State Persistence)
# ============================================================================

def example_langgraph_with_memory():
    """
    Shows how to maintain conversation history across multiple stocks
    Useful for portfolio analysis
    """
    
    print("\n" + "="*80)
    print("PART 3: LANGGRAPH - With Memory (Portfolio Analysis)")
    print("="*80)
    
    try:
        from langgraph.graph import StateGraph, END
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.schema import HumanMessage
        from dataclasses import dataclass, field
        from typing import List
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not set")
            return
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
        
        @dataclass
        class PortfolioState:
            stocks: List[Dict] = field(default_factory=list)
            analysis_history: List[str] = field(default_factory=list)  # Memory!
            portfolio_summary: str = ""
            recommendation: str = ""
        
        
        def analyze_each_stock(state: PortfolioState) -> PortfolioState:
            """Analyze each stock and store in memory."""
            
            for stock in state.stocks[:3]:  # Analyze first 3 stocks
                result = f"{stock['symbol']}: ${stock['price']} ({stock['change_percent']}%)"
                state.analysis_history.append(result)
            
            print(f"  📊 Analyzed {len(state.analysis_history)} stocks")
            return state
        
        
        def generate_portfolio_summary(state: PortfolioState) -> PortfolioState:
            """Use memory to generate portfolio summary."""
            
            history_text = "\n".join(state.analysis_history)
            
            prompt = HumanMessage(
                content=f"""Analyzed these stocks:
{history_text}

Provide portfolio recommendation (Aggressive/Balanced/Conservative)"""
            )
            
            response = llm.invoke([prompt])
            state.portfolio_summary = response.content
            
            print(f"  📈 Generated portfolio summary")
            return state
        
        
        # Build graph
        graph = StateGraph(PortfolioState)
        graph.add_node("analyze_stocks", analyze_each_stock)
        graph.add_node("summarize", generate_portfolio_summary)
        graph.add_edge("analyze_stocks", "summarize")
        graph.add_edge("summarize", END)
        graph.set_entry_point("analyze_stocks")
        
        workflow = graph.compile()
        
        # Create state with multiple stocks
        state = PortfolioState(
            stocks=[
                {"symbol": "AAPL", "price": 185.50, "change_percent": "1.2%"},
                {"symbol": "MSFT", "price": 420.75, "change_percent": "-0.8%"},
                {"symbol": "NVDA", "price": 875.30, "change_percent": "5.2%"},
            ]
        )
        
        # Execute
        result = workflow.invoke(state)
        
        print(f"\n✅ Portfolio Analysis:")
        print(f"Stocks analyzed: {len(result.analysis_history)}")
        print(f"\nSummary:\n{result.portfolio_summary}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# COMPARISON: Call All Examples
# ============================================================================

SIDE_BY_SIDE = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                  QUICK COMPARISON OF EXAMPLES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Example 1: LangChain (Simple)                                             │
│  ─────────────────────────                                                 │
│  • Just format and send prompt                                             │
│  • One call to LLM                                                         │
│  • Output: Text analysis                                                   │
│  • Use Case: Quick analysis of single stock                                │
│                                                                              │
│  Example 2: LangGraph (Smart)                                              │
│  ──────────────────────────                                                │
│  • Multiple analysis steps                                                 │
│  • Conditional routing (if/else)                                           │
│  • Output: Recommendation + reasoning                                      │
│  • Use Case: Decision-making (BUY/SELL/HOLD)                               │
│                                                                              │
│  Example 3: LangGraph + Memory (Advanced)                                  │
│  ──────────────────────────────────────                                    │
│  • Analyze multiple stocks                                                 │
│  • Maintain history across steps                                           │
│  • Output: Portfolio recommendation                                        │
│  • Use Case: Portfolio analysis                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

RECOMMENDATION FOR YOUR STOCK AGENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1 (Now):
  → Use Example 1 (LangChain Simple)
  → Replace current gemini_agent.py
  → Better prompt management

Phase 2 (Later):
  → Use Example 2 (LangGraph Smart)
  → Add decision logic
  → Provide BUY/SELL/HOLD recommendations

Phase 3 (Advanced):
  → Use Example 3 (LangGraph + Memory)
  → Analyze multiple stocks together
  → Portfolio-level insights
"""

print(SIDE_BY_SIDE)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("LANGCHAIN & LANGGRAPH PRACTICAL EXAMPLES")
    print("="*80)
    
    # Try to run examples (requires API key)
    print("\nNote: These examples require GEMINI_API_KEY in .env")
    print("\nChoose which to run:")
    print("  1. LangChain Simple (easiest)")
    print("  2. LangGraph Smart (recommended)")
    print("  3. LangGraph + Memory (advanced)")
    print("  0. See comparison")
    
    choice = input("\nEnter choice (0-3) or leave blank for all: ").strip()
    
    if choice == "1" or choice == "":
        example_langchain()
    
    if choice == "2" or choice == "":
        example_langgraph()
    
    if choice == "3" or choice == "":
        example_langgraph_with_memory()
    
    if choice == "0":
        print(SIDE_BY_SIDE)
