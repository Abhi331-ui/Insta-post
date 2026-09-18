from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
import jwt
import bcrypt

from backend.config import settings
from backend.database import get_db
from backend.models.user import User, BrandSetting, ContentPillar

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


class UserRegisterRequest(BaseModel):
    email: str
    password: str
    brand_name: Optional[str] = "PromptPulse"


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        plain_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Require a valid JWT for every request. Dev-only bootstrap is allowed only in development."""
    if credentials and credentials.credentials:
        token = credentials.credentials
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user:
                    return user
        except Exception:
            pass

    if settings.ENVIRONMENT == "development":
        primary_user = db.query(User).first()

        if not primary_user:
            primary_user = User(
                email="admin@promptpulse.ai",
                hashed_password=hash_password("promptpulse2025"),
            )
            db.add(primary_user)
            db.commit()
            db.refresh(primary_user)

            brand = BrandSetting(
                user_id=primary_user.id,
                brand_name="PromptPulse",
                primary_color="#7C3AED",
                background_color="#000000",
                text_color="#FFFFFF",
                secondary_color="#D1D5DB",
                auto_mode_enabled=False,
                posting_time="09:00",
            )
            db.add(brand)

            pillars = [
                ContentPillar(
                    user_id=primary_user.id,
                    name="AI Workflows & Automation",
                    percentage=40,
                    description="Practical pipelines that eliminate repetitive friction",
                ),
                ContentPillar(
                    user_id=primary_user.id,
                    name="New Model & Tool Launches",
                    percentage=30,
                    description="Breaking releases and zero-day product capabilities",
                ),
                ContentPillar(
                    user_id=primary_user.id,
                    name="Developer & Engineering Tools",
                    percentage=20,
                    description="In-browser compilers, multi-file code agents, and CLIs",
                ),
                ContentPillar(
                    user_id=primary_user.id,
                    name="Productivity Experiments",
                    percentage=10,
                    description="Real benchmarks and time-saved comparisons",
                ),
            ]

            db.add_all(pillars)
            db.commit()

        return primary_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
    )


@router.post("/register", response_model=TokenResponse)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize brand settings
    brand = BrandSetting(
        user_id=user.id,
        brand_name=req.brand_name or "PromptPulse",
        primary_color="#2563EB",
        background_color="#F8FAFC",
        text_color="#0F172A",
        secondary_color="#64748B",
        auto_mode_enabled=False,
    )
    db.add(brand)
    db.commit()

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }


@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }
