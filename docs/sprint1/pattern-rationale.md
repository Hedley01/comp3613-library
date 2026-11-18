# Pattern Rationale: Same-Slot Conflict Resolution

## Special feature

Same-slot conflict resolution (R4): when two lecturers request the same room and date, the system decides who gets the slot.

## What stakeholders need

- INT-1 (Administrator): priority is based on the course or workshop's needs, not strictly first come, first served. Preferences can be adjusted in busy periods such as exams, if the coordinator and administrator agree.
- INT-3 (Coordinator): the earlier request wins by default, but the coordinator can override for a later request from a larger group if the room can hold it. They want the system to recommend a winner while they keep the final say.
- INT-1 and INT-3: no overbooking, and the losing lecturer must be told why.
- Starter acceptance criteria (docs/ACCEPTANCE.md, items 7 to 9): default capacity 30, the earlier request wins unless the coordinator explicitly overrides for a larger cohort, and the system records which request won and whether an override occurred.
- Together, the rule differs between stakeholders and changes over time (A4, R4, R9).

## Inherited weakness

In `app/services/conflicts.py`, `resolve_slot_request()` decides every same-slot clash in one function of nested conditionals that mixes a capacity check, an earlier-request-wins rule and a larger-cohort override. It returns a plain dict. `app/services/bookings.py` calls it from both `request_booking()` and `coordinator_override_accept()`.

Defects against the requirements:

- The rule is hard-coded in one function (conflicts.py lines 28 to 127), so R4 and R9 cannot be met without editing it.
- Capacity is checked against the incoming headcount alone, not the total already booked, so a room can be overbooked (25 booked plus 10 incoming is accepted in a 30-seat room). Nothing locks the slot against simultaneous requests (R3, NFR2).
- "Earlier wins" is inverted (the latest booking is treated as the winner), a larger cohort displaces an existing booking without a coordinator override, and cancelled bookings still count.
- Override-accept ignores a "reject" verdict and does not check the booking's current status (bookings.py lines 127 to 170).
- No notification exists. A displaced booking silently becomes "rejected", keeps its confirmation code, and no reason is stored (R5).

## Pattern identified: Strategy

The part that varies is the rule for choosing a winner among requests for one slot. Strategy puts each rule behind one interface. The booking code asks "who wins?" without knowing which rule is active, and the rule can be switched at run time (R9) without editing the booking code.

ASSIGNMENT.md names Strategy as a strong fit and asks teams to defend any alternative. We chose it because of the interview evidence above, and we compared it with the alternatives below.

| Participant | Role |
|---|---|
| ConflictResolutionStrategy | Interface: `resolve(incoming, existing, room, override_requested)` returns a Resolution (decision, displaced ids, rule applied, override flag, reason) |
| CapacityGuard | Checks the total headcount on the slot against room capacity (default 30) before any strategy runs |
| EarlierRequestWins | Default: the earliest active request keeps the slot |
| LargerCohortOverride | Used only when the coordinator explicitly requests an override, the incoming cohort is larger and the room can hold it |
| CoursePriority | Optional third strategy from INT-1 |
| ConflictPolicy | Stores which strategy is active. The administrator changes it (R9) |
| BookingService (context) | Runs the guard, asks the strategy, applies the decision and saves the Resolution (R10 to R12) |
| BookingRepository | New: loads and saves bookings, as the layered architecture requires |
| NotificationService | Tells the losing lecturer the outcome and the reason (R5, R16) |

## Alternatives considered

| Option | Why not chosen |
|---|---|
| Keep one function and add flags (the inherited approach) | Every new rule means editing the same function, and rules cannot be tested in isolation |
| Chain of Responsibility | Fits an ordered sequence of checks, but stakeholders described whole alternative policies chosen per period |
| Template Method | The rule would be fixed at compile time by subclassing, but it needs to be switched by configuration at run time |
| State | Models a booking's lifecycle (pending, accepted, cancelled), not how a winner is chosen |

## Sprint 2 change outline

1. Extract the clash decision from `resolve_slot_request()` in `app/services/conflicts.py` into `ConflictResolutionStrategy`, and add a `BookingRepository` so `bookings.py` stops querying the database directly.
2. Implement `CapacityGuard`, `EarlierRequestWins` and `LargerCohortOverride`, each returning a Resolution with the rule applied and a reason.
3. Add `ConflictPolicy` as a stored setting, with an administrator action to switch the active strategy.
4. Route `request_booking()` and `coordinator_override_accept()` through `BookingService`, and make override-accept respect a reject decision.
5. Store the Resolution on the booking (accepted request, displaced requests, rule, override flag) and invalidate confirmation codes for displaced and cancelled bookings.
6. Notify the losing lecturer with the reason.
7. Test each strategy, that switching the policy changes the outcome for the same two requests, that capacity is never exceeded, and that simultaneous same-slot requests never both confirm.

## Open questions

- **Shared or exclusive slot (A8):** the starter's own defect notes say capacity should count the total already booked, so we assume a slot (room and date) can be shared up to capacity, and a conflict occurs when a new request would exceed it. Acceptance item 8 can also be read as one booking per slot. To confirm with the coordinator.
- **Course ranking:** INT-1 does not define how courses are ranked for `CoursePriority`, so Sprint 2 ships the other two strategies first.
