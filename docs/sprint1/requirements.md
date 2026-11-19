# Requirements: Library Workshop Booking

**Scenario:** 2 - Library, lecturer workshop booking
**Special feature:** Same-slot conflict resolution (R4)

## Interview sources

| ID | Stakeholder | Date | Status |
|---|---|---|---|
| INT-1 | Library Administrator (swen: Library Workshop Booking interview) | 15 Nov 2026 | Done |
| INT-2 | Lecturer (swen) | 18 Nov 2026 | Done |
| INT-3 | Library Coordinator (swen) | 18 Nov 2026 | Done |

Exploratory interviews (Job Board x2, UWI Connect, 15 Nov 2026) were used to compare scenarios and are not cited below.

Other sources: AC n is item n of the starter's docs/ACCEPTANCE.md, and CODE is our reading of the starter code.

## Definitions

- **Slot:** a room at a given date and time slot. The starter stores a date only, so until a time slot is added, a slot is a room on a date (A9).
- **Conflict:** a request that cannot be confirmed because confirming it would push the total headcount of confirmed bookings for that slot above the room's capacity (A8).

## Facts from INT-1 (Library Administrator)

- Configures workshop rooms and capacities and handles disputes about capacity policies.
- Lecturers currently book by email, and the library coordinator decides clashes using "conflict preferences".
- Preferences are typically based on the course or the workshop's needs, not strictly first come, first served.
- Preferences can be adjusted in busy periods such as exams, if the coordinator and administrator agree.
- A losing lecturer must get a clear notification with the reason, then picks another time or reduces headcount.
- Overbooking is not allowed. The system would be rejected if it allowed overbooking or did not enforce capacity rules.

## Facts from INT-2 (Lecturer)

- Requests include the course code, number of students and any specific resources needed.
- Requests go to the library coordinator for review. Once approved, the lecturer gets a confirmation to share with students.
- A lecturer can cancel any time before the workshop starts.
- Pain points: finding available slots, waiting for approval, and back and forth.
- Conflicts are discovered only after submitting, then the lecturer scrambles for another time.
- Wants to see before submitting: available dates and times, which rooms are free, room capacities and existing bookings.
- Wants status of all requests in one place and in-system notifications of approvals, rejections and cancellations.
- Would like a calendar view of their bookings, reminders for upcoming workshops, and a way to message the coordinator in the system.

## Facts from INT-3 (Library Coordinator)

- Reviews requests, checks they fit room capacities and schedules, approves or denies, and issues confirmations.
- When two classes want the same slot, the earlier request gets priority. The coordinator can override this if the later request is for a larger group that the room can hold without exceeding capacity.
- If the later request cannot be approved because of capacity, the lecturer must reduce headcount or pick a different time.
- Conflicts are handled manually today, mainly by checking room capacity and class sizes.
- Wants the system to identify conflicting requests automatically, show room capacity next to class sizes, and recommend which request gets priority, while keeping the final say.
- Decisions are emailed today. Wants notifications to include the reason, the room capacity, the number of students in the conflicting request and suggested alternative slots. Wants them sent automatically, with the option to review before sending.
- Lecturers can cancel confirmed bookings any time before the session. The coordinator can cancel for operational reasons and wants affected people notified automatically with details and alternatives.
- Pain point: the volume of emails. Wants a simple online request form, a calendar view of all bookings and a history of requests and cancellations.

## Requirements

