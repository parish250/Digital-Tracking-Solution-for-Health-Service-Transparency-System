# enhanced_main.py - Add these endpoints to your existing FastAPI application

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import qrcode
import io
import base64
import json
import uuid

# Add these imports to your existing ones
import qrcode
from PIL import Image
import hashlib

app = FastAPI(title="Digital Tracking Solution for Health Service Transparency")

# ============================================================================
# NEW PYDANTIC MODELS - Add these to your existing models
# ============================================================================

class QRCodeGenerate(BaseModel):
    shipment_id: str
    checkpoint_type: str  # "warehouse", "distribution_center", "delivery"
    location: str
    expected_items: int

class QRCodeResponse(BaseModel):
    qr_code_id: str
    shipment_id: str
    qr_code_data: str  # Base64 encoded QR image
    qr_code_url: str   # URL for scanning
    checkpoint_info: dict

class ScanLogCreate(BaseModel):
    qr_code_id: str
    shipment_id: str
    scanned_by: str      # Officer/Personnel ID
    scanned_at: datetime = datetime.now()
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    items_count: Optional[int] = None
    status: str  # "arrived", "departed", "delivered", "issue"
    notes: Optional[str] = None
    photos: Optional[List[str]] = []  # Base64 encoded photos

class ScanLogRead(BaseModel):
    id: str
    qr_code_id: str
    shipment_id: str
    scanned_by: str
    scanned_at: datetime
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    items_count: Optional[int]
    status: str
    notes: Optional[str]
    photos: Optional[List[str]]
    created_at: datetime

class StatusUpdate(BaseModel):
    shipment_id: str
    new_status: str
    location: str
    updated_by: str
    notes: Optional[str] = None
    timestamp: datetime = datetime.now()

class RealTimeEvent(BaseModel):
    event_id: str
    event_type: str  # "scan", "status_update", "alert"
    shipment_id: str
    data: dict
    timestamp: datetime

# ============================================================================
# QR CODE GENERATION ENDPOINTS
# ============================================================================

