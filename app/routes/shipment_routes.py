from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.db_config import get_db
from app.models.food_aid import Shipment, ScanLog, Warehouse, DistributionCenter, FoodAidItem

from app.schemas.shipment_schemas import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
    ScanLogCreate,
    ScanLogRead,
)

# Let main.py handle tags
router = APIRouter()

# Dependency placeholder for role-based access (to implement later)
def get_current_user():
    # TODO: Replace with real auth logic
    return {"role": "official", "user_id": 1}

@router.post("/", response_model=ShipmentRead, status_code=status.HTTP_201_CREATED)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_shipment = Shipment(
        aid_item_id=shipment.aid_item_id,
        origin_id=shipment.origin_id,
        destination_id=shipment.destination_id,
        status=shipment.status,
        timestamp=shipment.timestamp or datetime.utcnow(),
    )
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment

@router.get("/", response_model=List[ShipmentRead])
def list_shipments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(Shipment).offset(skip).limit(limit).all()

@router.get("/{shipment_id}", response_model=ShipmentRead)
def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment

@router.put("/{shipment_id}", response_model=ShipmentRead)
def update_shipment(
    shipment_id: int,
    shipment_update: ShipmentUpdate,
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    for var, value in vars(shipment_update).items():
        if value is not None:
            setattr(shipment, var, value)
    db.commit()
    db.refresh(shipment)
    return shipment

@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shipment(
    shipment_id: int,
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    db.delete(shipment)
    db.commit()
    return

# --- QR Code Scan Logging ---
@router.post("/{shipment_id}/scan", response_model=ScanLogRead)
def log_scan(
    shipment_id: int,
    scan_data: ScanLogCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    scan_log = ScanLog(
        shipment_id=shipment_id,
        location=scan_data.location,
        scanned_at=scan_data.scanned_at or datetime.utcnow(),
        scanned_by=scan_data.scanned_by or f"user_{user['user_id']}"
    )
    db.add(scan_log)
    db.commit()
    db.refresh(scan_log)
    return scan_log
