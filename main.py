"""
MZIGO LOGISTICS — BACKEND API
Version: 7.0.0

Features:
- User registration and login
- Secure password hashing
- Hashed, expiring authentication tokens
- Trader and fleet-owner roles
- Persistent SQL database
- Truck listings and search
- Atomic truck-capacity reservation
- Booking history
- Rules-based Zambian corridor price estimates

Run locally:
    pip install fastapi "uvicorn[standard]" sqlalchemy pydantic
    uvicorn main:app --reload

For production:
- Set SECRET_KEY to a long random secret.
- Set DATABASE_URL to a PostgreSQL connection URL.
- Set CORS_ORIGINS to your real frontend origin(s).
- Use HTTPS.
"""

from __future__ import annotations

import os
import re
import hmac
import hashlib
import secrets
import logging

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Header,
    Query,
    status,
)
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index,
    update,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session,
    relationship,
)


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "Mzigo Logistics API"
APP_VERSION = "7.0.0"

APP_ENV = os.getenv("APP_ENV", "development").lower()

SECRET_KEY = os.getenv("SECRET_KEY", "")

if APP_ENV == "production" and len(SECRET_KEY) < 32:
    raise RuntimeError(
        "Production requires SECRET_KEY to contain at least 32 characters."
    )

if not SECRET_KEY:
    if APP_ENV == "production":
        raise RuntimeError("SECRET_KEY is required in production.")
    SECRET_KEY = secrets.token_urlsafe(48)
    logging.warning(
        "Using a temporary development SECRET_KEY. "
        "Existing login tokens will stop working after restart."
    )

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mzigo.db")

TOKEN_TTL_HOURS = int(os.getenv("TOKEN_TTL_HOURS", "24"))

PASSWORD_ITERATIONS = 600_000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mzigo")


