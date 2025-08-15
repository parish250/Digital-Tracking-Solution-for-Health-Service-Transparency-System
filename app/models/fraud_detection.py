from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from app.db_config import Base
from datetime import datetime


class FraudDetection(Base):
    __tablename__ = "fraud_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    score = Column(Float, nullable=False)  # Fraud probability score (0-1)
    is_fraud = Column(Boolean, default=False)
    reason = Column(String(255))  # Reason for fraud detection
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FraudDetection(id={self.id}, shipment_id={self.shipment_id}, score={self.score}, is_fraud={self.is_fraud})>"