from .client import Client
from .service import Service
from .reservation import Reservation
from .logger import SystemLogger
from .exceptions import (
    InvalidClientError,
    ServiceUnavailableError,
    InvalidReservationError,
    InvalidServiceParameterError,
)


class SoftwareFJSystem:
    def __init__(self, log_path: str = "logs/system.log"):
        self._clients = []
        self._services = []
        self._reservations = []
        self._logger = SystemLogger(log_path)

    @property
    def clients(self):
        return list(self._clients)

    @property
    def services(self):
        return list(self._services)

    @property
    def reservations(self):
        return list(self._reservations)

    @property
    def logger(self):
        return self._logger

    def register_client(self, name, document, email, phone=None):
        try:
            client = Client(name, document, email, phone)
            if any(c.document == client.document for c in self._clients):
                raise InvalidClientError("Client with this document already exists.", field="document")
            self._clients.append(client)
            self._logger.log_event("CLIENT_REGISTERED", client.describe())
            return client
        except InvalidClientError as exc:
            self._logger.error("Failed to register client.", exc)
            raise
        finally:
            self._logger.debug("register_client finished.")

    def add_service(self, service):
        try:
            if not isinstance(service, Service):
                raise InvalidServiceParameterError("Object is not a Service.", parameter="service")
            if any(s.name == service.name for s in self._services):
                raise InvalidServiceParameterError("Service with this name already exists.", parameter="name")
            self._services.append(service)
            self._logger.log_event("SERVICE_ADDED", service.describe())
            return service
        except (InvalidServiceParameterError, Exception) as exc:
            self._logger.error("Failed to add service.", exc)
            raise
        finally:
            self._logger.debug("add_service finished.")

    def find_client(self, document):
        for client in self._clients:
            if client.document == document:
                return client
        return None

    def find_service(self, name):
        for service in self._services:
            if service.name == name:
                return service
        return None

    def create_reservation(self, client_document, service_name, duration, quantity=1):
        try:
            client = self.find_client(client_document)
            if client is None:
                raise InvalidReservationError(f"Client with document '{client_document}' not found.")
            service = self.find_service(service_name)
            if service is None:
                raise ServiceUnavailableError(f"Service '{service_name}' not found.", service=service_name)
            reservation = Reservation(client, service, duration, quantity)
            self._reservations.append(reservation)
            self._logger.log_event("RESERVATION_CREATED", reservation.describe())
            return reservation
        except (InvalidReservationError, ServiceUnavailableError, InvalidClientError, Exception) as exc:
            self._logger.error("Failed to create reservation.", exc)
            raise
        finally:
            self._logger.debug("create_reservation finished.")

    def confirm_reservation(self, reservation_id):
        reservation = self._find_reservation(reservation_id)
        try:
            reservation.confirm()
            self._logger.log_event("RESERVATION_CONFIRMED", reservation.describe())
            return reservation
        except Exception as exc:
            self._logger.error("Failed to confirm reservation.", exc)
            raise
        finally:
            self._logger.debug("confirm_reservation finished.")

    def cancel_reservation(self, reservation_id, reason=None):
        reservation = self._find_reservation(reservation_id)
        try:
            reservation.cancel(reason)
            self._logger.log_event("RESERVATION_CANCELLED", reservation.describe())
            return reservation
        except Exception as exc:
            self._logger.error("Failed to cancel reservation.", exc)
            raise
        finally:
            self._logger.debug("cancel_reservation finished.")

    def process_reservation(self, reservation_id, tax_rate=0.0, discount=0.0):
        reservation = self._find_reservation(reservation_id)
        try:
            cost = reservation.process(tax_rate=tax_rate, discount=discount)
            self._logger.log_event("RESERVATION_PROCESSED", f"{reservation.describe()} cost={cost}")
            return cost
        except Exception as exc:
            self._logger.error("Failed to process reservation.", exc)
            raise
        finally:
            self._logger.debug("process_reservation finished.")

    def _find_reservation(self, reservation_id):
        for reservation in self._reservations:
            if reservation.id == reservation_id:
                return reservation
        raise InvalidReservationError(f"Reservation with id '{reservation_id}' not found.", reservation_id=str(reservation_id))

    def summary(self):
        return {
            "clients": len(self._clients),
            "services": len(self._services),
            "reservations": len(self._reservations),
            "by_status": self._count_by_status(),
        }

    def _count_by_status(self):
        counts = {}
        for reservation in self._reservations:
            counts[reservation.status] = counts.get(reservation.status, 0) + 1
        return counts
