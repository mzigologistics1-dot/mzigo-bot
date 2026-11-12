
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, cast, String
from sqlalchemy.orm import Session


def create_admin_router(
    User, Truck, Booking, get_db, get_current_user
):
    router = APIRouter(
        prefix="/api/admin",
        tags=["admin"]
    )

    def require_admin(
        current_user=Depends(get_current_user)
    ):
        configured = os.getenv("ADMIN_USER_IDS", "")

        if not configured.strip():
            raise HTTPException(
                status_code=503,
                detail="Admin access is not configured."
            )

        try:
            allowed_ids = {
                int(x.strip())
                for x in configured.split(",")
                if x.strip()
            }
        except ValueError:
            raise HTTPException(
                status_code=500,
                detail="Invalid ADMIN_USER_IDS configuration."
            )

        if current_user.id not in allowed_ids:
            raise HTTPException(
                status_code=403,
                detail="Administrator access required."
            )

        return current_user

    @router.get("/me")
    def admin_me(admin=Depends(require_admin)):
        return {
            "id": admin.id,
            "full_name": admin.full_name,
            "phone": admin.phone,
            "role": admin.role
        }

    @router.get("/overview")
    def overview(
        admin=Depends(require_admin),
        db: Session = Depends(get_db)
    ):
        total_users = db.query(
            func.count(User.id)
        ).scalar() or 0

        total_trucks = db.query(
            func.count(Truck.id)
        ).scalar() or 0

        active_trucks = db.query(
            func.count(Truck.id)
        ).filter(
            Truck.is_active.is_(True)
        ).scalar() or 0

        available_trucks = db.query(
            func.count(Truck.id)
        ).filter(
            Truck.is_active.is_(True),
            Truck.available_tonnes > 0
        ).scalar() or 0

        capacity = db.query(
            func.coalesce(
                func.sum(Truck.available_tonnes), 0
            )
        ).filter(
            Truck.is_active.is_(True)
        ).scalar() or 0

        total_bookings = db.query(
            func.count(Booking.id)
        ).scalar() or 0

        pending = db.query(
            func.count(Booking.id)
        ).filter(
            func.lower(Booking.status) == "pending"
        ).scalar() or 0

        delivered = db.query(
            func.count(Booking.id)
        ).filter(
            func.lower(Booking.status) == "delivered"
        ).scalar() or 0

        return {
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "users": {
                "total": total_users
            },

            "fleet": {
                "total": total_trucks,
                "active": active_trucks,
                "available": available_trucks,
                "available_capacity_tonnes": float(capacity)
            },

            "bookings": {
                "total": total_bookings,
                "pending": pending,
                "delivered": delivered
            }
        }

    @router.get("/fleet")
    def fleet(
        q: str = "",
        active: str = Query(
            "all",
            pattern="^(all|active|inactive)$"
        ),
        limit: int = Query(100, ge=1, le=250),
        offset: int = Query(0, ge=0),
        admin=Depends(require_admin),
        db: Session = Depends(get_db)
    ):
        query = db.query(
            Truck, User
        ).join(
            User, Truck.owner_id == User.id
        )

        if active == "active":
            query = query.filter(
                Truck.is_active.is_(True)
            )
        elif active == "inactive":
            query = query.filter(
                Truck.is_active.is_(False)
            )

        if q:
            term = f"%{q.strip()}%"
            query = query.filter(
                Truck.origin.ilike(term)
                | Truck.destination.ilike(term)
                | Truck.truck_type.ilike(term)
                | User.full_name.ilike(term)
            )

        total = query.count()

        records = query.order_by(
            Truck.created_at.desc()
        ).offset(offset).limit(limit).all()

        items = []

        for truck, owner in records:
            items.append({
                "id": truck.id,
                "owner_name": owner.full_name,
                "origin": truck.origin,
                "destination": truck.destination,
                "truck_type": truck.truck_type,
                "capacity_tonnes": truck.capacity_tonnes,
                "available_tonnes": truck.available_tonnes,
                "price_zmw": truck.price_zmw,
                "departure_date": truck.departure_date,
                "is_active": truck.is_active
            })

        return {
            "count": total,
            "items": items
        }

    @router.get("/bookings")
    def bookings(
        q: str = "",
        status: str = "",
        limit: int = Query(100, ge=1, le=250),
        offset: int = Query(0, ge=0),
        admin=Depends(require_admin),
        db: Session = Depends(get_db)
    ):
        query = db.query(
            Booking, Truck, User
        ).join(
            Truck, Booking.truck_id == Truck.id
        ).join(
            User, Booking.trader_id == User.id
        )

        if status:
            query = query.filter(
                Booking.status.ilike(status)
            )

        if q:
            term = f"%{q.strip()}%"
            query = query.filter(
                Truck.origin.ilike(term)
                | Truck.destination.ilike(term)
                | User.full_name.ilike(term)
                | cast(Booking.id, String).ilike(term)
            )

        total = query.count()

        records = query.order_by(
            Booking.created_at.desc()
        ).offset(offset).limit(limit).all()

        items = []

        for booking, truck, trader in records:
            items.append({
                "id": booking.id,
                "trader_name": trader.full_name,
                "truck_id": truck.id,
                "truck_type": truck.truck_type,
                "origin": truck.origin,
                "destination": truck.destination,
                "quantity_tonnes": booking.quantity_tonnes,
                "status": booking.status,
                "payment_status": booking.payment_status
            })

        return {
            "count": total,
            "items": items
        }

    @router.get("/alerts")
    def alerts(
        admin=Depends(require_admin),
        db: Session = Depends(get_db)
    ):
        records = db.query(
            Booking, Truck, User
        ).join(
            Truck, Booking.truck_id == Truck.id
        ).join(
            User, Booking.trader_id == User.id
        ).filter(
            func.lower(Booking.status) == "pending"
        ).limit(50).all()

        return {
            "count": len(records),
            "items": [
                {
                    "id": booking.id,
                    "severity": "warning",
                    "title": f"Booking #{booking.id} awaiting processing",
                    "detail": (
                        f"{trader.full_name}: "
                        f"{truck.origin} to {truck.destination}"
                    )
                }
                for booking, truck, trader in records
            ]
        }

    return router
