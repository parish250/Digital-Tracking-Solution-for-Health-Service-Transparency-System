from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db_config import Base
from datetime import datetime


class AuditTrail(Base):
    __tablename__ = "audit_trails"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # e.g., "create", "update", "delete"
    table_name = Column(String(50), nullable=False)  # e.g., "shipments", "feedbacks"
    record_id = Column(Integer, nullable=False)  # ID of the record that was modified
    old_values = Column(String(500))  # JSON string of old values
    new_values = Column(String(500))  # JSON string of new values
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditTrail(id={self.id}, user_id={self.user_id}, action={self.action}, table={self.table_name})>"