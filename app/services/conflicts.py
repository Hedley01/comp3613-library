"""
Same-slot conflict resolution using the Strategy pattern.

Vocabulary (see docs/sprint1/requirements.md, assumption A8):

A slot is a room on a date.
Several bookings may share a slot while their combined headcount stays within
the room's capacity.
A conflict happens when confirming a request would push the slot above
that capacity. Resolving it means deciding who keeps the places.

Participants (see docs/sprint2/class-diagram.md):

CapacityGuard               runs before any strategy
ConflictResolutionStrategy  the interface every rule implements
EarlierRequestWins          default rule: earlier bookings keep the slot
LargerCohortOverride        a larger cohort takes the places of smaller ones
ConflictPolicy              remembers which strategy is active
Resolution                  the value a strategy returns

This module is plain Python on purpose: no database or web imports, so every
rule can be unit-tested in isolation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

DEFAULT_CAPACITY = 30
ACTIVE_STATUSES = frozenset({"accepted", "pending"})
DEFAULT_POLICY = "earlier_wins"


def room_capacity(room: dict[str, Any] | None) -> int:
    """Capacity of a room, falling back to the default of 30."""
    if room is None:
        return DEFAULT_CAPACITY
    capacity = room.get("capacity")
    if capacity is None:
        return DEFAULT_CAPACITY
    return int(capacity)


def _booked_order(booking: dict[str, Any]) -> tuple[str, int]:
    """Sort key that orders bookings from earliest to latest."""
    return (booking.get("created_at") or "", int(booking.get("id") or 0))


@dataclass(frozen=True)
class Resolution:
    """The outcome of resolving one request against one slot."""

    decision: str  # "accept" or "reject"
    rule: str  # which rule produced the decision
    reason: str  # human-readable explanation, reused in notifications
    override_used: bool = False  # True only when a coordinator explicitly overrode
    displace_ids: tuple[int, ...] = ()  # existing bookings that lose their places
    conflict: bool = False  # True when the slot could not hold everyone

    @property
    def accepted(self) -> bool:
        return self.decision == "accept"

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "override_used": self.override_used,
            "displace_ids": list(self.displace_ids),
            "reason": self.reason,
            "rule": self.rule,
            "conflict": self.conflict,
        }


class CapacityGuard:
    """Capacity checks that run before any strategy is consulted."""

    def capacity(self, room: dict[str, Any] | None) -> int:
        return room_capacity(room)

    def active(self, existing: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Bookings that hold places. Cancelled and rejected bookings never count."""
        return [b for b in existing if b.get("status") in ACTIVE_STATUSES]

    def occupied(self, existing: list[dict[str, Any]]) -> int:
        return sum(int(b["headcount"]) for b in self.active(existing))

    def exceeds_room(self, incoming: dict[str, Any], room: dict[str, Any] | None) -> bool:
        """True when the request could never fit, even in an empty room."""
        return int(incoming["headcount"]) > self.capacity(room)

    def fits(
        self,
        incoming: dict[str, Any],
        existing: list[dict[str, Any]],
        room: dict[str, Any] | None,
    ) -> bool:
        """True when the request fits alongside the bookings already on the slot."""
        total = self.occupied(existing) + int(incoming["headcount"])
        return total <= self.capacity(room)


class ConflictResolutionStrategy(ABC):
    """Interface for a rule that picks winners when a slot cannot hold everyone.

    ``resolve`` is called only after ``CapacityGuard`` has found a conflict.
    ``override_requested`` is True when a coordinator explicitly asked for an
    override of the normal rule.
    """

    name: str = ""

    @abstractmethod
    def resolve(
        self,
        incoming: dict[str, Any],
        existing: list[dict[str, Any]],
        room: dict[str, Any] | None,
        override_requested: bool = False,
    ) -> Resolution:
        raise NotImplementedError


