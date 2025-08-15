import json
from sqlalchemy.orm import Session
from app.models.audit_trail import AuditTrail
from app.models.user import User
from typing import Dict, Any, Optional


class AuditService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
    
    def log_action(
        self, 
        action: str, 
        table_name: str, 
        record_id: int,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ):
        """
        Log an action to the audit trail
        
        Args:
            action: The action performed (create, update, delete)
            table_name: The name of the table affected
            record_id: The ID of the record affected
            old_values: Dictionary of old values (for update/delete)
            new_values: Dictionary of new values (for create/update)
        """
        try:
            # Convert dictionaries to JSON strings
            old_values_str = json.dumps(old_values) if old_values else None
            new_values_str = json.dumps(new_values) if new_values else None
            
            # Create audit trail entry
            audit_entry = AuditTrail(
                user_id=self.user.id,
                action=action,
                table_name=table_name,
                record_id=record_id,
                old_values=old_values_str,
                new_values=new_values_str
            )
            
            # Add to database
            self.db.add(audit_entry)
            self.db.commit()
            self.db.refresh(audit_entry)
            
            return audit_entry
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Error logging audit trail: {e}")
            self.db.rollback()
            return None
    
    def log_create(self, table_name: str, record_id: int, values: Dict[str, Any]):
        """
        Log a create action
        """
        return self.log_action("create", table_name, record_id, new_values=values)
    
    def log_update(self, table_name: str, record_id: int, old_values: Dict[str, Any], new_values: Dict[str, Any]):
        """
        Log an update action
        """
        return self.log_action("update", table_name, record_id, old_values=old_values, new_values=new_values)
    
    def log_delete(self, table_name: str, record_id: int, old_values: Dict[str, Any]):
        """
        Log a delete action
        """
        return self.log_action("delete", table_name, record_id, old_values=old_values)
    
    def get_audit_trail(self, table_name: str = None, record_id: int = None, limit: int = 100):
        """
        Retrieve audit trail entries
        
        Args:
            table_name: Filter by table name (optional)
            record_id: Filter by record ID (optional)
            limit: Maximum number of entries to return
            
        Returns:
            List of audit trail entries
        """
        query = self.db.query(AuditTrail)
        
        if table_name:
            query = query.filter(AuditTrail.table_name == table_name)
            
        if record_id:
            query = query.filter(AuditTrail.record_id == record_id)
            
        return query.order_by(AuditTrail.timestamp.desc()).limit(limit).all()


# Helper function to create audit service instance
def get_audit_service(db: Session, user: User):
    """
    Create an audit service instance
    """
    return AuditService(db, user)