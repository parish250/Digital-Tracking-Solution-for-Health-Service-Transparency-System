from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FeedbackBase(BaseModel):
    shipment_id: int
    feedback_type: str
    comment: str
    anonymous: bool = True
    submitted_at: Optional[datetime] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackRead(FeedbackBase):
    id: int

    class Config:
        orm_mode = True
