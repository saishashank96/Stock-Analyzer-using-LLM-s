from pydantic import BaseModel, Field


class IndianStockAction(BaseModel):
    """Data model for Indian stock portfolio analysis recommendations"""
    ticker: str = Field(description="Indian stock ticker (e.g., RELIANCE.NS, TCS.NS)")
    company_name: str = Field(description="Indian company name")
    action: str = Field(description="BUY, SELL, HOLD, or ADD (buy more)")
    reason: str = Field(description="Detailed reason considering Indian market conditions")
    priority: str = Field(description="HIGH, MEDIUM, or LOW priority")
    target_allocation: str = Field(description="Suggested position size or percentage")
    sector_outlook: str = Field(description="Outlook for this sector in Indian market")
    best_sector_to_add: str = Field(default="Unknown", description="Single best Indian market sector to add now")
    confidence_score: int = Field(default=70, description="Confidence score (0-100)")


class TraderPick(BaseModel):
    ticker: str = Field(description="NSE ticker with .NS suffix (e.g., TCS.NS)")
    company_name: str = Field(description="Company name")
    action: str = Field(description="BUY or SELL for a single intraday trade")
    reason: str = Field(description="Brief rationale (1-2 lines)")
    exit_target_price: float = Field(description="Target price to exit today in INR")
    exit_time_ist: str = Field(description="Exact exit time in HH:MM 24h IST (e.g., 15:20)")
    confidence_score: int = Field(default=70, description="0-100 confidence")
    current_price: float = Field(description="Current price of the stock in INR")

