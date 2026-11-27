"""Unit tests for the Strategy layer (app/services/conflicts.py).

These cover the special feature: same-slot conflict resolution. They need no
database. A room holds 30 unless stated otherwise.
"""

from app.services.conflicts import (
    ACTIVE_STATUSES,
    CapacityGuard,
    ConflictPolicy,
    ConflictResolutionStrategy,
    EarlierRequestWins,
    LargerCohortOverride,
    Resolution,
    STRATEGIES,
    decide,
    resolve_slot_request,
    room_capacity,
)

ROOM = {"id": 1, "name": "Workshop A", "capacity": 30}


def booking(id, headcount, created_at, status="accepted"):
    return {"id": id, "headcount": headcount, "created_at": created_at, "status": status}


def incoming(headcount, created_at="t9"):
    return {"headcount": headcount, "created_at": created_at}


def run(strategy, new, existing, override=False, room=ROOM):
    return decide(
        incoming=new, existing=existing, room=room, strategy=strategy,
        override_requested=override,
    )


# ---- capacity -------------------------------------------------------------


def test_room_capacity_defaults_to_30():
    assert room_capacity(None) == 30
    assert room_capacity({"capacity": None}) == 30
    assert room_capacity({"capacity": 12}) == 12


def test_guard_ignores_cancelled_and_rejected_bookings():
    guard = CapacityGuard()
    existing = [
        booking(1, 10, "t1"),
        booking(2, 20, "t2", "cancelled"),
        booking(3, 20, "t3", "rejected"),
    ]
    assert guard.occupied(existing) == 10
    assert guard.fits(incoming(20), existing, ROOM)


def test_guard_counts_total_headcount_not_just_the_request():
    guard = CapacityGuard()
    existing = [booking(1, 25, "t1")]
    assert not guard.fits(incoming(10), existing, ROOM)  # 35 > 30
    assert guard.fits(incoming(5), existing, ROOM)  # exactly 30


def test_request_larger_than_room_is_always_rejected_even_with_override():
    for override in (False, True):
        result = run(EarlierRequestWins(), incoming(31), [], override=override)
        assert result.decision == "reject"
        assert result.rule == "capacity_guard"
        assert not result.conflict


def test_no_soft_capacity_stretch_for_overrides():
    # The starter accepted up to capacity + 5 under override. It must not.
    result = run(EarlierRequestWins(), incoming(34), [], override=True)
    assert result.decision == "reject"


def test_empty_slot_is_accepted():
    result = run(EarlierRequestWins(), incoming(10), [])
    assert result.accepted and not result.conflict
    assert result.displace_ids == ()


def test_slot_can_be_shared_up_to_capacity():
    result = run(EarlierRequestWins(), incoming(10), [booking(1, 20, "t1")])
    assert result.accepted and not result.conflict


# ---- EarlierRequestWins ---------------------------------------------------


def test_earlier_wins_rejects_overbooking():
    # Starter defect: 25 booked + 10 incoming was accepted in a 30 seat room.
    result = run(EarlierRequestWins(), incoming(10), [booking(1, 25, "t1")])
    assert result.decision == "reject"
    assert result.rule == "earlier_wins"
    assert result.conflict
    assert result.override_used is False
    assert "25 of 30" in result.reason


def test_earlier_wins_keeps_an_equal_sized_earlier_booking():
    result = run(EarlierRequestWins(), incoming(20), [booking(1, 20, "t1")])
    assert result.decision == "reject"


def test_larger_cohort_does_not_win_without_an_explicit_override():
    # Starter defect: a larger cohort displaced the booking automatically.
    result = run(EarlierRequestWins(), incoming(25), [booking(1, 20, "t1")])
    assert result.decision == "reject"
    assert result.displace_ids == ()
    assert result.override_used is False


def test_explicit_override_lets_a_larger_cohort_displace_a_smaller_one():
    result = run(EarlierRequestWins(), incoming(25), [booking(1, 20, "t1")], override=True)
    assert result.accepted
    assert result.displace_ids == (1,)
    assert result.override_used is True
    assert result.rule == "larger_cohort"


def test_override_is_refused_when_the_request_is_not_larger():
    result = run(EarlierRequestWins(), incoming(20), [booking(1, 20, "t1")], override=True)
    assert result.decision == "reject"
    assert result.override_used is False
    assert "smaller" in result.reason


def test_cancelled_booking_never_blocks_the_slot():
    # Starter defect: cancelled bookings still counted.
    existing = [booking(1, 25, "t1", "cancelled")]
    result = run(EarlierRequestWins(), incoming(30), existing)
    assert result.accepted and not result.conflict


# ---- LargerCohortOverride -------------------------------------------------


def test_larger_cohort_displaces_the_fewest_bookings():
    # 10 + 15 = 25 booked. A request for 20 needs 15 places: displacing the 15 is enough.
    existing = [booking(1, 10, "t1"), booking(2, 15, "t2")]
    result = run(LargerCohortOverride(), incoming(20), existing)
    assert result.accepted
    assert result.displace_ids == (2,)