@app.post("/qr-codes/generate", response_model=QRCodeResponse)
async def generate_qr_code(qr_request: QRCodeGenerate, db: Session = Depends(get_db)):
    """
    Generate QR code for a shipment checkpoint
    """
    try:
        # Verify shipment exists
        shipment = db.query(Shipment).filter(Shipment.id == qr_request.shipment_id).first()
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        # Generate unique QR code ID
        qr_code_id = str(uuid.uuid4())
        
        # Create QR code data payload
        qr_data = {
            "qr_id": qr_code_id,
            "shipment_id": qr_request.shipment_id,
            "checkpoint": qr_request.checkpoint_type,
            "location": qr_request.location,
            "expected_items": qr_request.expected_items,
            "generated_at": datetime.now().isoformat(),
            "hash": hashlib.md5(f"{qr_code_id}{qr_request.shipment_id}".encode()).hexdigest()[:8]
        }
        
        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        # Store QR code info in database (you'll need to create this table)
        # For now, we'll return the response
        
        return QRCodeResponse(
            qr_code_id=qr_code_id,
            shipment_id=qr_request.shipment_id,
            qr_code_data=f"data:image/png;base64,{img_str}",
            qr_code_url=f"/qr-codes/{qr_code_id}/scan",
            checkpoint_info={
                "type": qr_request.checkpoint_type,
                "location": qr_request.location,
                "expected_items": qr_request.expected_items,
                "generated_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR code generation failed: {str(e)}")

@app.get("/qr-codes/{qr_code_id}/info")
async def get_qr_code_info(qr_code_id: str, db: Session = Depends(get_db)):
    """
    Get QR code information for scanning apps
    """
    # In a real implementation, you'd query from database
    # For now, return mock data structure
    return {
        "qr_code_id": qr_code_id,
        "valid": True,
        "shipment_info": {
            "id": "SHP-1001",
            "status": "In Transit",
            "origin": "Central Warehouse",
            "destination": "Nyagatare DC"
        },
        "checkpoint_info": {
            "type": "distribution_center",
            "location": "Nyagatare Distribution Center",
            "expected_items": 250
        }
    }

# ============================================================================
# SCAN LOGGING ENDPOINTS
# ============================================================================

@app.post("/scans/log", response_model=ScanLogRead)
async def log_scan(scan_data: ScanLogCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Log a QR code scan and update shipment status
    """
    try:
        # Verify QR code and shipment exist
        shipment = db.query(Shipment).filter(Shipment.id == scan_data.shipment_id).first()
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        # Generate scan log ID
        scan_id = str(uuid.uuid4())
        
        # Create scan log entry
        scan_log = ScanLogRead(
            id=scan_id,
            qr_code_id=scan_data.qr_code_id,
            shipment_id=scan_data.shipment_id,
            scanned_by=scan_data.scanned_by,
            scanned_at=scan_data.scanned_at,
            location=scan_data.location,
            latitude=scan_data.latitude,
            longitude=scan_data.longitude,
            items_count=scan_data.items_count,
            status=scan_data.status,
            notes=scan_data.notes,
            photos=scan_data.photos or [],
            created_at=datetime.now()
        )
        
        # Update shipment status based on scan
        await update_shipment_from_scan(scan_data, db)
        
        # Send real-time notification
        background_tasks.add_task(broadcast_scan_event, scan_log)
        
        # In real implementation, save to database here
        # db.add(scan_log_db_model)
        # db.commit()
        
        return scan_log
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan logging failed: {str(e)}")

@app.get("/scans/shipment/{shipment_id}", response_model=List[ScanLogRead])
async def get_shipment_scans(shipment_id: str, db: Session = Depends(get_db)):
    """
    Get all scan logs for a specific shipment
    """
    # Mock response - replace with actual database query
    return [
        ScanLogRead(
            id="scan-1",
            qr_code_id="qr-123",
            shipment_id=shipment_id,
            scanned_by="Officer-001",
            scanned_at=datetime.now() - timedelta(hours=2),
            location="Central Warehouse",
            latitude=-1.9441,
            longitude=29.8739,
            items_count=250,
            status="departed",
            notes="All items verified and loaded",
            photos=[],
            created_at=datetime.now() - timedelta(hours=2)
        ),
        ScanLogRead(
            id="scan-2",
            qr_code_id="qr-123",
            shipment_id=shipment_id,
            scanned_by="Officer-002",
            scanned_at=datetime.now() - timedelta(minutes=30),
            location="Nyagatare DC",
            latitude=-1.2921,
            longitude=30.3426,
            items_count=250,
            status="arrived",
            notes="Arrived at distribution center",
            photos=[],
            created_at=datetime.now() - timedelta(minutes=30)
        )
    ]

# ============================================================================
# REAL-TIME STATUS UPDATE ENDPOINTS
# ============================================================================

@app.post("/shipments/{shipment_id}/status")
async def update_shipment_status(
    shipment_id: str, 
    status_update: StatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Update shipment status and broadcast real-time notification
    """
    try:
        # Verify shipment exists
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        # Update shipment status
        old_status = shipment.status
        shipment.status = status_update.new_status
        shipment.current_location = status_update.location
        shipment.updated_at = status_update.timestamp
        
        # Create status history entry
        status_history = {
            "id": str(uuid.uuid4()),
            "shipment_id": shipment_id,
            "old_status": old_status,
            "new_status": status_update.new_status,
            "location": status_update.location,
            "updated_by": status_update.updated_by,
            "notes": status_update.notes,
            "timestamp": status_update.timestamp
        }
        
        # Broadcast real-time event
        background_tasks.add_task(broadcast_status_update, shipment_id, status_update)
        
        # In real implementation, save to database
        # db.commit()
        
        return {
            "message": "Status updated successfully",
            "shipment_id": shipment_id,
            "old_status": old_status,
            "new_status": status_update.new_status,
            "updated_at": status_update.timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")

@app.get("/shipments/{shipment_id}/status-history")
async def get_status_history(shipment_id: str, db: Session = Depends(get_db)):
    """
    Get complete status history for a shipment
    """
    # Mock response - replace with actual database query
    return [
        {
            "id": "hist-1",
            "shipment_id": shipment_id,
            "status": "Created",
            "location": "Central Warehouse",
            "updated_by": "System",
            "timestamp": datetime.now() - timedelta(days=2),
            "notes": "Shipment created and items allocated"
        },
        {
            "id": "hist-2",
            "shipment_id": shipment_id,
            "status": "In Transit",
            "location": "Central Warehouse",
            "updated_by": "Officer-001",
            "timestamp": datetime.now() - timedelta(hours=6),
            "notes": "Items loaded and departed"
        },
        {
            "id": "hist-3",
            "shipment_id": shipment_id,
            "status": "At Distribution Center",
            "location": "Nyagatare DC",
            "updated_by": "Officer-002",
            "timestamp": datetime.now() - timedelta(minutes=30),
            "notes": "Arrived at distribution center"
        }
    ]

# ============================================================================
# REAL-TIME EVENTS & NOTIFICATIONS
# ============================================================================

@app.get("/events/real-time/{shipment_id}")
async def get_real_time_events(shipment_id: str, since: Optional[datetime] = None):
    """
    Get real-time events for a shipment (can be used for polling or websockets)
    """
    # Mock real-time events
    events = [
        RealTimeEvent(
            event_id=str(uuid.uuid4()),
            event_type="scan",
            shipment_id=shipment_id,
            data={
                "location": "Nyagatare DC",
                "scanned_by": "Officer-002",
                "status": "arrived",
                "items_verified": 250
            },
            timestamp=datetime.now() - timedelta(minutes=5)
        ),
        RealTimeEvent(
            event_id=str(uuid.uuid4()),
            event_type="status_update",
            shipment_id=shipment_id,
            data={
                "old_status": "In Transit",
                "new_status": "At Distribution Center",
                "location": "Nyagatare DC"
            },
            timestamp=datetime.now() - timedelta(minutes=3)
        )
    ]
    
    if since:
        events = [e for e in events if e.timestamp > since]
    
    return {"events": events}

@app.get("/alerts/active")
async def get_active_alerts():
    """
    Get active alerts for the dashboard
    """
    return {
        "alerts": [
            {
                "id": "alert-1",
                "type": "delay",
                "severity": "warning",
                "shipment_id": "SHP-1001",
                "message": "Shipment delayed by 2 hours",
                "created_at": datetime.now() - timedelta(hours=1),
                "resolved": False
            },
            {
                "id": "alert-2",
                "type": "anomaly",
                "severity": "danger",
                "shipment_id": "SHP-1003",
                "message": "Unusual route deviation detected",
                "created_at": datetime.now() - timedelta(minutes=30),
                "resolved": False
            }
        ]
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def update_shipment_from_scan(scan_data: ScanLogCreate, db: Session):
    """
    Update shipment status based on scan information
    """
    status_mapping = {
        "arrived": "At Distribution Center",
        "departed": "In Transit", 
        "delivered": "Delivered",
        "issue": "Delayed"
    }
    
    if scan_data.status in status_mapping:
        # In real implementation, update database
        # shipment = db.query(Shipment).filter(Shipment.id == scan_data.shipment_id).first()
        # shipment.status = status_mapping[scan_data.status]
        # shipment.current_location = scan_data.location
        # db.commit()
        pass

async def broadcast_scan_event(scan_log: ScanLogRead):
    """
    Broadcast scan event to real-time subscribers (WebSocket, SSE, etc.)
    """
    # In real implementation, use WebSocket or Server-Sent Events
    print(f"Broadcasting scan event: {scan_log.shipment_id} scanned at {scan_log.location}")

async def broadcast_status_update(shipment_id: str, status_update: StatusUpdate):
    """
    Broadcast status update to real-time subscribers
    """
    # In real implementation, use WebSocket or Server-Sent Events
    print(f"Broadcasting status update: {shipment_id} -> {status_update.new_status}")

# ============================================================================
# BATCH OPERATIONS FOR EFFICIENCY
# ============================================================================

@app.post("/scans/batch")
async def log_multiple_scans(scans: List[ScanLogCreate], db: Session = Depends(get_db)):
    """
    Log multiple scans at once (useful for offline sync)
    """
    results = []
    for scan in scans:
        try:
            scan_result = await log_scan(scan, BackgroundTasks(), db)
            results.append({"success": True, "scan_id": scan_result.id})
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    
    return {"results": results}

@app.get("/shipments/tracking-summary")
async def get_tracking_summary():
    """
    Get summary data for dashboard KPIs
    """
    return {
        "total_shipments": 156,
        "in_transit": 23,
        "delivered": 98,
        "delayed": 8,
        "at_warehouses": 15,
        "at_distribution_centers": 12,
        "average_transit_time_hours": 36.5,
        "on_time_delivery_rate": 87.3,
        "last_updated": datetime.now()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)