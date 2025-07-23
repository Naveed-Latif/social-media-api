from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session 
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)


@router.post("/",response_model=schemas.UserResponse  ,status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.CreatUser, db: Session = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    
    hashed_password = utils.hash(new_user.password)
    new_user.password = hashed_password
    if db.query(models.User).filter(models.User.email == new_user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with email {new_user.email} already exists")
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
