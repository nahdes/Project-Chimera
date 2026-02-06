from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal


class GeneratePostInput(BaseModel):
    topic: str = Field(..., min_length=1)
    platform: Literal["twitter", "instagram", "tiktok"]
    tone: Optional[str] = None
    max_length: Optional[int] = None


class GeneratePostOutput(BaseModel):
    text_content: str
    hashtags: List[str]
    estimated_engagement_score: float = Field(ge=0.0, le=1.0)
    safety_check: Dict[str, Any]


class ExecuteTransactionInput(BaseModel):
    transaction_type: str
    from_wallet: str
    to_address: str
    amount: str
    token_type: Literal["ETH", "BASE", "USDC", "custom"]
    reason: Optional[str] = None
