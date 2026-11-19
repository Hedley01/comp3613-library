# Starter Repository Audit — Library Workshop Booking

**Project:** COMP3613 Software Engineering  
**Starter version:** 0.2.0  
**Repository:** `comp3613-library`  
**Audit date:** 18 November 2026

## 1. Purpose

This audit examines the starter repository's workshop booking functionality, with particular attention to booking creation, same-room and same-date conflicts, room capacity, cancellation, confirmation handling, and notifications.

The purpose is to identify existing behaviour and defects before implementing the required design improvements.

## 2. Booking creation workflow

The booking workflow follows the existing architecture:

1. `app/routers/library.py` receives the booking request through `POST /api/bookings`.
2. The route calls `request_booking()` in `app/services/bookings.py`.
3. The booking service retrieves the room and existing bookings for the requested room and date.
4. The service calls `resolve_slot_request()` in `app/services/conflicts.py`.
5. The service creates and saves the booking based on the resolver's decision.

**Relevant locations:**
- `app/routers/library.py`, lines 56–70 — booking API endpoint.
- `app/services/bookings.py`, lines 47–94 — booking creation and conflict resolution call.
- `app/services/conflicts.py`, lines 28–118 — conflict-resolution logic.

## 3. Same-slot conflict handling

The conflict-resolution logic is centralised in `app/services/conflicts.py`. The booking service calls this resolver for both ordinary booking requests and coordinator overrides.

However, several defects were identified:

- **Aggregate capacity is not checked:** The resolver compares the incoming headcount against room capacity without adding the headcounts of existing bookings.
- **First-come-first-served logic is reversed:** Existing bookings are sorted by `created_at`, but the resolver selects the last entry as the champion. This favours the newest existing booking rather than the earliest.
- **Larger-cohort override is automatic:** A larger incoming cohort can displace an existing booking even when a coordinator override was not requested.
- **Conflicting bookings can coexist:** When the incoming headcount is equal to or smaller than the selected existing booking's headcount, the resolver can accept the new booking alongside it.
- **Cancelled bookings remain in the active conflict list:** The resolver includes `cancelled` alongside `accepted` and `pending` bookings.

**Relevant locations:**
- `app/services/conflicts.py`, lines 53–69 — individual headcount capacity check.
- Lines 73–75 — active booking statuses include cancelled bookings.
- Lines 87–95 — champion selection and larger-cohort handling.
- Lines 107–118 — coexistence and fallback decisions.

The conflict logic is implemented procedurally using nested conditionals. The starter code comments identify Strategy or composed policies as an intended improvement.

## 4. Room capacity handling

The application defines a default room capacity of 30.

The `room_capacity()` function returns this default when the room or its capacity is missing.

**Relevant locations:**
- `app/services/conflicts.py`, line 16 — `DEFAULT_CAPACITY = 30`.
- Lines 19–25 — default capacity handling.

The individual capacity check works for a single incoming request. However, the resolver does not calculate total occupancy across existing bookings, allowing aggregate overbooking.

## 5. Runtime testing

Runtime testing was performed using the local application through the OpenAPI interface at `/docs`.

The seeded lecturer account was used:
- Account: `lecturer1@example.com`
- User ID: `3`
- Role: Lecturer

### Test 1 — First booking for a room and date

**Request:**
- Room: Workshop A (ID 1)
- Date: 2099-03-16
- Course: TEST1001
- Headcount: 20

**Result:** HTTP 200 — booking accepted.

The booking was assigned ID 2 and received confirmation code `CONF-D46236E0`.

### Test 2 — Second booking for the same room and date

**Request:**
- Room: Workshop A (ID 1)
- Date: 2099-03-16
- Course: TEST1002
- Headcount: 20

**Result:** HTTP 200 — booking accepted.

The resolver returned:

`"decision": "accept"`  
`"reason": "coexist on slot"`

