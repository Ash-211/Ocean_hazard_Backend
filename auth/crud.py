# auth/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models, schemas, utils
import uuid

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: uuid.UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,  # Explicitly set user as active
        is_verified=False  # Explicitly set user as not verified
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not utils.verify_password(password, user.hashed_password):
        return False
    return user

def create_user_session(db: Session, user_id: uuid.UUID, token: str, expires_at):
    session = models.UserSession(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_user_session(db: Session, token: str):
    return db.query(models.UserSession).filter(models.UserSession.token == token).first()

def delete_user_session(db: Session, token: str):
    session = get_user_session(db, token)
    if session:
        db.delete(session)
        db.commit()
    return session

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user_role(db: Session, user_id: uuid.UUID, role: str):
    user = get_user_by_id(db, user_id)
    if user:
        user.role = role
        db.commit()
        db.refresh(user)
    return user
