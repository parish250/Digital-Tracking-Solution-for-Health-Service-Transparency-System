from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.db_config import get_db
from app.models.food_aid import Shipment, ScanLog, Warehouse, DistributionCenter, FoodAidItem
from app.models.user import User
from app.models.fraud_detection import FraudDetection

from app.schemas.shipment_schemas import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
    ScanLogCreate,
    ScanLogRead,
)

from app.utils.auth import get_current_user, require_distributor, require_official
from app.services.fraud_detection import fraud_detection_service
from app.services.audit_service import get_audit_service

# Let main.py handle tags
router = APIRouter()

@router.post("/", response_model=ShipmentRead, status_code=status.HTTP_201_CREATED)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_official)
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
    
    # Log audit trail
    audit_service = get_audit_service(db, user)
    audit_service.log_create(
        table_name="shipments",
        record_id=db_shipment.id,
        values={
            "aid_item_id": shipment.aid_item_id,
            "origin_id": shipment.origin_id,
            "destination_id": shipment.destination_id,
            "status": shipment.status,
            "timestamp": str(shipment.timestamp or datetime.utcnow())
        }
    )
    
    return db_shipment

@router.get("/", response_model=List[ShipmentRead])
def list_shipments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Shipment).offset(skip).limit(limit).all()

@router.get("/{shipment_id}", response_model=ShipmentRead)
def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment

@router.put("/{shipment_id}", response_model=ShipmentRead)
def update_shipment(
    shipment_id: int,
    shipment_update: ShipmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_official)
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Store old values for audit trail
    old_values = {
        "aid_item_id": shipment.aid_item_id,
        "origin_id": shipment.origin_id,
        "destination_id": shipment.destination_id,
        "status": shipment.status,
        "timestamp": str(shipment.timestamp)
    }
    
    for var, value in vars(shipment_update).items():
        if value is not None:
            setattr(shipment, var, value)
    db.commit()
    db.refresh(shipment)
    
    # Log audit trail
    audit_service = get_audit_service(db, user)
    new_values = {
        "aid_item_id": shipment.aid_item_id,
        "origin_id": shipment.origin_id,
        "destination_id": shipment.destination_id,
        "status": shipment.status,
        "timestamp": str(shipment.timestamp)
    }
    audit_service.log_update(
        table_name="shipments",
        record_id=shipment_id,
        old_values=old_values,
        new_values=new_values
    )
    
    return shipment

@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_official)
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Store old values for audit trail
    old_values = {
        "aid_item_id": shipment.aid_item_id,
        "origin_id": shipment.origin_id,
        "destination_id": shipment.destination_id,
        "status": shipment.status,
        "timestamp": str(shipment.timestamp)
    }
    
    db.delete(shipment)
    db.commit()
    
    # Log audit trail
    audit_service = get_audit_service(db, user)
    audit_service.log_delete(
        table_name="shipments",
        record_id=shipment_id,
        old_values=old_values
    )
    
    return

# --- QR Code Scan Logging ---
@router.post("/{shipment_id}/scan", response_model=ScanLogRead)
def log_scan(
    shipment_id: int,
    scan_data: ScanLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_distributor)
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    scan_log = ScanLog(
        shipment_id=shipment_id,
        location=scan_data.location,
        scanned_at=scan_data.scanned_at or datetime.utcnow(),
        scanned_by=scan_data.scanned_by or f"user_{user.id}"
    )
    db.add(scan_log)
    db.commit()
    db.refresh(scan_log)
    
    # Log audit trail
    audit_service = get_audit_service(db, user)
    audit_service.log_create(
        table_name="scan_logs",
        record_id=scan_log.id,
        values={
            "shipment_id": shipment_id,
            "location": scan_data.location,
            "scanned_at": str(scan_data.scanned_at or datetime.utcnow()),
            "scanned_by": scan_data.scanned_by or f"user_{user.id}"
        }
    )
    
    # Run fraud detection on the shipment
    try:
        score, is_fraud, reason = fraud_detection_service.predict_fraud(shipment, db)
        
        # Store fraud detection result
        fraud_detection = FraudDetection(
            shipment_id=shipment_id,
            score=score,
            is_fraud=is_fraud,
            reason=reason
        )
        db.add(fraud_detection)
        db.commit()
        
        # Log fraud detection in audit trail
        audit_service.log_create(
            table_name="fraud_detections",
            record_id=fraud_detection.id,
            values={
                "shipment_id": shipment_id,
                "score": score,
                "is_fraud": is_fraud,
                "reason": reason
            }
        )
    except Exception as e:
        # Log error but don't fail the scan
        print(f"Fraud detection error: {e}")
    
    return scan_log

# --- Fraud Detection ---
@router.get("/{shipment_id}/fraud-analysis")
def get_fraud_analysis(
    shipment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get fraud analysis for a specific shipment
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Run fraud detection
    score, is_fraud, reason = fraud_detection_service.predict_fraud(shipment, db)
    
    return {
        "shipment_id": shipment_id,
        "fraud_score": score,
        "is_fraud": is_fraud,
        "reason": reason,
        "timestamp": datetime.utcnow()
    }

# --- Audit Trail ---
@router.get("/{shipment_id}/audit-trail")
def get_shipment_audit_trail(
    shipment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get audit trail for a specific shipment
    """
    audit_service = get_audit_service(db, user)
    audit_trail = audit_service.get_audit_trail(
        table_name="shipments",
        record_id=shipment_id
    )
    
    return audit_trail
