from abc import ABC, abstractmethod
from functools import singledispatchmethod

from .entities import Entity
from .exceptions import (
    ServiceUnavailableError,
    InvalidServiceParameterError,
    InconsistentCalculationError,
)


class Service(Entity, ABC):
    def __init__(
        self,
        name: str,
        description: str,
        base_price: float,
        available: bool = True,
        min_duration: float = 1.0,
    ):
        super().__init__(name)
        self._description = description
        self._base_price = None
        self._available = bool(available)
        self._min_duration = min_duration
        self.base_price = base_price
        self.description = description

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise InvalidServiceParameterError("Description cannot be empty.", parameter="description")
        self._description = value.strip()

    @property
    def base_price(self) -> float:
        return self._base_price

    @base_price.setter
    def base_price(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise InvalidServiceParameterError(
                "Base price must be a number.", parameter="base_price", cause=exc
            ) from exc
        if value <= 0:
            raise InvalidServiceParameterError("Base price must be greater than zero.", parameter="base_price")
        self._base_price = value

    @property
    def available(self) -> bool:
        return self._available

    def set_available(self, value: bool):
        self._available = bool(value)

    @property
    def min_duration(self) -> float:
        return self._min_duration

    @min_duration.setter
    def min_duration(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise InvalidServiceParameterError(
                "Minimum duration must be a number.", parameter="min_duration", cause=exc
            ) from exc
        if value <= 0:
            raise InvalidServiceParameterError("Minimum duration must be greater than zero.", parameter="min_duration")
        self._min_duration = value

    def ensure_available(self):
        if not self._available:
            raise ServiceUnavailableError(f"Service '{self.name}' is not available.", service=self.name)

    def validate_duration(self, duration: float):
        try:
            duration = float(duration)
        except (TypeError, ValueError) as exc:
            raise InvalidServiceParameterError(
                "Duration must be a number.", parameter="duration", cause=exc
            ) from exc
        if duration < self._min_duration:
            raise InvalidServiceParameterError(
                f"Duration {duration} is below minimum {self._min_duration}.", parameter="duration"
            )
        if duration <= 0:
            raise InvalidServiceParameterError("Duration must be greater than zero.", parameter="duration")
        return duration

    @abstractmethod
    def calculate_cost(self, duration: float = 1.0, quantity: int = 1, tax_rate: float = 0.0, discount: float = 0.0):
        raise NotImplementedError

    @singledispatchmethod
    def cost_variant(self, arg):
        raise NotImplementedError

    @cost_variant.register
    def _(self, arg: int):
        return self.calculate_cost(duration=float(arg))

    @cost_variant.register
    def _(self, arg: float):
        return self.calculate_cost(duration=arg)

    @cost_variant.register
    def _(self, arg: tuple):
        duration, quantity = arg
        return self.calculate_cost(duration=duration, quantity=quantity)

    def calculate_cost_with_tax(self, duration: float = 1.0, quantity: int = 1, tax_rate: float = 0.19):
        base = self.calculate_cost(duration=duration, quantity=quantity, tax_rate=0.0, discount=0.0)
        total = base * (1 + tax_rate)
        if total < 0:
            raise InconsistentCalculationError("Negative total after tax.", value=total)
        return round(total, 2)

    def calculate_cost_with_discount(self, duration: float = 1.0, quantity: int = 1, discount: float = 0.10):
        base = self.calculate_cost(duration=duration, quantity=quantity, tax_rate=0.0, discount=0.0)
        total = base * (1 - discount)
        if total < 0:
            raise InconsistentCalculationError("Negative total after discount.", value=total)
        return round(total, 2)

    @abstractmethod
    def describe(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        raise NotImplementedError

    def validate(self) -> bool:
        try:
            if not self._available:
                return False
            if self._base_price <= 0:
                return False
            return True
        except Exception:
            return False

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', price={self._base_price}, available={self._available})"


class RoomReservationService(Service):
    def __init__(self, name: str, description: str, base_price: float, capacity: int = 10, available: bool = True):
        super().__init__(name, description, base_price, available=available, min_duration=1.0)
        self._capacity = None
        self.capacity = capacity

    @property
    def capacity(self) -> int:
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise InvalidServiceParameterError("Capacity must be an integer.", parameter="capacity", cause=exc) from exc
        if value <= 0:
            raise InvalidServiceParameterError("Capacity must be greater than zero.", parameter="capacity")
        self._capacity = value

    def calculate_cost(self, duration: float = 1.0, quantity: int = 1, tax_rate: float = 0.0, discount: float = 0.0):
        self.ensure_available()
        duration = self.validate_duration(duration)
        if quantity != 1:
            raise InvalidServiceParameterError("Room reservation does not support quantity.", parameter="quantity")
        base = self.base_price * duration
        total = base * (1 + tax_rate) * (1 - discount)
        if total < 0:
            raise InconsistentCalculationError("Inconsistent cost result.", value=total)
        return round(total, 2)

    def describe(self) -> str:
        return (
            f"RoomReservationService(name='{self.name}', price_per_hour={self.base_price}, "
            f"capacity={self._capacity}, available={self.available})"
        )

    def validate_parameters(self, **kwargs) -> bool:
        try:
            duration = kwargs.get("duration", 1.0)
            self.validate_duration(duration)
            return True
        except Exception:
            return False


class EquipmentRentalService(Service):
    def __init__(self, name: str, description: str, base_price: float, deposit: float = 0.0, available: bool = True):
        super().__init__(name, description, base_price, available=available, min_duration=1.0)
        self._deposit = None
        self.deposit = deposit

    @property
    def deposit(self) -> float:
        return self._deposit

    @deposit.setter
    def deposit(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise InvalidServiceParameterError("Deposit must be a number.", parameter="deposit", cause=exc) from exc
        if value < 0:
            raise InvalidServiceParameterError("Deposit cannot be negative.", parameter="deposit")
        self._deposit = value

    def calculate_cost(self, duration: float = 1.0, quantity: int = 1, tax_rate: float = 0.0, discount: float = 0.0):
        self.ensure_available()
        duration = self.validate_duration(duration)
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidServiceParameterError("Quantity must be a positive integer.", parameter="quantity")
        base = self.base_price * duration * quantity
        total = (base + self._deposit) * (1 + tax_rate) * (1 - discount)
        if total < 0:
            raise InconsistentCalculationError("Inconsistent cost result.", value=total)
        return round(total, 2)

    def describe(self) -> str:
        return (
            f"EquipmentRentalService(name='{self.name}', price_per_day={self.base_price}, "
            f"deposit={self._deposit}, available={self.available})"
        )

    def validate_parameters(self, **kwargs) -> bool:
        try:
            duration = kwargs.get("duration", 1.0)
            quantity = kwargs.get("quantity", 1)
            self.validate_duration(duration)
            if not isinstance(quantity, int) or quantity <= 0:
                return False
            return True
        except Exception:
            return False

class SpecializedAdvisoryService(Service):
    def __init__(self, name: str, description: str, base_price: float, expert_level: int = 1, available: bool = True):
        super().__init__(name, description, base_price, available=available, min_duration=0.5)
        self._expert_level = None
        self.expert_level = expert_level

    @property
    def expert_level(self) -> int:
        return self._expert_level

    @expert_level.setter
    def expert_level(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise InvalidServiceParameterError("Expert level must be an integer.", parameter="expert_level", cause=exc) from exc
        if value < 1 or value > 5:
            raise InvalidServiceParameterError("Expert level must be between 1 and 5.", parameter="expert_level")
        self._expert_level = value

    def calculate_cost(self, duration: float = 1.0, quantity: int = 1, tax_rate: float = 0.0, discount: float = 0.0):
        self.ensure_available()
        duration = self.validate_duration(duration)
        if quantity != 1:
            raise InvalidServiceParameterError("Advisory does not support quantity.", parameter="quantity")
        surcharge = 1 + (self._expert_level - 1) * 0.15
        base = self.base_price * duration * surcharge
        total = base * (1 + tax_rate) * (1 - discount)
        if total < 0:
            raise InconsistentCalculationError("Inconsistent cost result.", value=total)
        return round(total, 2)

    def describe(self) -> str:
        return (
            f"SpecializedAdvisoryService(name='{self.name}', price_per_hour={self.base_price}, "
            f"expert_level={self._expert_level}, available={self.available})"
        )

    def validate_parameters(self, **kwargs) -> bool:
        try:
            duration = kwargs.get("duration", 1.0)
            self.validate_duration(duration)
            return True
        except Exception:
            return False
