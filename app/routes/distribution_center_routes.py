from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.db_config import get_db

# Removed prefix here — main.py already adds it
router = APIRouter(tags=["Distribution Centers"])

@router.post("/", response_model=schemas.DistributionCenter, status_code=status.HTTP_201_CREATED)
def create_distribution_center(center: schemas.DistributionCenterCreate, db: Session = Depends(get_db)):
    db_center = models.DistributionCenter(**center.dict())
    db.add(db_center)
    db.commit()
    db.refresh(db_center)
    return db_center

@router.get("/", response_model=list[schemas.DistributionCenter])
def get_distribution_centers(db: Session = Depends(get_db)) -> list[schemas.DistributionCenter]:
    return db.query(models.DistributionCenter).all()

@router.get("/{center_id}", response_model=schemas.DistributionCenter)
def get_distribution_center(center_id: int, db: Session = Depends(get_db)) -> schemas.DistributionCenter:
    center = db.query(models.DistributionCenter).filter(models.DistributionCenter.id == center_id).first()
    if not center:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Distribution center not found")
    return center

@router.delete("/{center_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_distribution_center(center_id: int, db: Session = Depends(get_db)):
    center = db.query(models.DistributionCenter).filter(models.DistributionCenter.id == center_id).first()
    if not center:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Distribution center not found")
    db.delete(center)
    db.commit()
    return None
