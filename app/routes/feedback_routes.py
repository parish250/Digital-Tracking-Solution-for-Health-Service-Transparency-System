from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.models.food_aid import Feedback
from app.db_config import get_db
from app.models.user import User
from app.utils.auth import get_current_user, require_citizen, require_official
from app.services.sms_service import sms_service
from app.services.audit_service import get_audit_service

router = APIRouter()

# Remove the get_db function as it's imported from db_config

@router.post("/", response_model=FeedbackRead)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db), user: User = Depends(require_citizen)):
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    # Log audit trail
    audit_service = get_audit_service(db, user)
    audit_service.log_create(
        table_name="feedbacks",
        record_id=db_feedback.id,
        values=feedback.dict()
    )
    
    return db_feedback

@router.get("/", response_model=List[FeedbackRead])
def get_feedbacks(db: Session = Depends(get_db), user: User = Depends(require_official)):
    return db.query(Feedback).all()

@router.get("/{feedback_id}", response_model=FeedbackRead)
def get_feedback(feedback_id: int, db: Session = Depends(get_db), user: User = Depends(require_official)):

    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

# --- SMS/Webhook Endpoints ---
@router.post("/sms-webhook")
async def receive_sms_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint for receiving SMS messages from Twilio or other SMS providers
    """
    try:
        # Get the request body
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Parse the incoming data (this depends on your SMS provider)
        # For Twilio, you would parse the form data
        from_number = request.query_params.get('From', '')
        message_body = request.query_params.get('Body', '')
        
        # Process the SMS message
        processed_data = sms_service.receive_sms(from_number, message_body)
        
        # Create feedback entry in database
        feedback_entry = Feedback(
            shipment_id=processed_data["parsed_feedback"].get("shipment_id"),
            feedback_type=processed_data["parsed_feedback"].get("status", "general"),
            comment=f"SMS from {from_number}: {message_body}",
            anonymous=True,  # SMS feedback is typically anonymous
        )
        
        db.add(feedback_entry)
        db.commit()
        db.refresh(feedback_entry)
        
        # Log audit trail
        # Since this is an automated process, we'll use a system user
        class SystemUser:
            id = 0
            username = "system"
            role = "admin"
        
        system_user = SystemUser()
        audit_service = get_audit_service(db, system_user)
        audit_service.log_create(
            table_name="feedbacks",
            record_id=feedback_entry.id,
            values={
                "shipment_id": feedback_entry.shipment_id,
                "feedback_type": feedback_entry.feedback_type,
                "comment": feedback_entry.comment,
                "anonymous": feedback_entry.anonymous,
                "submitted_at": str(feedback_entry.submitted_at) if feedback_entry.submitted_at else None
            }
        )
        
        return {"status": "success", "message": "Feedback received and processed"}
    except Exception as e:
        print(f"Error processing SMS webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process SMS webhook")
