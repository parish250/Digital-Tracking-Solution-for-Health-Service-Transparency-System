from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
    citizen = "citizen"
    distributor = "distributor"
    official = "official"

class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRole

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        orm_mode = True
