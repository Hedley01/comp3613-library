
from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(
        self,
        *,
        user_id: int,
        booking_id: int | None,
        kind: str,
        message: str,
        created_at: str,
    ) -> dict[str, Any]:
        row = Notification(
            user_id=user_id,
            booking_id=booking_id,
            kind=kind,
            message=message,
            created_at=created_at,
        )
        self.session.add(row)
        self.session.flush()
        return row.model_dump()

    def list_for_user(self, user_id: int) -> list[dict[str, Any]]:
        rows = self.session.exec(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.id)
        ).all()
        return [row.model_dump() for row in rows]
