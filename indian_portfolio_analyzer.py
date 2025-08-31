import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from datetime import datetime

load_dotenv()


class IndianStockAction(BaseModel):
    ticker: str = Field(description="Indian stock ticker (e.g., RELIANCE.NS, TCS.NS)")
    company_name: str = Field(description="Indian company name")
    action: str = Field(description="BUY, SELL, HOLD, or ADD (buy more)")
    reason: str = Field(description="Detailed reason considering Indian market conditions")
    priority: str = Field(description="HIGH, MEDIUM, or LOW priority")
    target_allocation: str = Field(description="Suggested position size or percentage")
    sector_outlook: str = Field(description="Outlook for this sector in Indian market")
    best_sector_to_add: str = Field(default="Unknown", description="Single best Indian market sector to add now")
    confidence_score: int = Field(default=70, description="Confidence score (0-100)")


def read_portfolio_excel(file_path="Stock.xlsx"):
    """Read Indian stock portfolio from Excel file"""
    try:
        if not Path(file_path).exists():
            print(f"❌ {file_path} not found. Please create it with columns: Company Name, Total Quantity, Avg Trading Price")
            return None

        df = pd.read_excel(file_path)
        required_cols = ['Company Name', 'Total Quantity', 'Avg Trading Price']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            print(f"❌ Missing columns in Excel: {missing_cols}")
            return None

        df_renamed = df.rename(columns={
            'Company Name': 'Company',
            'Total Quantity': 'Shares',
            'Avg Trading Price': 'Cost_Per_Share',
            'LTP': 'Current_Price'
        })

        df_renamed['Ticker'] = df_renamed['Company'].str.upper().str.replace(' ', '')
        
        if 'Current_Price' not in df_renamed.columns:
            df_renamed['Current_Price'] = df_renamed['Cost_Per_Share']

        if 'Sector' not in df_renamed.columns:
            df_renamed['Sector'] = 'Unknown'

        return df_renamed

    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return None


def setup_models():
    """Setup and return prompt→model→parser chains and format instructions"""
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Please set the OPENAI_API_KEY environment variable.")
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit("Please set the GOOGLE_API_KEY environment variable.")

    prompt = ChatPromptTemplate.from_template(
        "Analyze this Indian stock portfolio and suggest ONE specific action (BUY new Indian stock, SELL existing, HOLD, or ADD more to existing).\n\n"
        "Current Indian Portfolio:\n{portfolio_data}\n\n"
        "Market Context: {market_context}\n\n"
        "Also identify the ONE best sector to add now given risks and sector rotation.\n\n"
        "Recommend the SINGLE MOST IMPORTANT action for this Indian portfolio right now.\n\n"
        "{format_instructions}"
    )
    
    openai_llm = ChatOpenAI(model="gpt-4", temperature=0.4)
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

    parser = PydanticOutputParser(pydantic_object=IndianStockAction)
    format_instructions = parser.get_format_instructions()

    openai_chain = prompt | openai_llm | parser
    gemini_chain = prompt | gemini_llm | parser
    both = RunnableParallel(openai=openai_chain, gemini=gemini_chain)

    return both, format_instructions


def format_indian_portfolio_data(df):
    """Format Indian portfolio data for AI analysis"""
    portfolio_summary = []
    total_value = 0
    sector_allocation = {}

    for _, row in df.iterrows():
        shares = row['Shares']
        cost = row['Cost_Per_Share']
        current = row.get('Current_Price', cost)
        sector = row.get('Sector', 'Unknown')

        total_cost = shares * cost
        current_value = shares * current
        gain_loss = current_value - total_cost
        gain_loss_pct = (gain_loss / total_cost) * 100 if total_cost > 0 else 0

        total_value += current_value

        if sector in sector_allocation:
            sector_allocation[sector] += current_value
        else:
            sector_allocation[sector] = current_value

        portfolio_summary.append(
            f"- {row['Ticker']} ({row['Company']}): {shares} shares, "
            f"Cost: ₹{cost:.2f}, Current: ₹{current:.2f}, "
            f"P&L: ₹{gain_loss:.2f} ({gain_loss_pct:.1f}%), Sector: {sector}"
        )

    sector_breakdown = []
    for sector, value in sector_allocation.items():
        percentage = (value / total_value) * 100 if total_value > 0 else 0
        sector_breakdown.append(f"  {sector}: ₹{value:.2f} ({percentage:.1f}%)")

    result = "\n".join(portfolio_summary)
    result += f"\n\nTotal Portfolio Value: ₹{total_value:.2f}"
    result += f"\n\nSector Allocation:\n" + "\n".join(sector_breakdown)

    return result


