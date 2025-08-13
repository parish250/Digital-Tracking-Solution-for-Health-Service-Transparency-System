from pydantic import BaseModel

class DistributionCenterBase(BaseModel):
    name: str
    location: str

class DistributionCenterCreate(DistributionCenterBase):
    pass

class DistributionCenter(DistributionCenterBase):
    id: int

    class Config:
        orm_mode = True

