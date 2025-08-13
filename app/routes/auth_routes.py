from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db_config import get_db
from app import models, schemas
from app.utils.security import hash_password, verify_password, create_access_token
from app import schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_pw = hash_password(user.password)
    new_user = models.User(username=user.username, password_hash=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.username, "role": db_user.role.value})
    return {"access_token": token, "token_type": "bearer"}
