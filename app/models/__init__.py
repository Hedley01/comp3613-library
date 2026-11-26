
"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.booking import Booking
from app.models.conflict_record import ConflictRecord
from app.models.notification import Notification
from app.models.room import Room
from app.models.setting import PolicySetting
from app.models.user import User

__all__ = [
    "User",
    "Room",
    "Booking",
    "ConflictRecord",
    "Notification",
    "PolicySetting",
]