Both bookings were accepted, resulting in a combined headcount of 40 for a room with capacity 30.

**Finding:** Aggregate room capacity is not enforced. This is a confirmed runtime defect.

### Test 3 — Single booking exceeding room capacity

**Request:**
- Room: Workshop A (ID 1)
- Date: 2099-03-17
- Course: TEST1003
- Headcount: 31

**Result:** HTTP 400 — request rejected.

Response:

`{"detail": "exceeds room capacity"}`

**Finding:** The individual capacity check correctly rejects a single request exceeding the room's capacity. This does not prevent aggregate overbooking.

## 6. Cancellation and confirmation handling

The cancellation service changes a booking's status to `cancelled` but does not clear its confirmation code.

The confirmation lookup retrieves bookings using their confirmation code and does not check whether the booking has been cancelled or rejected.

Consequently, a cancelled or rejected booking may still be returned as a valid confirmation.

**Relevant locations:**
- `app/services/bookings.py`, lines 173–191 — cancellation logic.
- Lines 186–188 — cancellation status update without clearing confirmation code.
- Lines 194–202 — confirmation lookup and return behaviour.

The booking service also marks displaced bookings as rejected without clearing their confirmation codes (lines 99–104).

## 7. Validation and approval observations

The booking service checks that headcount is positive, but its implementation does not adequately validate all required booking information.

The service allows empty course codes and resources to pass through, despite the acceptance criteria requiring these details.

**Relevant locations:**
- `app/services/bookings.py`, lines 60–62 — incomplete validation.
- Lines 109–118 — booking creation.

Additionally, ordinary booking requests are immediately assigned the `accepted` status rather than being held for coordinator review (lines 106–107). This should be reviewed against the stakeholder requirement that the coordinator manages booking approvals.

## 8. Notifications

A source search was performed within the `app` directory for notification and email-related functionality, including:

- `notification`
- `notify`
- `send_mail`
- `send_email`
- `SMTP`
- `EmailMessage`

No matches were returned.

**Finding:** No notification or email implementation was identified in the application source search. The application therefore requires further work to support the requested in-system notifications and communication about booking outcomes.

## 9. Duplication and architecture

The search across Python files under `app` identified one central conflict-resolution implementation in `app/services/conflicts.py`.

The booking service calls this resolver for both ordinary booking requests and coordinator overrides.

The decision logic is therefore centralised rather than implemented as multiple separate conflict-resolution functions. However, the resolver itself combines several policies in one procedural function, making it difficult to maintain and extend.

A Strategy-based or composed-policy design would allow capacity checks, first-come-first-served decisions, and coordinator overrides to be separated.

## 10. Summary of findings

| Area | Finding |
|---|---|
| Booking creation | Implemented through the API and service layer |
| Individual capacity | Working in runtime test |
| Aggregate capacity | Defective; overbooking confirmed |
| First-come-first-served | Logic favours the newest existing booking |
| Coordinator override | Larger-cohort displacement can occur automatically |
| Cancelled bookings | Still included in conflict calculations |
| Confirmation handling | Cancelled/rejected confirmations may remain accessible |
| Required field validation | Incomplete |
| Coordinator approval | Ordinary requests are immediately accepted |
| Notifications | No implementation found in the `app` source search |
| Conflict logic | Centralised, but combines multiple policies procedurally |

## 11. Conclusion

The starter repository provides a working foundation for workshop booking, including API endpoints, room and booking models, a booking service, and a central conflict resolver.

However, the audit identified significant defects in conflict resolution, aggregate room capacity, booking cancellation, confirmation validity, and validation. Runtime testing confirmed that two bookings of 20 students can both be accepted for a room with a capacity of 30, while a single booking of 31 students is correctly rejected.

These findings provide a baseline for the upcoming refactoring work. The conflict-resolution logic should be redesigned using separate policies, and the booking workflow should enforce capacity, approval, cancellation, confirmation, and notification requirements.