class LargerCohortOverride(ConflictResolutionStrategy):
    """A larger cohort takes the places of strictly smaller cohorts when overridden.

    Requires an explicit coordinator override (``override_requested=True``).
    When approved, it displaces as few bookings as possible: the largest smaller
    cohort first, and among equal sizes the most recently booked first, so earlier
    bookings are protected. If displacing every smaller cohort still leaves the
    slot over capacity, the request is rejected and nothing changes.
    """

    name = "larger_cohort"

    def resolve(
        self,
        incoming: dict[str, Any],
        existing: list[dict[str, Any]],
        room: dict[str, Any] | None,
        override_requested: bool = False,
    ) -> Resolution:
        guard = CapacityGuard()
        capacity = guard.capacity(room)
        wanted = int(incoming["headcount"])
        active = guard.active(existing)
        missing = guard.occupied(existing) + wanted - capacity

        if missing <= 0:
            return Resolution("accept", self.name, "room has capacity for this request")

        if not override_requested:
            return Resolution(
                "reject",
                self.name,
                f"coordinator override required for larger cohort of {wanted} "
                f"students when slot is full ({guard.occupied(existing)}/{capacity} occupied)",
                override_used=False,
                conflict=True,
            )

        smaller = [b for b in active if int(b["headcount"]) < wanted]
        smaller.sort(key=_booked_order, reverse=True)  # latest booked first
        smaller.sort(key=lambda b: -int(b["headcount"]))  # then largest first (stable)

        displaced: list[int] = []
        freed = 0
        for booking in smaller:
            if freed >= missing:
                break
            displaced.append(int(booking["id"]))
            freed += int(booking["headcount"])

        if freed < missing:
            if not smaller:
                reason = (
                    f"no booking on this slot is smaller than {wanted} students, "
                    "so none can be displaced"
                )
            else:
                reason = (
                    f"cannot make room for {wanted} students: bookings smaller than "
                    f"this request free only {freed} of the {missing} places needed"
                )
            return Resolution("reject", self.name, reason, conflict=True)

        return Resolution(
            "accept",
            self.name,
            f"larger cohort of {wanted} students takes the places of "
            f"{len(displaced)} smaller booking(s)",
            override_used=True,
            displace_ids=tuple(displaced),
            conflict=True,
        )


class EarlierRequestWins(ConflictResolutionStrategy):
    """Default rule: bookings that already hold places keep them.

    A coordinator can still override explicitly. The override is evaluated by
    ``LargerCohortOverride``, so it only succeeds for a larger cohort.
    """

    name = "earlier_wins"

    def resolve(
        self,
        incoming: dict[str, Any],
        existing: list[dict[str, Any]],
        room: dict[str, Any] | None,
        override_requested: bool = False,
    ) -> Resolution:
        if override_requested:
            return LargerCohortOverride().resolve(incoming, existing, room, True)
        guard = CapacityGuard()
        return Resolution(
            "reject",
            self.name,
            f"slot is full: {guard.occupied(existing)} of {guard.capacity(room)} "
            "places are already booked by earlier requests",
            conflict=True,
        )


STRATEGIES: dict[str, type[ConflictResolutionStrategy]] = {
    EarlierRequestWins.name: EarlierRequestWins,
    LargerCohortOverride.name: LargerCohortOverride,
}


class PolicyStore(Protocol):
    """Where the active policy name is persisted."""

    def get_policy(self) -> str | None: ...

    def set_policy(self, name: str) -> None: ...


class ConflictPolicy:
    """Remembers which strategy is active. The administrator can change it."""

    def __init__(self, store: PolicyStore | None = None) -> None:
        self._store = store
        self._name = DEFAULT_POLICY

    def available(self) -> list[str]:
        return sorted(STRATEGIES)

    def get_active_name(self) -> str:
        name = self._store.get_policy() if self._store else self._name
        return name if name in STRATEGIES else DEFAULT_POLICY

    def get_active(self) -> ConflictResolutionStrategy:
        return STRATEGIES[self.get_active_name()]()

    def set_active(self, name: str) -> None:
        if name not in STRATEGIES:
            raise ValueError(
                f"unknown policy '{name}'; choose one of: {', '.join(self.available())}"
            )
        if self._store:
            self._store.set_policy(name)
        else:
            self._name = name


def decide(
    *,
    incoming: dict[str, Any],
    existing: list[dict[str, Any]],
    room: dict[str, Any] | None,
    strategy: ConflictResolutionStrategy,
    guard: CapacityGuard | None = None,
    override_requested: bool = False,
) -> Resolution:
    """Run the guard, then ask the strategy only if the slot cannot hold everyone."""
    guard = guard or CapacityGuard()
    wanted = int(incoming["headcount"])
    if guard.exceeds_room(incoming, room):
        return Resolution(
            "reject",
            "capacity_guard",
            f"exceeds room capacity ({wanted} students, capacity {guard.capacity(room)})",
        )
    if guard.fits(incoming, existing, room):
        return Resolution("accept", "capacity_guard", "room has capacity for this request")
    return strategy.resolve(incoming, existing, room, override_requested)


def resolve_slot_request(
    *,
    incoming: dict[str, Any],
    existing: list[dict[str, Any]],
    room: dict[str, Any] | None,
    coordinator_override: bool = False,
    strategy: ConflictResolutionStrategy | None = None,
) -> dict[str, Any]:
    """Backwards-compatible entry point that returns the verdict as a dict."""
    resolution = decide(
        incoming=incoming,
        existing=existing,
        room=room,
        strategy=strategy or EarlierRequestWins(),
        override_requested=coordinator_override,
    )
    return resolution.to_dict()
