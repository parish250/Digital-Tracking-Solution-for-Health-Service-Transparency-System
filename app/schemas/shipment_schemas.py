from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ShipmentBase(BaseModel):
    aid_item_id: int
    origin_id: Optional[int] = None
    destination_id: Optional[int] = None
    status: Optional[str] = "dispatched"
    timestamp: Optional[datetime]

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentUpdate(BaseModel):
    aid_item_id: Optional[int]
    origin_id: Optional[int]
    destination_id: Optional[int]
    status: Optional[str]
    timestamp: Optional[datetime]

class ShipmentRead(ShipmentBase):
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        orm_mode = True

class ScanLogBase(BaseModel):
    location: str
    scanned_at: Optional[datetime]
    scanned_by: Optional[str]

class ScanLogCreate(ScanLogBase):
    pass

class ScanLogRead(ScanLogBase):
    id: int
    shipment_id: int

    class Config:
        orm_mode = True