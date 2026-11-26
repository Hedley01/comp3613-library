
from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.models.booking import Booking


class BookingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, booking_id: int) -> dict[str, Any] | None:
        row = self.session.get(Booking, booking_id)
        return row.model_dump() if row else None

    def get_by_confirmation_code(self, code: str) -> dict[str, Any] | None:
        row = self.session.exec(
            select(Booking).where(Booking.confirmation_code == code)
        ).first()
        return row.model_dump() if row else None

    def list(
        self, *, room_id: int | None = None, date: str | None = None
    ) -> list[dict[str, Any]]:
        stmt = select(Booking)
        if room_id is not None:
            stmt = stmt.where(Booking.room_id == room_id)
        if date is not None:
            stmt = stmt.where(Booking.preferred_date == date)
        rows = self.session.exec(stmt.order_by(Booking.id)).all()
        return [row.model_dump() for row in rows]

    def list_for_slot(
        self, room_id: int, date: str, exclude_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Every booking (any status) for one room on one date."""
        stmt = select(Booking).where(
            Booking.room_id == room_id, Booking.preferred_date == date
        )
        if exclude_id is not None:
            stmt = stmt.where(Booking.id != exclude_id)
        rows = self.session.exec(stmt.order_by(Booking.id)).all()
        return [row.model_dump() for row in rows]

    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        row = Booking(**data)
        self.session.add(row)
        self.session.flush()
        return row.model_dump()

    def update(self, booking_id: int, **fields: Any) -> dict[str, Any] | None:
        row = self.session.get(Booking, booking_id)
        if row is None:
            return None
        for key, value in fields.items():
            setattr(row, key, value)
        self.session.add(row)
        self.session.flush()
        return row.model_dump()
