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

load_dotenv()

# Pydantic model for structured stock recommendation
class Stock(BaseModel):
    ticker: str = Field(description="Stock ticker symbol")
    company_name: str = Field(description="Company name")
    reason: str = Field(description="Short reason for recommendation")
    recommendation: str = Field(description="BUY, HOLD, or SELL")

# Require both keys
if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("Please set the OPENAI_API_KEY environment variable.")
if not os.getenv("GOOGLE_API_KEY"):
    raise SystemExit("Please set the GOOGLE_API_KEY environment variable.")

# Models
openai_llm = ChatOpenAI(model="gpt-4", temperature=0.4)
gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.4)

# Parser setup
parser = PydanticOutputParser(pydantic_object=Stock)
format_instructions = parser.get_format_instructions()

# Prompt with format instructions
prompt = ChatPromptTemplate.from_template(
    "Suggest exactly one stock from {name} to invest in. "
    "Provide the ticker, company name, reason, and recommendation.\n\n"
    "{format_instructions}"
)
# Run both in parallel with structured output
both = RunnableParallel(
    openai = prompt | openai_llm | parser,
    gemini = prompt | gemini_llm | parser,
)

name = input("Country  ").strip()
resp = both.invoke({"name": name, "format_instructions": format_instructions})

# Display structured results
print("\n" + "="*50)
print("OPENAI RECOMMENDATION")
print("="*50)
openai_stock = resp["openai"]
print(f"🏢 Company: {openai_stock.company_name}")
print(f"📈 Ticker: {openai_stock.ticker}")
print(f"📊 Recommendation: {openai_stock.recommendation}")
print(f"💡 Reason: {openai_stock.reason}")

print("\n" + "="*50)
print("GEMINI RECOMMENDATION")
print("="*50)
gemini_stock = resp["gemini"]
print(f"🏢 Company: {gemini_stock.company_name}")
print(f"📈 Ticker: {gemini_stock.ticker}")
print(f"📊 Recommendation: {gemini_stock.recommendation}")
print(f"💡 Reason: {gemini_stock.reason}")