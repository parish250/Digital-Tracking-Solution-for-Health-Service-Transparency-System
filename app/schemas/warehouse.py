from pydantic import BaseModel
from typing import Optional


# Shared attributes for all schemas
class WarehouseBase(BaseModel):
    name: str
    location: str


# For creating a warehouse
class WarehouseCreate(WarehouseBase):
    pass


# For updating a warehouse (partial)
class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


# For reading warehouse data (matches route's response_model=Warehouse)
class Warehouse(WarehouseBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode
