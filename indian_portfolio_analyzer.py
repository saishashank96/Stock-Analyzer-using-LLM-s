import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
from app.services.portfolio_reader import read_portfolio_excel, format_indian_portfolio_data, get_portfolio_summary, validate_portfolio_data
from app.utils.display_utils import (
    display_analysis_results, display_summary, display_single_recommendation,
    display_portfolio_header, display_model_selection, display_analysis_progress,
    display_portfolio_data, display_error_message, display_success_message
)
from app.models.data_models import IndianStockAction

load_dotenv()


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

    display_analysis_progress(market_context)

    resp = both.invoke({
        "portfolio_data": portfolio_summary,
        "market_context": market_context,
        "format_instructions": format_instructions
    })

    return resp, portfolio_summary


def main():
    """Main execution function"""
    display_portfolio_header()

    print("📊 Reading Indian portfolio from Stock.xlsx...")
    portfolio_df = read_portfolio_excel()

    if portfolio_df is None:
        display_error_message("Cannot proceed without portfolio data")
        print("\n📋 Create 'Stocks.xlsx' with columns:")
        print("   - Company Name")
        print("   - Total Quantity") 
        print("   - Avg Trading Price")
        print("   - Sector (optional)")
        return

    # Validate portfolio data
    is_valid, validation_message = validate_portfolio_data(portfolio_df)
    if not is_valid:
        display_error_message(f"Portfolio validation failed: {validation_message}")
        return

    both, format_instructions = setup_models()

    portfolio_summary = format_indian_portfolio_data(portfolio_df)
    display_portfolio_data(portfolio_summary)

    display_model_selection()
    
    try:
        model_choice = input("Select model (1-3) or press Enter for both: ").strip()
    except EOFError:
        model_choice = "3"

    all_contexts = get_all_indian_market_contexts()
    combined_context = "Consider all market scenarios: " + "; ".join(all_contexts.values())
    
    resp, _ = analyze_portfolio(portfolio_df, combined_context, both, format_instructions)
    
    if model_choice == "1":
        display_single_recommendation(resp, "openai")
    elif model_choice == "2":
        display_single_recommendation(resp, "gemini")
    else:
        display_analysis_results(resp["openai"], resp["gemini"])
        portfolio_summary_text = get_portfolio_summary(portfolio_df)
        display_summary(resp["openai"], resp["gemini"], portfolio_summary_text)


if __name__ == "__main__":
    main()
