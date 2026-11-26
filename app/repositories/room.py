
from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.models.room import Room


class RoomRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, room_id: int, lock: bool = False) -> dict[str, Any] | None:
        """Load a room. ``lock=True`` takes a row lock on databases that support it."""
        stmt = select(Room).where(Room.id == room_id)
        if lock:
            stmt = stmt.with_for_update()
        row = self.session.exec(stmt).first()
        return row.model_dump() if row else None

    def list(self) -> list[dict[str, Any]]:
        rows = self.session.exec(select(Room).order_by(Room.id)).all()
        return [row.model_dump() for row in rows]

    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        row = Room(**data)
        self.session.add(row)
        self.session.flush()
        return row.model_dump()

    def update(self, room_id: int, **fields: Any) -> dict[str, Any] | None:
        row = self.session.get(Room, room_id)
        if row is None:
            return None
        for key, value in fields.items():
            setattr(row, key, value)
        self.session.add(row)
        self.session.flush()
        return row.model_dump()
