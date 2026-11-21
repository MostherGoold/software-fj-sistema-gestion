import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.system import SoftwareFJSystem
from src.service import (
    RoomReservationService,
    EquipmentRentalService,
    SpecializedAdvisoryService,
)
from src.exceptions import (
    ServiceUnavailableError,
    InvalidServiceParameterError,
    InconsistentCalculationError,
    OperationNotAllowedError,
)


class TestServices(unittest.TestCase):
    def setUp(self):
        self.system = SoftwareFJSystem(log_path="logs/test.log")

    def test_room_cost_with_tax_and_discount(self):
        self.system.add_service(RoomReservationService("Sala T", "Sala", 1000.0, capacity=5))
        service = self.system.find_service("Sala T")
        cost = service.calculate_cost(duration=2, quantity=1, tax_rate=0.19, discount=0.10)
        self.assertAlmostEqual(cost, 2142.0, places=2)

    def test_equipment_cost_with_quantity(self):
        self.system.add_service(EquipmentRentalService("Proy T", "Proy", 100.0, deposit=50.0))
        service = self.system.find_service("Proy T")
        cost = service.calculate_cost(duration=3, quantity=2, tax_rate=0.0, discount=0.0)
        self.assertEqual(cost, 650.0)

    def test_advisory_surcharge(self):
        self.system.add_service(SpecializedAdvisoryService("Adv T", "Adv", 100.0, expert_level=3))
        service = self.system.find_service("Adv T")
        cost = service.calculate_cost(duration=2, quantity=1, tax_rate=0.0, discount=0.0)
        self.assertEqual(cost, 260.0)

    def test_unavailable_service_raises(self):
        service = RoomReservationService("Sala X", "Sala", 1000.0, capacity=5)
        service.set_available(False)
        with self.assertRaises(ServiceUnavailableError):
            service.ensure_available()

    def test_invalid_capacity_raises(self):
        with self.assertRaises(InvalidServiceParameterError):
            RoomReservationService("Sala Y", "Sala", 1000.0, capacity=0)

    def test_invalid_duration_raises(self):
        service = RoomReservationService("Sala Z", "Sala", 1000.0, capacity=5)
        with self.assertRaises(InvalidServiceParameterError):
            service.validate_duration(0.1)

    def test_inconsistent_calculation_raises(self):
        service = RoomReservationService("Sala W", "Sala", 1000.0, capacity=5)
        with self.assertRaises(InconsistentCalculationError):
            service.calculate_cost_with_discount(duration=2, quantity=1, discount=1.5)

    def test_cancel_and_process_not_allowed(self):
        self.system.register_client("Juan", "DOC55555", "juan2@example.com")
        self.system.add_service(RoomReservationService("Sala C", "Sala", 1000.0, capacity=5))
        reservation = self.system.create_reservation("DOC55555", "Sala C", 2)
        self.system.confirm_reservation(reservation.id)
        self.system.cancel_reservation(reservation.id)
        with self.assertRaises(OperationNotAllowedError):
            self.system.process_reservation(reservation.id)

    def test_cost_variant_single_dispatch(self):
        self.system.add_service(RoomReservationService("Sala V", "Sala", 1000.0, capacity=5))
        service = self.system.find_service("Sala V")
        self.assertEqual(service.cost_variant(2), 2000.0)
        self.assertEqual(service.cost_variant(2.5), 2500.0)
        self.assertEqual(service.cost_variant((3, 1)), 3000.0)

    def test_calculate_with_tax_helper(self):
        self.system.add_service(RoomReservationService("Sala H", "Sala", 1000.0, capacity=5))
        service = self.system.find_service("Sala H")
        cost = service.calculate_cost_with_tax(duration=2, quantity=1, tax_rate=0.19)
        self.assertAlmostEqual(cost, 2380.0, places=2)


if __name__ == "__main__":
    unittest.main()
