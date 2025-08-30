# auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import uuid

from database import get_db
from . import schemas, crud, utils
from .utils import create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = crud.get_user_by_id(db, uuid.UUID(user_id))
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: schemas.UserResponse = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Store session in database
    expires_at = datetime.utcnow() + access_token_expires
    crud.create_user_session(db, user.id, access_token, expires_at)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    crud.delete_user_session(db, token)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: schemas.UserResponse = Depends(get_current_active_user)):
    return current_user

@router.get("/users", response_model=List[schemas.UserResponse])
def read_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_active_user)
):
    if current_user.role not in ["official", "analyst"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users = crud.get_all_users(db, skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}/role", response_model=schemas.UserResponse)
def update_user_role(
    user_id: str,
    role: str,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_active_user)
):
    if current_user.role != "analyst":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = crud.update_user_role(db, uuid.UUID(user_id), role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
