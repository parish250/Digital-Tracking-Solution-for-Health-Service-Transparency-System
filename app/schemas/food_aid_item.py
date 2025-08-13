from pydantic import BaseModel

class FoodAidItemBase(BaseModel):
    name: str
    quantity: int
    unit: str

class FoodAidItemCreate(FoodAidItemBase):
    pass

class FoodAidItem(FoodAidItemBase):
    id: int

    class Config:
        orm_mode = True
