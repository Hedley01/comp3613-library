# Library Workshop Booking System — Sprint 1 Notes

## Actors

- **Lecturer** — Submits workshop booking requests and uses the system to check availability and status, receive booking outcomes, revise requests, and cancel bookings. (Acceptance criteria 1, 5, and 6; status and revision details are from the additional lecturer instructions.)
- **Library Coordinator** — Manages availability, capacity, and conflict outcomes; reviews and resolves conflicts and approves or rejects requests. (Acceptance criteria 2 and 8–9 support management and conflict resolution; approval/rejection: Additional lecturer instruction — no explicit requirement ID provided.)
- **Library Administrator** — May support coordinator operations; the specific administrator interactions shown here come from the additional lecturer instructions. (Acceptance criterion 3.)

## Use Cases

- **View Room Availability — Lets the lecturer check whether a room is available. (Additional scenario context — no numbered acceptance criterion.)
- **Submit Booking Request** — Lets the lecturer submit a workshop booking request with the required details. (Acceptance criterion 1.)
- **View Booking Status** — Lets the lecturer check the status of a booking request. (Additional lecturer instruction — no explicit requirement ID provided.)
- **Receive Confirmation** — Provides the lecturer a shareable confirmation for an accepted booking. (Acceptance criterion 5.)
- **Receive Rejection Notice with Reason** — Lets the lecturer receive the reason for a rejected request. (Acceptance criterion 4 for incomplete requests; broader notice behavior: Additional lecturer instruction — no explicit requirement ID provided.)
- **Resubmit with Another Time or Reduced Headcount** — Lets the lecturer submit a revised request with another time or a smaller headcount. (Additional lecturer instruction — no explicit requirement ID provided.)
- **Cancel Booking** — Lets the lecturer cancel a booking when a class is moved, or lets the coordinator handle an operational cancellation. (Acceptance criterion 6; coordinator operational cancellation is in the original scenario context, without a numbered criterion.)
- **Review Conflicting Requests** — Lets the coordinator review requests competing for the same room and date. (Acceptance criteria 2 and 8.)
- **Resolve Slot Conflict** — Lets the coordinator resolve same-room/date requests, normally favoring the earlier request, with an explicit larger-cohort override when capacity permits. (Acceptance criteria 7–9.)
- **Approve or Reject Request** — Lets the coordinator approve or reject a booking request. (Additional lecturer instruction — no explicit requirement ID provided.)
- **Manage Room Availability** — Lets the coordinator manage workshop room availability. (Acceptance criterion 2.)
- **Configure Rooms and Capacities** — Lets the administrator configure workshop rooms and their capacities. (Additional lecturer instruction — no explicit requirement ID provided.)
- **Set Conflict Preference** — Lets the administrator set the conflict preference. (Additional lecturer instruction — no explicit requirement ID provided.)
- **Handle Capacity Disputes** — Lets the administrator handle capacity disputes. (Additional lecturer instruction — no explicit requirement ID provided.)