def get_all_indian_market_contexts():
    """Get all Indian market contexts for comprehensive analysis"""
    contexts = {
        "Monsoon Impact": "Monsoon season - impact on agriculture and FMCG sectors, rural demand patterns",
        "Budget/Policy Period": "Budget announcement period - policy sensitive stocks volatile, regulatory changes expected",
        "FII Selling Pressure": "FII selling pressure due to global factors, DII support, rupee volatility",
        "General Market": "Normal Indian market conditions with moderate volatility, mixed sector performance",
        "Stock expert":"check anuj singhal analysis on cnbc for last day and take into context",
        "duration":"short term for next week"
    }
    return contexts


def analyze_portfolio(portfolio_df, market_context, both, format_instructions):
    """Analyze portfolio and get AI recommendations"""
    portfolio_summary = format_indian_portfolio_data(portfolio_df)

    print(f"\n🤖 Analyzing Indian portfolio with context: {market_context}")
    print("⏳ Generating recommendations...")

    resp = both.invoke({
        "portfolio_data": portfolio_summary,
        "market_context": market_context,
        "format_instructions": format_instructions
    })

    return resp, portfolio_summary


def display_analysis_results(openai_action, gemini_action):
    """Display structured analysis results"""
    print("\n" + "=" * 70)
    print("🤖 OPENAI INDIAN PORTFOLIO ANALYSIS")
    print("=" * 70)
    action_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡", "ADD": "🔵"}.get(openai_action.action, "⚪")
    priority_emoji = {"HIGH": "🔥", "MEDIUM": "⚠️", "LOW": "ℹ️"}.get(openai_action.priority, "")

    print(f"{action_emoji} Action: {openai_action.action}")
    print(f"🏢 Stock: {openai_action.company_name} ({openai_action.ticker})")
    print(f"{priority_emoji} Priority: {openai_action.priority}")
    print(f"🎯 Target: {openai_action.target_allocation}")
    print(f"🏭 Sector Outlook: {openai_action.sector_outlook}")
    print(f"📌 Best Sector To Add: {openai_action.best_sector_to_add}")
    print(f"💡 Reason: {openai_action.reason}")
    print(f"🎯 Confidence: {openai_action.confidence_score}%")

    print("\n" + "=" * 70)
    print("🤖 GEMINI INDIAN PORTFOLIO ANALYSIS")
    print("=" * 70)
    action_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡", "ADD": "🔵"}.get(gemini_action.action, "⚪")
    priority_emoji = {"HIGH": "🔥", "MEDIUM": "⚠️", "LOW": "ℹ️"}.get(gemini_action.priority, "")

    print(f"{action_emoji} Action: {gemini_action.action}")
    print(f"🏢 Stock: {gemini_action.company_name} ({gemini_action.ticker})")
    print(f"{priority_emoji} Priority: {gemini_action.priority}")
    print(f"🎯 Target: {gemini_action.target_allocation}")
    print(f"🏭 Sector Outlook: {gemini_action.sector_outlook}")
    print(f"📌 Best Sector To Add: {gemini_action.best_sector_to_add}")
    print(f"💡 Reason: {gemini_action.reason}")
    print(f"🎯 Confidence: {gemini_action.confidence_score}%")


