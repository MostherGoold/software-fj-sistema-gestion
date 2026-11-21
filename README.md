# Software FJ - Integrated Management System for Clients, Services and Reservations

Academic project for the Programming course (UNAD), Phase 4 - Simulated practices. Group 53.

## Description

Object-oriented system (Python) that manages clients, services and reservations for Software FJ, a company offering room reservations, equipment rental and specialized advisory services. No database is used; management is done with objects and in-memory lists. Files are used only for event and error logging.

## Features

- Abstract base class `Entity` for general entities.
- `Client` class with robust validations and encapsulation.
- Abstract `Service` class with three specialized services: `RoomReservationService`, `EquipmentRentalService`, `SpecializedAdvisoryService` (polymorphism and overridden methods).
- `Reservation` class integrating client, service, duration and status (confirm, cancel, process).
- Overloaded cost calculation methods (tax, discount, optional parameters, single dispatch).
- Custom exceptions, try/except, try/except/else, try/except/finally and exception chaining.
- File-based logging of all events and errors.
- 20 complete simulations (valid and invalid cases) with the system staying running after each failure.

## Project structure

```
software-fj/
  src/
    entities.py
    client.py
    service.py
    reservation.py
    system.py
    exceptions.py
    logger.py
  main.py
  tests/
  logs/
  README.md
```

## Requirements

- Python 3.10+

## Run

```bash
python3 main.py
```

The log file is generated at `logs/system.log`.

## Author

- Elias Jose Iguaran Marquez (MostherGoold)

## Repository

https://github.com/MostherGoold/software-fj-sistema-gestion
