from datetime import datetime

from .client import Client
from .service import Service
from .exceptions import (
    InvalidReservationError,
    OperationNotAllowedError,
    ServiceUnavailableError,
)


class Reservation:
    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_PROCESSED = "PROCESSED"

    def __init__(self, client: Client, service: Service, duration: float, quantity: int = 1):
        self._id = None
        self._client = None
        self._service = None
        self._duration = None
        self._quantity = quantity
        self._status = self.STATUS_PENDING
        self._created_at = datetime.now()
        self._confirmed_at = None
        self._cancelled_at = None
        self._processed_at = None
        self._total_cost = None

        try:
            if not isinstance(client, Client):
                raise InvalidReservationError("Client must be a Client instance.")
            if not isinstance(service, Service):
                raise InvalidReservationError("Service must be a Service instance.")
            if not client.active:
                raise InvalidReservationError("Client is not active.")
            service.ensure_available()
            duration = service.validate_duration(duration)
            if not isinstance(quantity, int) or quantity <= 0:
                raise InvalidReservationError("Quantity must be a positive integer.")

            self._client = client
            self._service = service
            self._duration = duration
            self._quantity = quantity
            Reservation._assign_id(self)
        except (InvalidReservationError, ServiceUnavailableError, Exception) as exc:
            raise InvalidReservationError(
                "Could not create reservation.", reservation_id=None, cause=exc
            ) from exc

    _id_counter = 0

    @classmethod
    def _assign_id(cls, instance):
        cls._id_counter += 1
        instance._id = cls._id_counter

    @property
    def id(self) -> int:
        return self._id

    @property
    def client(self) -> Client:
        return self._client

    @property
    def service(self) -> Service:
        return self._service

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def status(self) -> str:
        return self._status

    @property
    def total_cost(self):
        return self._total_cost

    def confirm(self):
        if self._status != self.STATUS_PENDING:
            raise OperationNotAllowedError(
                f"Cannot confirm reservation in status {self._status}."
            )
        try:
            self._service.ensure_available()
            self._status = self.STATUS_CONFIRMED
            self._confirmed_at = datetime.now()
        except ServiceUnavailableError as exc:
            raise InvalidReservationError(
                "Service became unavailable; cannot confirm.", reservation_id=str(self._id), cause=exc
            ) from exc
        return self

    def cancel(self, reason: str = None):
        if self._status in (self.STATUS_CANCELLED, self.STATUS_PROCESSED):
            raise OperationNotAllowedError(
                f"Cannot cancel reservation in status {self._status}."
            )
        self._status = self.STATUS_CANCELLED
        self._cancelled_at = datetime.now()
        return self

    def process(self, tax_rate: float = 0.0, discount: float = 0.0):
        if self._status != self.STATUS_CONFIRMED:
            raise OperationNotAllowedError(
                f"Cannot process reservation in status {self._status}."
            )
        try:
            cost = self._service.calculate_cost(
                duration=self._duration, quantity=self._quantity, tax_rate=tax_rate, discount=discount
            )
            self._total_cost = cost
            self._status = self.STATUS_PROCESSED
            self._processed_at = datetime.now()
            return cost
        except Exception as exc:
            raise InvalidReservationError(
                "Error processing reservation.", reservation_id=str(self._id), cause=exc
            ) from exc

    def describe(self) -> str:
        return (
            f"Reservation(id={self._id}, client='{self._client.name}', service='{self._service.name}', "
            f"duration={self._duration}, quantity={self._quantity}, status={self._status}, "
            f"total_cost={self._total_cost})"
        )

    def __str__(self) -> str:
        return self.describe()

    def __repr__(self) -> str:
        return self.describe()

    def validate(self) -> bool:
        try:
            if self._client is None or self._service is None:
                return False
            if self._duration <= 0:
                return False
            if self._quantity <= 0:
                return False
            return True
        except Exception:
            return False
