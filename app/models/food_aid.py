from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.db_config import Base

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    location = Column(String(255))

class DistributionCenter(Base):
    __tablename__ = "distribution_centers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    location = Column(String(255))

class FoodAidItem(Base):
    __tablename__ = "food_aid_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    quantity = Column(Integer)

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    aid_item_id = Column(Integer, ForeignKey("food_aid_items.id"))
    origin_id = Column(Integer, ForeignKey("warehouses.id"))
    destination_id = Column(Integer, ForeignKey("distribution_centers.id"))
    status = Column(String(50))  # e.g., dispatched, in transit, delivered
    timestamp = Column(DateTime)

    aid_item = relationship("FoodAidItem")
    origin = relationship("Warehouse")
    destination = relationship("DistributionCenter")

class ScanLog(Base):
    __tablename__ = "scan_logs"
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"))
    location = Column(String(255))
    scanned_at = Column(DateTime)
    scanned_by = Column(String(100))  # could be linked to a user table later

class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"))
    feedback_type = Column(String(50))  # e.g., received, missing, delayed
    comment = Column(Text)
    anonymous = Column(Boolean, default=True)
    submitted_at = Column(DateTime)
