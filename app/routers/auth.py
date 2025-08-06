from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.Token)
def login(response: Response, user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_data = db.query(models.User).filter(models.User.email == user.username).first()
    if not user_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invaild credentials")
    
    if not utils.verify(user.password, user_data.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Incorrect password ")
        
    # create token 
    # token
    access_token = oauth2.create_access_token(data={"user_id": user_data.id})
    
    refresh_token = oauth2.create_refresh_token(user_data.id, db)
        
        # Set refresh token as HTTP-only cookie
    response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=7*24*60*60,  # 7 days in seconds
            samesite="lax"
        )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)):
    
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")
    
    # Validate the refresh token
    db_token = oauth2.validate_refresh_token(refresh_token, db)
    
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    # 🔄 TOKEN ROTATION MAGIC STARTS HERE
    
    # 1. Revoke the old refresh token (security!)
    oauth2.revoke_refresh_token(refresh_token, db)
    
    # 2. Create a brand new access token
    new_access_token = oauth2.create_access_token(data={"user_id": db_token.user_id})
    
    # 3. Create a brand new refresh token
    new_refresh_token = oauth2.create_refresh_token(db_token.user_id, db)
    
    # 4. Set the new refresh token as cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=7*24*60*60,
        samesite="lax"
    )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "message": "Tokens refreshed successfully"
    }
    
@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token:
        # Revoke it in database
        oauth2.revoke_refresh_token(refresh_token, db)
    
    # Clear the cookie
    response.delete_cookie("refresh_token")
    
    return {"message": "Logged out successfully"}

