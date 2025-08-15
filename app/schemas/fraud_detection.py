from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FraudDetectionBase(BaseModel):
    shipment_id: int
    score: float
    is_fraud: bool
    reason: Optional[str] = None


class FraudDetectionCreate(FraudDetectionBase):
    pass


class FraudDetectionRead(FraudDetectionBase):
    id: int
    detected_at: datetime

    class Config:
        orm_mode = True


class FraudAnalysisResponse(BaseModel):
    shipment_id: int
    fraud_score: float
    is_fraud: bool
    reason: str
    timestamp: datetime