def display_summary(openai_action, gemini_action, portfolio_df):
    """Display analysis summary and consensus"""
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    action_consensus = openai_action.action == gemini_action.action
    ticker_consensus = openai_action.ticker == gemini_action.ticker
    confidence_avg = (openai_action.confidence_score + gemini_action.confidence_score) / 2
    
    if action_consensus and ticker_consensus:
        print(f"🎯 STRONG CONSENSUS: Both models agree on {openai_action.action} {openai_action.ticker}")
        print(f"📈 Average Confidence: {confidence_avg:.0f}%")
    elif action_consensus:
        print(f"🤝 ACTION CONSENSUS: Both models recommend {openai_action.action}")
        print(f"   OpenAI: {openai_action.ticker} | Gemini: {gemini_action.ticker}")
        print(f"📈 Average Confidence: {confidence_avg:.0f}%")
    else:
        print(f"🤔 DIFFERENT VIEWS:")
        print(f"   OpenAI: {openai_action.action} {openai_action.ticker} (Confidence: {openai_action.confidence_score}%)")
        print(f"   Gemini: {gemini_action.action} {gemini_action.ticker} (Confidence: {gemini_action.confidence_score}%)")
        print(f"⚠️ Consider manual review before acting")

    total_value = (portfolio_df['Shares'] * portfolio_df['Current_Price']).sum()
    print(f"\n💰 Current Portfolio Value: ₹{total_value:.2f}")
    print("🇮🇳 Analysis complete for Indian market conditions!")
    print(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main execution function"""
    print("🇮🇳 Indian Stock Portfolio Analyzer")
    print("=" * 50)

    print("📊 Reading Indian portfolio from Stock.xlsx...")
    portfolio_df = read_portfolio_excel()

    if portfolio_df is None:
        print("❌ Cannot proceed without portfolio data")
        print("\n📋 Create 'Stocks.xlsx' with columns:")
        print("   - Company Name")
        print("   - Total Quantity") 
        print("   - Avg Trading Price")
        print("   - Sector (optional)")
        return

    both, format_instructions = setup_models()

    print("\n📋 Current Indian Portfolio:")
    portfolio_summary = format_indian_portfolio_data(portfolio_df)
    print(portfolio_summary)

    print("\n🤖 Choose AI Model:")
    print("1. OpenAI GPT-4")
    print("2. Google Gemini")
    print("3. Both models")
    
    try:
        model_choice = input("Select model (1-3) or press Enter for both: ").strip()
    except EOFError:
        model_choice = "3"

    all_contexts = get_all_indian_market_contexts()
    combined_context = "Consider all market scenarios: " + "; ".join(all_contexts.values())
    
    resp, _ = analyze_portfolio(portfolio_df, combined_context, both, format_instructions)
    
    if model_choice == "1":
        print("\n🤖 OpenAI GPT-4 Recommendation:")
        print(f"📈 Action: {resp['openai'].action} - {resp['openai'].ticker}")
        print(f"💡 Reason: {resp['openai'].reason}")
        print(f"⚡ Priority: {resp['openai'].priority}")
        print(f"🎯 Target Allocation: {resp['openai'].target_allocation}")
        print(f"📊 Sector Outlook: {resp['openai'].sector_outlook}")
        print(f"🎯 Confidence: {resp['openai'].confidence_score}%")
    elif model_choice == "2":
        print("\n🧠 Google Gemini Recommendation:")
        print(f"📈 Action: {resp['gemini'].action} - {resp['gemini'].ticker}")
        print(f"💡 Reason: {resp['gemini'].reason}")
        print(f"⚡ Priority: {resp['gemini'].priority}")
        print(f"🎯 Target Allocation: {resp['gemini'].target_allocation}")
        print(f"📊 Sector Outlook: {resp['gemini'].sector_outlook}")
        print(f"🎯 Confidence: {resp['gemini'].confidence_score}%")
    else:
        display_analysis_results(resp["openai"], resp["gemini"])
        display_summary(resp["openai"], resp["gemini"], portfolio_df)


if __name__ == "__main__":
    main()
