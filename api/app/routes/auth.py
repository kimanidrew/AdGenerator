from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import AuthInput, SignupInput, TokenOutput
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup", response_model=TokenOutput, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupInput, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(email=email, password_hash=hash_password(payload.password), ai_training_consent=payload.allow_ai_training, ai_training_consent_at=datetime.now(timezone.utc) if payload.allow_ai_training else None)
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOutput(access_token=create_access_token(str(user.id)), user=user)

@router.post("/login", response_model=TokenOutput)
def login(payload: AuthInput, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return TokenOutput(access_token=create_access_token(str(user.id)), user=user)