def test_larger_cohort_protects_the_earlier_booking_among_equal_sizes():
    # 10 + 10 + 8 = 28 booked. A request for 12 needs 10 places.
    # Two bookings of 10 tie: the later one (id 2) is displaced, the earlier is kept.
    existing = [booking(1, 10, "t1"), booking(2, 10, "t2"), booking(3, 8, "t3")]
    result = run(LargerCohortOverride(), incoming(12), existing)
    assert result.accepted
    assert result.displace_ids == (2,)


def test_larger_cohort_never_displaces_an_equal_or_larger_booking():
    existing = [booking(1, 25, "t1")]
    result = run(LargerCohortOverride(), incoming(25), existing)
    assert result.decision == "reject"
    assert result.displace_ids == ()


def test_larger_cohort_rejects_when_displacing_smaller_bookings_is_not_enough():
    # 20 + 8 = 28 booked. A request for 12 needs 10 places, but only the 8 is
    # smaller than 12 and it frees just 8, so nothing is displaced.
    existing = [booking(1, 20, "t1"), booking(2, 8, "t2")]
    result = run(LargerCohortOverride(), incoming(12), existing)
    assert result.decision == "reject"
    assert result.displace_ids == ()


def test_policy_driven_win_is_not_recorded_as_a_coordinator_override():
    result = run(LargerCohortOverride(), incoming(25), [booking(1, 20, "t1")])
    assert result.accepted
    assert result.override_used is False
    assert result.rule == "larger_cohort"


# ---- the feature: the rule is configurable --------------------------------


def test_same_two_requests_give_different_outcomes_under_different_rules():
    existing = [booking(1, 20, "t1")]
    new = incoming(25)
    earlier = run(EarlierRequestWins(), new, existing)
    larger = run(LargerCohortOverride(), new, existing)
    assert earlier.decision == "reject"
    assert larger.decision == "accept"
    assert larger.displace_ids == (1,)


def test_confirmed_places_never_exceed_capacity_under_any_rule():
    existing = [booking(1, 10, "t1"), booking(2, 15, "t2")]
    for strategy in (EarlierRequestWins(), LargerCohortOverride()):
        for override in (False, True):
            for size in (5, 10, 15, 20, 25, 30):
                result = run(strategy, incoming(size), existing, override=override)
                if result.accepted:
                    kept = [b for b in existing if b["id"] not in result.displace_ids]
                    assert CapacityGuard().occupied(kept) + size <= 30


# ---- policy ---------------------------------------------------------------


class MemoryStore:
    def __init__(self):
        self.name = None

    def get_policy(self):
        return self.name

    def set_policy(self, name):
        self.name = name


def test_policy_defaults_to_earlier_wins():
    policy = ConflictPolicy(MemoryStore())
    assert policy.get_active_name() == "earlier_wins"
    assert isinstance(policy.get_active(), EarlierRequestWins)


def test_policy_can_be_switched_and_is_stored():
    store = MemoryStore()
    policy = ConflictPolicy(store)
    policy.set_active("larger_cohort")
    assert store.name == "larger_cohort"
    assert isinstance(ConflictPolicy(store).get_active(), LargerCohortOverride)


def test_policy_rejects_unknown_names():
    policy = ConflictPolicy(MemoryStore())
    try:
        policy.set_active("coin_flip")
    except ValueError as exc:
        assert "coin_flip" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_policy_ignores_a_stored_name_that_no_longer_exists():
    store = MemoryStore()
    store.name = "removed_rule"
    assert ConflictPolicy(store).get_active_name() == "earlier_wins"


def test_every_registered_strategy_implements_the_interface():
    for name, cls in STRATEGIES.items():
        assert issubclass(cls, ConflictResolutionStrategy)
        assert cls.name == name


# ---- result type and compatibility ----------------------------------------


def test_resolution_to_dict_keeps_the_starter_keys():
    data = Resolution("accept", "r", "why", override_used=True, displace_ids=(3,)).to_dict()
    assert {"decision", "override_used", "displace_ids", "reason"} <= set(data)
    assert data["displace_ids"] == [3]


def test_resolve_slot_request_still_works_with_the_old_signature():
    verdict = resolve_slot_request(
        incoming=incoming(10), existing=[booking(1, 25, "t1")], room=ROOM
    )
    assert verdict["decision"] == "reject"
    verdict = resolve_slot_request(
        incoming=incoming(25), existing=[booking(1, 20, "t1")], room=ROOM,
        coordinator_override=True,
    )
    assert verdict["decision"] == "accept" and verdict["override_used"] is True


def test_active_statuses_are_accepted_and_pending_only():
    assert ACTIVE_STATUSES == {"accepted", "pending"}