| ID | Requirement | Priority | Source | Acceptance note |
|---|---|---|---|---|
| R1 | A lecturer can submit a workshop booking request online (course code, number of students, room, date, time slot, specific resources needed) | Must | INT-1, INT-2, INT-3, AC1 (A5, A7, A9) | The request is saved and visible to the coordinator for review |
| R2 | The system never confirms a booking when the total headcount of confirmed bookings for that room and slot would exceed the room's capacity (double booking prevented) | Must | INT-1, INT-3, AC7 (A8) | With 25 confirmed in a 30-seat room, a request for 10 is not confirmed |
| R3 | The system enforces room capacity: a single request above the room's capacity is never confirmed, and a room with no capacity set defaults to 30 | Must | INT-1, INT-3, AC7 | A request for 31 in a 30-seat room is rejected, and a room with no capacity set accepts up to 30 |
| R4 (SPECIAL FEATURE) | When requests for the same room and slot cannot all fit within the room's capacity, the system resolves the conflict using a configurable conflict rule (for example earliest request first, larger group wins only on explicit coordinator override if the room can hold it, priority by course or workshop needs), not one hard-coded rule | Must | INT-1, INT-3, AC8 (A4) | The same two competing requests give different outcomes under different configured rules, and confirmed bookings for a slot never exceed the room's capacity |
| R5 | A lecturer who loses a slot is notified of the decision with the reason | Must | INT-1, INT-2, INT-3 | The notification names the slot, the outcome and the reason |
| R6 | The administrator can configure workshop rooms and their capacities | Must | INT-1 | A capacity change applies to the next booking check |
| R7 | A lecturer receives a confirmation when a request is approved | Must | INT-2, INT-3 | A confirmation is shown after approval |
| R8 | A lecturer who loses a slot can resubmit for another time or a reduced headcount | Should | INT-1, INT-3 | The resubmission goes through the same checks as a new request |
| R9 | The conflict rule can be changed for busy periods such as exams, with coordinator and administrator agreement | Should | INT-1 (A2) | The active rule can be switched without changing code |
| R10 (supports special feature) | The coordinator sees conflicting requests together, with room capacity and the number of students in each | Must | INT-3 | Two requests that cannot both fit in one room and slot appear together with capacity and student numbers |
| R11 (supports special feature) | The system recommends which conflicting request should win under the active rule, and the coordinator can accept or override it | Should | INT-3 | The coordinator's final decision is the one applied |
| R12 | The coordinator approves or denies each request | Must | INT-2, INT-3 | A request stays pending until the coordinator decides |
| R13 | A lecturer can see room availability, capacities and existing bookings before submitting a request | Should | INT-2 | Free and booked rooms for a chosen date and time are visible before submitting |
| R14 | A lecturer can see the status of all their requests in one place | Must | INT-2, INT-3 | Pending, approved, rejected and cancelled requests are listed |
| R15 | Affected lecturers are notified automatically when a booking is cancelled, with the reason and suggested alternatives where possible | Should | INT-2, INT-3 (A6) | A cancellation creates a notification for each affected lecturer |
| R16 | Rejection notifications include the room capacity, the number of students in the conflicting request and suggested alternative slots | Should | INT-3 | A rejection notification shows those details |
| R17 | The coordinator can review a notification before it is sent | Could | INT-3 | A notification can be held for review, then released |
| R18 | A lecturer can cancel a booking any time before the workshop starts, and the coordinator can cancel for operational reasons | Should | INT-2, INT-3 | A cancelled booking frees its slot |
| R19 | A calendar view of bookings (own bookings for lecturers, all bookings for the coordinator) | Could | INT-2, INT-3 | Bookings show on a calendar by date |
| R20 | A lecturer can set reminders for upcoming workshops | Could | INT-2 | A reminder is shown before the workshop |
| R21 | A lecturer and the coordinator can exchange messages inside the system | Could | INT-2 | A message sent by one appears for the other |
| R22 | The system keeps a history of requests, changes and cancellations | Could | INT-3 | The history lists each request with its changes and decisions |
| R23 | Incomplete requests (missing course code, date, resources or a non-positive headcount) are rejected with clear feedback | Must | AC4, CODE | Each missing field gives a specific error message and nothing is saved |
| R24 | A cancelled or rejected booking no longer works as a confirmation and no longer counts toward its slot's capacity | Must | AC5, AC6, CODE | After cancelling, the confirmation lookup no longer returns it as valid and the freed capacity can be booked |
| R25 | Conflict resolution records which request was accepted, which were displaced, the rule applied and whether an override occurred | Must | AC9, CODE | After a conflict, the stored booking shows the rule, the displaced requests and the override flag |
| NFR1 | Lecturers can submit requests and see outcomes without staff help | Must | INT-1, INT-2, INT-3 | A first-time lecturer submits a request unaided |
| NFR2 | Booking checks stay correct when requests arrive at the same time | Must | INT-1, CODE (A3) | Two simultaneous requests that together exceed a slot's capacity are never both confirmed |
| NFR3 | Every action is tied to a verified identity: a user cannot act as another user or role by supplying that user's ID | Should | CODE | A request carrying another user's ID without valid credentials is refused |
| NFR4 | Passwords are stored hashed and login responses never contain password material | Must | AC10 | A stored password is a hash, and the login response has no password field |

## Assumptions and open issues

- **A2:** The conflict rule can be changed inside the system without a code change. INT-1 says preferences are adjusted in busy periods but not how, so we assume a stored setting that the administrator can change (R9).
- **A3:** "Reliable" means two simultaneous requests can never together push a slot above its capacity. This is our reading of INT-1. Confirm in the starter audit.
- **A4 (discrepancy):** INT-1 says priority is based on course or workshop needs, not strictly first come, first served. INT-3 says the earlier request wins, with a coordinator override for a larger group. We treat the rule as variable, so R4 requires a configurable rule instead of choosing one.
- **A5 (discrepancy):** INT-1 and INT-3 describe booking by email today, while INT-2 describes an online request form. All three want online submission, so R1 is unaffected.
- **A6:** INT-3 mentions notifying students affected by a cancellation. We assume students are not system users and the lecturer passes on confirmations (INT-2), so only lecturers are notified.
- **A7:** "Specific resources" in a request is a free-text field, not a managed inventory, and it is required (AC4). INT-2 does not say more.
- **A8 (design decision):** A slot can be shared by several bookings up to the room's capacity, and a conflict occurs only when a new request would exceed it. We chose this because the starter's defect notes say capacity should count the total already booked, and INT-3 describes asking lecturers to reduce headcount instead of refusing the slot outright. AC8 can also be read as one booking per slot. If that reading is adopted, R2, R4 and NFR2 simplify to "at most one confirmed booking per slot".
- **A9:** The starter stores a date only (AC1), but INT-2 and INT-3 talk about times and slots, so R1 asks for a time slot. If Sprint 2 does not add one, the date is the slot and the gap is recorded in the final report.

## Starter audit

R23 to R25, NFR3 and NFR4 come from the starter's acceptance criteria and code. Further defects from the audit are added as new rows.
