import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.system import SoftwareFJSystem
from src.service import RoomReservationService
from src.exceptions import InvalidClientError, InvalidReservationError


class TestSystem(unittest.TestCase):
    def setUp(self):
        self.system = SoftwareFJSystem(log_path="logs/test.log")

    def test_register_valid_client(self):
        client = self.system.register_client("Test User", "DOC11111", "test@example.com")
        self.assertEqual(client.document, "DOC11111")
        self.assertEqual(len(self.system.clients), 1)

    def test_register_invalid_client(self):
        with self.assertRaises(InvalidClientError):
            self.system.register_client("Bad", "DOC22222", "bad-email")
        self.assertEqual(len(self.system.clients), 0)

    def test_reservation_flow(self):
        self.system.register_client("Juan", "DOC33333", "juan@example.com")
        self.system.add_service(RoomReservationService("Sala T", "Sala", 1000.0, capacity=5))
        reservation = self.system.create_reservation("DOC33333", "Sala T", 2)
        self.assertEqual(reservation.status, "PENDING")
        self.system.confirm_reservation(reservation.id)
        self.assertEqual(reservation.status, "CONFIRMED")
        cost = self.system.process_reservation(reservation.id, tax_rate=0.10)
        self.assertGreater(cost, 0)
        self.assertEqual(reservation.status, "PROCESSED")

    def test_reservation_unknown_client(self):
        self.system.add_service(RoomReservationService("Sala T2", "Sala", 1000.0, capacity=5))
        with self.assertRaises(InvalidReservationError):
            self.system.create_reservation("NOPE", "Sala T2", 2)


if __name__ == "__main__":
    unittest.main()
