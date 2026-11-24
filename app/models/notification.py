
from typing import Optional

from sqlmodel import Field, SQLModel

class Notification(SQLModel, table=True):
    """A message shown to a lecturer inside the system."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    booking_id: Optional[int] = None
    kind: str
    message: str
    created_at: str
