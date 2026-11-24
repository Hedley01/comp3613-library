
from typing import Optional

from sqlmodel import Field, SQLModel

class ConflictRecord(SQLModel, table=True):
    """Audit entry: which rule resolved a conflict and whether an override occurred."""

    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(index=True)
    preferred_date: str = Field(index=True)
    subject_booking_id: int
    outcome: str  # "accepted" or "rejected"
    rule_applied: str
    override_used: int = 0
    competing_ids: str = ""
    displaced_ids: str = ""
    reason: str
    decided_by: int
    created_at: str
