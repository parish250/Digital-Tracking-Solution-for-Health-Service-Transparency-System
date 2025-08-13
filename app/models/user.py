from sqlalchemy import Column, Integer, String, Enum
from app.db_config import Base
import enum

class UserRole(str, enum.Enum):
    citizen = "citizen"
    distributor = "distributor"
    official = "official"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.citizen, nullable=False)
