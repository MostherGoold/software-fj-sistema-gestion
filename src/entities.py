from abc import ABC, abstractmethod
from datetime import datetime

from .exceptions import InvalidEntityError


class Entity(ABC):
    _id_counter = 0

    def __init__(self, name: str):
        Entity._id_counter += 1
        self._id = Entity._id_counter
        self._name = None
        self.name = name
        self._created_at = datetime.now()

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise InvalidEntityError("Entity name cannot be empty.", cause=ValueError("empty name"))
        self._name = value.strip()

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @abstractmethod
    def describe(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, name='{self._name}')"

    def __repr__(self) -> str:
        return self.__str__()
