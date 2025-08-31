import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.data_models import TraderPick
from app.services.tools import fetch_live_price_yahoo



def now_ist_str():
    return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST")


def setup_chain():
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.4)
    parser = PydanticOutputParser(pydantic_object=TraderPick)
    format_instructions = parser.get_format_instructions()
    prompt = ChatPromptTemplate.from_template(
        "You are an Indian intraday trading assistant. Today is {today_ist}.\n"
        "Exchange: NSE (India). Output exactly ONE stock suitable for a single trade today.\n"
        "Requirements:\n"
        "Make sure it is for that particular day read the technical charts and breakthrough"
        "- Use NSE ticker with .NS (e.g., RELIANCE.NS).\n"
        "- Provide a concise reason (1-2 lines).\n"
        "- Provide exit_target_price in INR for today (float).\n"
        "- Provide exact exit_time_ist in HH:MM 24h IST (e.g., 15:20).\n"
        "- Prefer liquid, large-cap names.\n\n"
        "{format_instructions}"
    )
    chain = prompt | gemini_llm | parser
    return chain, format_instructions


def generate_recommendation(chain, format_instructions):
    pick = chain.invoke({"today_ist": now_ist_str(), "format_instructions": format_instructions})
    ticker = pick.ticker if pick.ticker.endswith(".NS") else f"{pick.ticker}.NS"
    live_price = fetch_live_price_yahoo(ticker)
    return pick, ticker, live_price


def display_result(pick, ticker, live_price):
    print("\n" + "=" * 60)
    print("INDIAN INTRADAY PICK (NSE)")
    print("=" * 60)
    print(f"🏢 Company: {pick.company_name}")
    print(f"Current price:{pick.current_price}")
    print(f"📈 Ticker: {ticker}")
    if live_price is not None:
        print(f"💹 Live Price: ₹{live_price:.2f}")
    print(f"🧭 Action: {pick.action}")
    print(f"🎯 Exit Target: ₹{pick.exit_target_price:.2f}")
    print(f"⏰ Exit Time (IST): {pick.exit_time_ist}")
    print(f"💡 Reason: {pick.reason}")
    print(f"📊 Confidence: {pick.confidence_score}%")


def main():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Please set the OPENAI_API_KEY environment variable.")
    chain, format_instructions = setup_chain()
    pick, ticker, live_price = generate_recommendation(chain, format_instructions)
    display_result(pick, ticker, live_price)


if __name__ == "__main__":
    main()


