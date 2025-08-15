from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.db_config import get_db
from app.models.user import User
from app.utils.auth import require_official, get_current_user

# Removed prefix here — main.py will add it
router = APIRouter(tags=["Food Aid Items"])

@router.post("/", response_model=schemas.FoodAidItem, status_code=status.HTTP_201_CREATED)
def create_food_aid_item(item: schemas.FoodAidItemCreate, db: Session = Depends(get_db), user: User = Depends(require_official)):
    db_item = models.FoodAidItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=list[schemas.FoodAidItem])
def get_food_aid_items(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[schemas.FoodAidItem]:
    return db.query(models.FoodAidItem).all()

@router.get("/{item_id}", response_model=schemas.FoodAidItem)
def get_food_aid_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> schemas.FoodAidItem:
    item = db.query(models.FoodAidItem).filter(models.FoodAidItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food aid item not found")
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_aid_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(require_official)):
    item = db.query(models.FoodAidItem).filter(models.FoodAidItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food aid item not found")
    db.delete(item)
    db.commit()
    return None