# ============================================================
# DATABASE
# ============================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_datetime(value: datetime) -> datetime:
    """
    SQLite may return naive datetimes. Treat those as UTC.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


# ============================================================
# DATABASE MODELS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(120), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)

    password_hash = Column(String(300), nullable=False)

    role = Column(String(30), nullable=False, default="trader")

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now)

    trucks = relationship("Truck", back_populates="owner")
    bookings = relationship("Booking", back_populates="trader")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    token_hash = Column(String(64), unique=True, index=True, nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    revoked = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now)


class Truck(Base):
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    origin = Column(String(100), nullable=False, index=True)
    destination = Column(String(100), nullable=False, index=True)

    truck_type = Column(String(60), nullable=False)

    capacity_tonnes = Column(Float, nullable=False)
    available_tonnes = Column(Float, nullable=False)

    price_zmw = Column(Float, nullable=True)

    departure_date = Column(String(30), nullable=True)

    description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now)

    owner = relationship("User", back_populates="trucks")

    __table_args__ = (
        Index("idx_truck_route", "origin", "destination"),
    )


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    trader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)

    quantity_tonnes = Column(Float, nullable=False)

    status = Column(String(30), default="pending", nullable=False)

    payment_status = Column(
        String(30),
        default="not_paid",
        nullable=False,
    )

    created_at = Column(DateTime(timezone=True), default=utc_now)

    trader = relationship("User", back_populates="bookings")
    truck = relationship("Truck")


Base.metadata.create_all(bind=engine)


# ============================================================
# SECURITY
# ============================================================

def normalize_phone(phone: str) -> str:
    """
    Normalizes common Zambian mobile numbers to 260XXXXXXXXX.

    Accepted examples:
        0971234567
        971234567
        260971234567
        +260971234567
    """
    digits = re.sub(r"\D", "", phone)

    if digits.startswith("0"):
        digits = "260" + digits[1:]

    if len(digits) == 9:
        digits = "260" + digits

    if not re.fullmatch(r"260[0-9]{9}", digits):
        raise ValueError(
            "Enter a valid Zambian phone number, e.g. 0971234567."
        )

    return digits


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )

    return (
        f"pbkdf2_sha256${PASSWORD_ITERATIONS}"
        f"${salt.hex()}${digest.hex()}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        calculated = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )

        return hmac.compare_digest(
            calculated.hex(),
            digest_hex,
        )

    except (ValueError, TypeError):
        return False


def create_access_token(db: Session, user_id: int) -> str:
    raw_token = secrets.token_urlsafe(48)

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    token = AuthToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=utc_now() + timedelta(hours=TOKEN_TTL_HOURS),
    )

    db.add(token)
    db.commit()

    return raw_token


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    scheme, separator, raw_token = authorization.partition(" ")

    if not separator or scheme.lower() != "bearer" or not raw_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header.",
        )

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    token = (
        db.query(AuthToken)
        .filter(
            AuthToken.token_hash == token_hash,
            AuthToken.revoked.is_(False),
        )
        .first()
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or revoked token.",
        )

    if normalize_datetime(token.expires_at) <= utc_now():
        token.revoked = True
        db.commit()

        raise HTTPException(
            status_code=401,
            detail="Your session has expired. Please log in again.",
        )

    user = (
        db.query(User)
        .filter(
            User.id == token.user_id,
            User.is_active.is_(True),
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Account is unavailable.",
        )

    return user


def require_role(*allowed_roles: str):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return role_checker


# ============================================================
# INPUT SCHEMAS
# ============================================================

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=9, max_length=20)
    password: str = Field(min_length=10, max_length=128)
    role: str = Field(default="trader")

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, value):
        value = " ".join(value.strip().split())

        if len(value) < 2:
            raise ValueError("Enter your full name.")

        return value

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value):
        return normalize_phone(value)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        value = value.strip().lower()

        if value not in {"trader", "fleet_owner"}:
            raise ValueError("Role must be trader or fleet_owner.")

        return value


class LoginRequest(BaseModel):
    phone: str
    password: str = Field(min_length=1, max_length=128)

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value):
        return normalize_phone(value)


class TruckCreateRequest(BaseModel):
    origin: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)

    truck_type: str = Field(min_length=2, max_length=60)

    capacity_tonnes: float = Field(gt=0, le=1000)
    available_tonnes: float = Field(gt=0, le=1000)

    price_zmw: Optional[float] = Field(default=None, gt=0)

    departure_date: Optional[str] = Field(default=None, max_length=30)

    description: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("origin", "destination", "truck_type")
    @classmethod
    def clean_text(cls, value):
        return " ".join(value.strip().split())

    @field_validator("available_tonnes")
    @classmethod
    def validate_available_capacity(cls, value, info):
        capacity = info.data.get("capacity_tonnes")

        if capacity is not None and value > capacity:
            raise ValueError(
                "Available tonnes cannot exceed total truck capacity."
            )

        return value


class BookingCreateRequest(BaseModel):
    truck_id: int = Field(gt=0)
    quantity_tonnes: float = Field(gt=0, le=1000)


class EstimateRequest(BaseModel):
    origin: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)

    truck_type: str = Field(default="general", max_length=60)

    load_tonnes: float = Field(default=10, gt=0, le=1000)

    @field_validator("origin", "destination", "truck_type")
    @classmethod
    def clean_text(cls, value):
        return " ".join(value.strip().split())


# ============================================================
# API INITIALIZATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Freight matching API for connecting traders "
        "with available transport capacity."
    ),
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:5500",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ============================================================
# GENERAL ROUTES
# ============================================================

@app.get("/")
def root():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "index.html")
    )


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "mzigo-api",
        "version": APP_VERSION,
        "timestamp": utc_now().isoformat(),
    }


# ============================================================
# AUTHENTICATION
# ============================================================

@app.post("/api/auth/register", status_code=201)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(User)
        .filter(User.phone == payload.phone)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="An account with this phone number already exists.",
        )

    user = User(
        full_name=payload.full_name,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        logger.exception("Registration failed.")
        raise HTTPException(
            status_code=500,
            detail="Could not create account.",
        )

    return {
        "message": "Account created successfully.",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role,
        },
    }


@app.post("/api/auth/login")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.phone == payload.phone)
        .first()
    )

    if (
        not user
        or not verify_password(payload.password, user.password_hash)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect phone number or password.",
        )

    token = create_access_token(db, user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_TTL_HOURS * 3600,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role,
        },
    }


@app.post("/api/auth/logout")
def logout(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    if not authorization:
        return {"message": "Already logged out."}

    scheme, separator, raw_token = authorization.partition(" ")

    if not separator or scheme.lower() != "bearer" or not raw_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header.",
        )

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    token = (
        db.query(AuthToken)
        .filter(AuthToken.token_hash == token_hash)
        .first()
    )

    if token:
        token.revoked = True
        db.commit()

    return {"message": "Logged out successfully."}


@app.get("/api/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }


# ============================================================
# TRUCK LISTINGS
# ============================================================

@app.get("/api/trucks")
def list_trucks(
    origin: Optional[str] = Query(default=None, max_length=100),
    destination: Optional[str] = Query(default=None, max_length=100),
    truck_type: Optional[str] = Query(default=None, max_length=60),
    min_tonnes: Optional[float] = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Truck).filter(
        Truck.is_active.is_(True),
        Truck.available_tonnes > 0,
    )

    if origin:
        query = query.filter(
            Truck.origin.ilike(f"%{origin.strip()}%")
        )

    if destination:
        query = query.filter(
            Truck.destination.ilike(f"%{destination.strip()}%")
        )

    if truck_type:
        query = query.filter(
            Truck.truck_type.ilike(f"%{truck_type.strip()}%")
        )

    if min_tonnes is not None:
        query = query.filter(
            Truck.available_tonnes >= min_tonnes
        )

    trucks = (
        query.order_by(Truck.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "count": len(trucks),
        "trucks": [
            {
                "id": truck.id,
                "origin": truck.origin,
                "destination": truck.destination,
                "truck_type": truck.truck_type,
                "capacity_tonnes": truck.capacity_tonnes,
                "available_tonnes": truck.available_tonnes,
                "price_zmw": truck.price_zmw,
                "departure_date": truck.departure_date,
                "description": truck.description,
                "created_at": truck.created_at,
            }
            for truck in trucks
        ],
    }


@app.post("/api/trucks", status_code=201)
def create_truck(
    payload: TruckCreateRequest,
    current_user: User = Depends(
        require_role("fleet_owner")
    ),
    db: Session = Depends(get_db),
):
    if payload.origin.casefold() == payload.destination.casefold():
        raise HTTPException(
            status_code=422,
            detail="Origin and destination cannot be the same.",
        )

    truck = Truck(
        owner_id=current_user.id,
        origin=payload.origin,
        destination=payload.destination,
        truck_type=payload.truck_type,
        capacity_tonnes=payload.capacity_tonnes,
        available_tonnes=payload.available_tonnes,
        price_zmw=payload.price_zmw,
        departure_date=payload.departure_date,
        description=payload.description,
    )

    db.add(truck)

    try:
        db.commit()
        db.refresh(truck)
    except Exception:
        db.rollback()
        logger.exception("Truck creation failed.")
        raise HTTPException(
            status_code=500,
            detail="Could not publish truck listing.",
        )

    return {
        "message": "Truck published successfully.",
        "truck_id": truck.id,
    }


@app.get("/api/trucks/{truck_id}")
def get_truck(
    truck_id: int,
    db: Session = Depends(get_db),
):
    truck = (
        db.query(Truck)
        .filter(
            Truck.id == truck_id,
            Truck.is_active.is_(True),
        )
        .first()
    )

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck listing not found.",
        )

    return {
        "id": truck.id,
        "origin": truck.origin,
        "destination": truck.destination,
        "truck_type": truck.truck_type,
        "capacity_tonnes": truck.capacity_tonnes,
        "available_tonnes": truck.available_tonnes,
        "price_zmw": truck.price_zmw,
        "departure_date": truck.departure_date,
        "description": truck.description,
    }


@app.delete("/api/trucks/{truck_id}")
def deactivate_truck(
    truck_id: int,
    current_user: User = Depends(
        require_role("fleet_owner")
    ),
    db: Session = Depends(get_db),
):
    truck = (
        db.query(Truck)
        .filter(
            Truck.id == truck_id,
            Truck.owner_id == current_user.id,
        )
        .first()
    )

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck listing not found.",
        )

    truck.is_active = False
    db.commit()

    return {"message": "Truck listing deactivated."}


# ============================================================
# BOOKINGS
# ============================================================

@app.post("/api/bookings", status_code=201)
def create_booking(
    payload: BookingCreateRequest,
    current_user: User = Depends(
        require_role("trader")
    ),
    db: Session = Depends(get_db),
):
    truck = (
        db.query(Truck)
        .filter(
            Truck.id == payload.truck_id,
            Truck.is_active.is_(True),
        )
        .first()
    )

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck listing not found or inactive.",
        )

    if payload.quantity_tonnes > truck.available_tonnes:
        raise HTTPException(
            status_code=409,
            detail="Not enough truck capacity is available.",
        )

    try:
        # Conditional update prevents two concurrent bookings
        # from reserving the same remaining capacity.
        result = db.execute(
            update(Truck)
            .where(
                Truck.id == truck.id,
                Truck.is_active.is_(True),
                Truck.available_tonnes >= payload.quantity_tonnes,
            )
            .values(
                available_tonnes=(
                    Truck.available_tonnes - payload.quantity_tonnes
                )
            )
        )

        if result.rowcount != 1:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Capacity has changed. Refresh and try again.",
            )

        booking = Booking(
            trader_id=current_user.id,
            truck_id=truck.id,
            quantity_tonnes=payload.quantity_tonnes,
            status="pending",
            payment_status="not_paid",
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Booking creation failed.")
        raise HTTPException(
            status_code=500,
            detail="Could not create booking.",
        )

    return {
        "message": "Booking request created.",
        "booking": {
            "id": booking.id,
            "truck_id": booking.truck_id,
            "quantity_tonnes": booking.quantity_tonnes,
            "status": booking.status,
            "payment_status": booking.payment_status,
        },
    }


@app.get("/api/bookings")
def list_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "trader":
        query = db.query(Booking).filter(
            Booking.trader_id == current_user.id
        )
    elif current_user.role == "fleet_owner":
        query = (
            db.query(Booking)
            .join(Truck, Booking.truck_id == Truck.id)
            .filter(Truck.owner_id == current_user.id)
        )
    else:
        return {"count": 0, "bookings": []}

    bookings = query.order_by(
        Booking.created_at.desc()
    ).all()

    return {
        "count": len(bookings),
        "bookings": [
            {
                "id": booking.id,
                "truck_id": booking.truck_id,
                "quantity_tonnes": booking.quantity_tonnes,
                "status": booking.status,
                "payment_status": booking.payment_status,
                "created_at": booking.created_at,
            }
            for booking in bookings
        ],
    }


# ============================================================
# PRICE ESTIMATOR
# ============================================================

# Approximate one-way road distances in kilometres.
# These are planning assumptions, not live navigation distances.
CORRIDOR_DISTANCES_KM = {
    ("lusaka", "ndola"): 320,
    ("lusaka", "kitwe"): 362,
    ("ndola", "kitwe"): 60,
    ("lusaka", "livingstone"): 485,
    ("lusaka", "chipata"): 575,
    ("lusaka", "solwezi"): 575,
    ("ndola", "solwezi"): 430,
    ("kitwe", "solwezi"): 400,
    ("lusaka", "chingola"): 360,
    ("lusaka", "mongu"): 590,
    ("lusaka", "kabwe"): 140,
    ("lusaka", "kapiri mposhi"): 210,
}

DIESEL_PRICE_ZMW_PER_LITRE = float(
    os.getenv("DIESEL_PRICE_ZMW_PER_LITRE", "30")
)

FUEL_CONSUMPTION_L_PER_KM = float(
    os.getenv("FUEL_CONSUMPTION_L_PER_KM", "0.32")
)

OPERATING_COST_ZMW_PER_KM = float(
    os.getenv("OPERATING_COST_ZMW_PER_KM", "18")
)

AVERAGE_SPEED_KMH = float(
    os.getenv("AVERAGE_SPEED_KMH", "55")
)

CONTINGENCY_RATE = float(
    os.getenv("CONTINGENCY_RATE", "0.12")
)

PROFIT_MARGIN = float(
    os.getenv("PROFIT_MARGIN", "0.15")
)


def estimate_freight_price(
    origin: str,
    destination: str,
    load_tonnes: float,
):
    origin_key = origin.strip().casefold()
    destination_key = destination.strip().casefold()

    reverse_route = False

    distance = CORRIDOR_DISTANCES_KM.get(
        (origin_key, destination_key)
    )

    if distance is None:
        distance = CORRIDOR_DISTANCES_KM.get(
            (destination_key, origin_key)
        )
        reverse_route = distance is not None

    if distance is None:
        raise ValueError(
            "This route is not yet in the estimator's corridor database."
        )

    # These are initial planning assumptions.
    # The load factor is deliberately capped to avoid extreme estimates.
    load_factor = min(max(load_tonnes / 10.0, 0.5), 3.0)

    fuel_litres = distance * FUEL_CONSUMPTION_L_PER_KM

    fuel_cost = fuel_litres * DIESEL_PRICE_ZMW_PER_LITRE

    operating_cost = distance * OPERATING_COST_ZMW_PER_KM

    base_cost = (fuel_cost + operating_cost) * load_factor

    contingency = base_cost * CONTINGENCY_RATE

    subtotal = base_cost + contingency

    suggested_price = subtotal * (1 + PROFIT_MARGIN)

    travel_hours = distance / AVERAGE_SPEED_KMH

    return {
        "origin": origin,
        "destination": destination,
        "distance_km": distance,
        "reverse_route_used": reverse_route,
        "load_tonnes": load_tonnes,
        "estimated_price_zmw": round(suggested_price, 2),
        "estimated_fuel_litres": round(fuel_litres, 2),
        "estimated_fuel_cost_zmw": round(fuel_cost, 2),
        "estimated_travel_hours": round(travel_hours, 1),
        "assumptions": {
            "diesel_price_zmw_per_litre": DIESEL_PRICE_ZMW_PER_LITRE,
            "fuel_consumption_l_per_km": FUEL_CONSUMPTION_L_PER_KM,
            "operating_cost_zmw_per_km": OPERATING_COST_ZMW_PER_KM,
            "average_speed_kmh": AVERAGE_SPEED_KMH,
            "contingency_rate": CONTINGENCY_RATE,
            "profit_margin": PROFIT_MARGIN,
        },
        "disclaimer": (
            "This is a preliminary rules-based estimate, not a live quote. "
            "It does not account for every truck type, toll, loading fee, "
            "empty return, cargo risk, road condition or negotiated rate. "
            "Validate the assumptions against actual carrier costs."
        ),
    }


@app.post("/api/ai/estimate")
def estimate_price(payload: EstimateRequest):
    """
    This is a rules-based estimator, not a machine-learning AI model.
    """
    try:
        result = estimate_freight_price(
            origin=payload.origin,
            destination=payload.destination,
            load_tonnes=payload.load_tonnes,
        )

        result["truck_type"] = payload.truck_type

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():
    logger.info(
        "%s version %s is starting in %s mode.",
        APP_NAME,
        APP_VERSION,
        APP_ENV,
    )


# ============================================================
# MZIGO COMMAND CENTRE — ADMIN INTEGRATION
# ============================================================

from admin_routes import create_admin_router

app.include_router(
    create_admin_router(
        User=User,
        Truck=Truck,
        Booking=Booking,
        get_db=get_db,
        get_current_user=get_current_user,
    )
)


@app.get("/admin", include_in_schema=False)
def admin_dashboard():
    return FileResponse(
        os.path.join(
            os.path.dirname(__file__),
            "admin.html"
        )
    )




    

