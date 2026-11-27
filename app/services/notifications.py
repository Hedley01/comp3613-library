"""In-system notifications for lecturers (requirements R5, R7, R15, R16).

Plain Python: the store is any object with ``add`` and ``list_for_user``, so the
messages can be tested without a database.
"""

from __future__ import annotations

from typing import Any, Protocol


class NotificationStore(Protocol):
    def add(
        self,
        *,
        user_id: int,
        booking_id: int | None,
        kind: str,
        message: str,
        created_at: str,
    ) -> dict[str, Any]: ...

    def list_for_user(self, user_id: int) -> list[dict[str, Any]]: ...


def _describe(booking: dict[str, Any], room_name: str) -> str:
    return (
        f"{room_name} on {booking['preferred_date']} "
        f"({booking['headcount']} students, {booking['course_code']})"
    )


class NotificationService:
    """Builds the message for each outcome and stores it for the lecturer."""

    def __init__(self, store: NotificationStore) -> None:
        self._store = store

    def send(
        self,
        user_id: int,
        booking_id: int | None,
        kind: str,
        message: str,
        created_at: str,
    ) -> dict[str, Any]:
        return self._store.add(
            user_id=user_id,
            booking_id=booking_id,
            kind=kind,
            message=message,
            created_at=created_at,
        )

    def list_for_user(self, user_id: int) -> list[dict[str, Any]]:
        return self._store.list_for_user(user_id)

    # ---- message builders -------------------------------------------------

    @staticmethod
    def confirmed_message(booking: dict[str, Any], room_name: str) -> str:
        return (
            f"Your booking for {_describe(booking, room_name)} is confirmed. "
            f"Confirmation code: {booking.get('confirmation_code')}."
        )

    @staticmethod
    def rejected_message(
        booking: dict[str, Any],
        room_name: str,
        reason: str,
        capacity: int,
        occupied: int,
        alternatives: list[str],
        alternative_dates: list[str] | None = None,
    ) -> str:
        parts = [
            f"Your request for {_describe(booking, room_name)} was not confirmed. "
            f"Reason: {reason}. The room holds {capacity} and {occupied} places "
            "are already booked."
        ]
        if alternatives:
            parts.append("Rooms with space that day: " + ", ".join(alternatives) + ".")
        else:
            parts.append("No other room has space that day.")
        if alternative_dates:
            parts.append(
                "Dates with space in this room: " + ", ".join(alternative_dates) + "."
            )
        elif not alternatives:
            parts.append("Please try another date.")
        return " ".join(parts)
    
    @staticmethod
    def displaced_message(booking: dict[str, Any], room_name: str, reason: str) -> str:
        return (
            f"Your booking for {_describe(booking, room_name)} was released. "
            f"Reason: {reason}. Please resubmit for another time or a reduced headcount."
        )

    @staticmethod
    def cancelled_message(
        booking: dict[str, Any],
        room_name: str,
        role: str,
        reason: str | None = None,
        alternatives: list[str] | None = None,
    ) -> str:
        text = f"Your booking for {_describe(booking, room_name)} was cancelled by the {role}."
        if reason:
            text += f" Reason: {reason}."
        if alternatives:
            text += " Rooms with space that day: " + ", ".join(alternatives) + "."
        else:
            text += " Please book another room or date if you still need one."
        return text
