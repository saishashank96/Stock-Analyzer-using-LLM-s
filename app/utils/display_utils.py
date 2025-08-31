from datetime import datetime


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


def display_summary(openai_action, gemini_action, portfolio_summary):
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

    print(f"\n{portfolio_summary}")
    print("🇮🇳 Analysis complete for Indian market conditions!")
    print(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def display_single_recommendation(resp, model_name):
    """Display single model recommendation"""
    if model_name == "openai":
        print("\n🤖 OpenAI GPT-4 Recommendation:")
        action = resp['openai']
    else:
        print("\n🧠 Google Gemini Recommendation:")
        action = resp['gemini']
    
    print(f"📈 Action: {action.action} - {action.ticker}")
    print(f"💡 Reason: {action.reason}")
    print(f"⚡ Priority: {action.priority}")
    print(f"🎯 Target Allocation: {action.target_allocation}")
    print(f"📊 Sector Outlook: {action.sector_outlook}")
    print(f"🎯 Confidence: {action.confidence_score}%")


def display_portfolio_header():
    """Display portfolio analyzer header"""
    print("🇮🇳 Indian Stock Portfolio Analyzer")
    print("=" * 50)


def display_model_selection():
    """Display model selection menu"""
    print("\n🤖 Choose AI Model:")
    print("1. OpenAI GPT-4")
    print("2. Google Gemini")
    print("3. Both models")


def display_analysis_progress(market_context):
    """Display analysis progress information"""
    print(f"\n🤖 Analyzing Indian portfolio with context: {market_context}")
    print("⏳ Generating recommendations...")


def display_portfolio_data(portfolio_summary):
    """Display current portfolio data"""
    print("\n📋 Current Indian Portfolio:")
    print(portfolio_summary)


def display_error_message(message):
    """Display error message with formatting"""
    print(f"❌ {message}")


def display_success_message(message):
    """Display success message with formatting"""
    print(f"✅ {message}")


def display_warning_message(message):
    """Display warning message with formatting"""
    print(f"⚠️ {message}")


def display_info_message(message):
    """Display info message with formatting"""
    print(f"ℹ️ {message}")


