from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.warehouse import WarehouseCreate, Warehouse
from app.database import get_db
from app.models import Warehouse as WarehouseModel

router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"]
)

# Create a warehouse
@router.post("/", response_model=Warehouse)
def create_warehouse(warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    db_warehouse = WarehouseModel(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

# Get all warehouses
@router.get("/", response_model=List[Warehouse])
def get_warehouses(db: Session = Depends(get_db)):
    return db.query(WarehouseModel).all()

# Get single warehouse
@router.get("/{warehouse_id}", response_model=Warehouse)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = db.query(WarehouseModel).filter(WarehouseModel.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

# Update a warehouse
@router.put("/{warehouse_id}", response_model=Warehouse)
def update_warehouse(warehouse_id: int, warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    db_warehouse = db.query(WarehouseModel).filter(WarehouseModel.id == warehouse_id).first()
    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    for key, value in warehouse.dict().items():
        setattr(db_warehouse, key, value)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

# Delete a warehouse
@router.delete("/{warehouse_id}")
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = db.query(WarehouseModel).filter(WarehouseModel.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    db.delete(warehouse)
    db.commit()
    return {"message": "Warehouse deleted successfully"}
