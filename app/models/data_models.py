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

