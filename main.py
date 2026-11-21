import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.system import SoftwareFJSystem
from src.client import Client
from src.service import (
    RoomReservationService,
    EquipmentRentalService,
    SpecializedAdvisoryService,
)
from src.exceptions import (
    SoftwareFJError,
    InvalidClientError,
    ServiceUnavailableError,
    InvalidReservationError,
    OperationNotAllowedError,
    InvalidServiceParameterError,
    InconsistentCalculationError,
)


def banner(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def run_case(number, description, action):
    banner(f"SIMULATION {number}: {description}")
    try:
        result = action()
    except SoftwareFJError as exc:
        print(f"  [CAUGHT] {exc.code}: {exc.message}")
        if exc.__cause__ is not None:
            print(f"  [CAUSE]  {repr(exc.__cause__)}")
        return None
    except Exception as exc:
        print(f"  [UNEXPECTED] {type(exc).__name__}: {exc}")
        return None
    else:
        print(f"  [OK] Result: {result}")
        return result
    finally:
        print("  [FINALLY] case finished; system still running.")


def main():
    system = SoftwareFJSystem(log_path="logs/system.log")
    print("Software FJ Management System started.")
    print("Log file:", system.logger.path())

    # 1. Valid client registration
    def case1():
        client = system.register_client("Juan Cervantes", "DOC12345", "juan.cervantes@unad.edu.co", "+573001112233")
        return client.describe()

    c1 = run_case(1, "Register valid client", case1)

    # 2. Invalid client registration (bad email)
    def case2():
        system.register_client("Bad Client", "DOC99999", "not-an-email", "+573009998877")
        return "should not reach here"

    run_case(2, "Register invalid client (bad email)", case2)

    # 3. Another valid client
    def case3():
        client = system.register_client("Elias Iguaran", "DOC67890", "iguarankevin53@gmail.com", "+573002223344")
        return client.describe()

    run_case(3, "Register second valid client", case3)

    # 4. Add valid room reservation service
    def case4():
        service = RoomReservationService("Sala A", "Sala de reuniones para 10 personas", 50000.0, capacity=10)
        system.add_service(service)
        return service.describe()

    run_case(4, "Add valid room reservation service", case4)

    # 5. Add invalid service (negative price)
    def case5():
        service = RoomReservationService("Sala Mala", "Sala invalida", -100.0, capacity=5)
        system.add_service(service)
        return "should not reach here"

    run_case(5, "Add invalid service (negative base price)", case5)

    # 6. Add equipment rental service
    def case6():
        service = EquipmentRentalService("Proyector HD", "Proyector de alta definicion", 30000.0, deposit=20000.0)
        system.add_service(service)
        return service.describe()

    run_case(6, "Add equipment rental service", case6)

    # 7. Add specialized advisory service
    def case7():
        service = SpecializedAdvisoryService("Asesoria BD", "Asesoria en bases de datos", 80000.0, expert_level=3)
        system.add_service(service)
        return service.describe()

    run_case(7, "Add specialized advisory service", case7)

    # 8. Create successful reservation
    def case8():
        reservation = system.create_reservation("DOC12345", "Sala A", 3, quantity=1)
        return reservation

    r8 = run_case(8, "Create successful reservation", case8)

    # 9. Reservation with unknown client
    def case9():
        system.create_reservation("DOC00000", "Sala A", 2)
        return "should not reach here"

    run_case(9, "Create reservation with unknown client", case9)

    # 10. Reservation with unavailable service
    def case10():
        service = system.find_service("Proyector HD")
        service.set_available(False)
        try:
            system.create_reservation("DOC67890", "Proyector HD", 2)
            return "should not reach here"
        finally:
            service.set_available(True)

    run_case(10, "Create reservation with unavailable service", case10)

    # 11. Confirm reservation
    def case11():
        if r8 is None:
            raise InvalidReservationError("No reservation to confirm.")
        reservation = system.confirm_reservation(r8.id)
        return reservation

    run_case(11, "Confirm reservation", case11)

    # 12. Process reservation with tax and discount
    def case12():
        if r8 is None:
            raise InvalidReservationError("No reservation to process.")
        cost = system.process_reservation(r8.id, tax_rate=0.19, discount=0.05)
        return f"Processed cost: {cost}"

    run_case(12, "Process reservation with tax and discount", case12)

    # 13. Cancel a reservation then try to process it
    def case13():
        reservation = system.create_reservation("DOC67890", "Asesoria BD", 2, quantity=1)
        system.confirm_reservation(reservation.id)
        system.cancel_reservation(reservation.id, reason="Client request")
        return reservation

    r13 = run_case(13, "Create, confirm and cancel reservation", case13)

    # 14. Process cancelled reservation (not allowed)
    def case14():
        if r13 is None:
            raise OperationNotAllowedError("No reservation to process.")
        system.process_reservation(r13.id)
        return "should not reach here"

    run_case(14, "Process cancelled reservation (not allowed)", case14)

    # 15. Overloaded cost calculations
    def case15():
        service = system.find_service("Sala A")
        c1v = service.cost_variant(3)
        c2v = service.cost_variant(2.5)
        c3v = service.cost_variant((4, 1))
        tax = service.calculate_cost_with_tax(duration=2, quantity=1, tax_rate=0.19)
        disc = service.calculate_cost_with_discount(duration=2, quantity=1, discount=0.10)
        return f"variants=({c1v}, {c2v}, {c3v}) tax={tax} discount={disc}"

    run_case(15, "Overloaded cost calculations", case15)

    # 16. Update client email with invalid value (rollback)
    def case16():
        client = system.find_client("DOC12345")
        client.update_email("bad-email")
        return "should not reach here"

    run_case(16, "Update client email with invalid value", case16)

    # 17. Invalid service parameter (capacity 0)
    def case17():
        service = RoomReservationService("Sala X", "Sala invalida", 10000.0, capacity=0)
        system.add_service(service)
        return "should not reach here"

    run_case(17, "Create service with invalid capacity", case17)

    # 18. Equipment rental cost with quantity
    def case18():
        service = system.find_service("Proyector HD")
        service.set_available(True)
        cost = service.calculate_cost(duration=3, quantity=2, tax_rate=0.19, discount=0.05)
        return f"Equipment cost: {cost}"

    run_case(18, "Equipment rental cost with quantity, tax and discount", case18)

    # 19. Advisory cost with expert level surcharge
    def case19():
        service = system.find_service("Asesoria BD")
        cost = service.calculate_cost(duration=4, quantity=1, tax_rate=0.19)
        return f"Advisory cost: {cost}"

    run_case(19, "Advisory cost with expert level surcharge", case19)

    # 20. Inconsistent calculation (negative via discount > 1) -> caught
    def case20():
        service = system.find_service("Sala A")
        return service.calculate_cost_with_discount(duration=2, quantity=1, discount=1.5)

    run_case(20, "Inconsistent calculation (discount > 100%)", case20)

    banner("SYSTEM SUMMARY")
    print(system.summary())
    print("Total clients:", len(system.clients))
    print("Total services:", len(system.services))
    print("Total reservations:", len(system.reservations))
    for reservation in system.reservations:
        print("  -", reservation.describe())
    print("\nSystem finished all simulations without crashing.")


if __name__ == "__main__":
    main()
