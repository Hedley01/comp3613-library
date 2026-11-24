
from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.models.conflict_record import ConflictRecord
from app.models.setting import PolicySetting

POLICY_KEY = "conflict_policy"


class ConflictRecordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        row = ConflictRecord(**data)
        self.session.add(row)
        self.session.flush()
        return row.model_dump()

    def list(
        self, *, room_id: int | None = None, date: str | None = None
    ) -> list[dict[str, Any]]:
        stmt = select(ConflictRecord)
        if room_id is not None:
            stmt = stmt.where(ConflictRecord.room_id == room_id)
        if date is not None:
            stmt = stmt.where(ConflictRecord.preferred_date == date)
        rows = self.session.exec(stmt.order_by(ConflictRecord.id)).all()
        return [row.model_dump() for row in rows]


class PolicySettingRepository:
    """Persists the active conflict policy name (the ConflictPolicy store)."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_policy(self) -> str | None:
        row = self.session.get(PolicySetting, POLICY_KEY)
        return row.value if row else None

    def set_policy(self, name: str) -> None:
        row = self.session.get(PolicySetting, POLICY_KEY)
        if row is None:
            row = PolicySetting(key=POLICY_KEY, value=name)
        else:
            row.value = name
        self.session.add(row)
        self.session.flush()
