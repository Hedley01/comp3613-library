# Class Diagram: Inherited vs Proposed

Both diagrams show the same-slot conflict resolution feature (R4). The proposed design uses the Strategy pattern, as justified in pattern-rationale.md.

## Inherited structure

```mermaid
classDiagram
    direction LR

    class LibraryRouter {
        <<module>>
        +login(body)
        +rooms()
        +list_all(room_id, date)
        +create_booking(body, x_user_id)
        +override_accept(booking_id, x_user_id)
        +cancel(booking_id, x_user_id)
        +confirmation(code)
        -_actor_id(x_user_id)
    }
    class bookings {
        <<module>>
        +list_rooms()
        +list_bookings(room_id, date)
        +request_booking(lecturer_id, room_id, course_code, headcount, preferred_date, resources)
        +coordinator_override_accept(coordinator_id, booking_id)
        +cancel_booking(actor_id, booking_id)
        +get_confirmation(code)
    }
    class conflicts {
        <<module>>
        +room_capacity(room)
        +resolve_slot_request(incoming, existing, room, coordinator_override)
    }
    class library_auth {
        <<module>>
        +login(email, password)
        +get_user(user_id)
        +public_user(user)
    }
    class Booking {
        +int id
        +int lecturer_id
        +int room_id
        +str course_code
        +int headcount
        +str preferred_date
        +str resources
        +str status
        +int override_used
        +str confirmation_code
        +str created_at
    }
    class Room {
        +int id
        +str name
        +int capacity
    }
    class User {
        +int id
        +str username
        +str email
        +str password
        +str role
        +str display_name
    }

    LibraryRouter --> bookings : calls
    LibraryRouter --> library_auth : calls
    bookings --> conflicts : calls resolve_slot_request with plain dicts
    bookings --> library_auth : calls get_user
    bookings ..> Booking : queries the database directly
    bookings ..> Room : queries the database directly
    library_auth ..> User : queries the database directly
    Booking ..> Room : room_id, no foreign key
    Booking ..> User : lecturer_id, no foreign key
```


Weaknesses visible here: the whole conflict rule sits in one function in `conflicts`, `bookings` talks to the database directly (only users have a repository, and it is not used on this path), and decisions travel as plain dicts.

## Proposed design (Strategy)

```mermaid
classDiagram
    direction LR

    class LibraryRouter
    class BookingService {
        +request_booking(lecturer_id, room_id, course_code, headcount, preferred_date, resources)
        +coordinator_override_accept(coordinator_id, booking_id)
        +cancel_booking(actor_id, booking_id)
    }
    class BookingRepository {
        +get(booking_id)
        +list_for_slot(room_id, date)
        +save(booking)
    }
    class RoomRepository {
        +get(room_id)
        +list_rooms()
    }
    class CapacityGuard {
        +check(incoming, existing, room)
    }
    class ConflictPolicy {
        -active_strategy
        +get_active()
        +set_active(name)
    }
    class ConflictResolutionStrategy {
        <<interface>>
        +resolve(incoming, existing, room, override_requested) Resolution
    }
    class EarlierRequestWins
    class LargerCohortOverride
    class CoursePriority {
        <<optional>>
    }
    class Resolution {
        +decision
        +displaced_ids
        +rule
        +override_used
        +reason
    }
    class NotificationService {
        +notify_displaced(booking, resolution)
    }
    class Booking
    class Room

    LibraryRouter --> BookingService : calls
    BookingService --> BookingRepository : loads and saves bookings
    BookingService --> RoomRepository : loads rooms
    BookingService --> CapacityGuard : checks capacity first
    BookingService --> ConflictPolicy : asks for the active strategy
    BookingService --> NotificationService : notifies the losing lecturer
    ConflictPolicy o-- ConflictResolutionStrategy : active strategy
    ConflictResolutionStrategy <|.. EarlierRequestWins
    ConflictResolutionStrategy <|.. LargerCohortOverride
    ConflictResolutionStrategy <|.. CoursePriority
    ConflictResolutionStrategy ..> Resolution : returns
    BookingRepository ..> Booking
    RoomRepository ..> Room
```


## How the inherited code maps to the design

| Inherited | Proposed |
|---|---|
| `resolve_slot_request()`, one function with nested conditionals | `ConflictResolutionStrategy` with `EarlierRequestWins` and `LargerCohortOverride`. The capacity check moves to `CapacityGuard` |
| Module functions in `bookings.py` | `BookingService` class |
| Direct database queries in `bookings.py` | `BookingRepository` and `RoomRepository` |
| Plain dict verdict | `Resolution` |
| Nothing | `ConflictPolicy` (R9) and `NotificationService` (R5) |
| `Booking`, `Room`, `User` models | Unchanged, except `Booking` gains fields to store the Resolution |
