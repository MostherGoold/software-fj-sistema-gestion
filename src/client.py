import re

from .entities import Entity
from .exceptions import InvalidClientError


class Client(Entity):
    _EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    _PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")

    def __init__(self, name: str, document: str, email: str, phone: str = None):
        super().__init__(name)
        self._document = None
        self._email = None
        self._phone = None
        self._active = True

        try:
            self.document = document
            self.email = email
            self.phone = phone
        except (ValueError, TypeError) as exc:
            raise InvalidClientError(
                f"Invalid data when creating client '{name}'.",
                field="general",
                cause=exc,
            ) from exc

    @property
    def document(self) -> str:
        return self._document

    @document.setter
    def document(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise InvalidClientError("Document cannot be empty.", field="document")
        value = value.strip()
        if len(value) < 5 or len(value) > 20:
            raise InvalidClientError(
                "Document must have between 5 and 20 characters.", field="document"
            )
        if not value.isalnum():
            raise InvalidClientError(
                "Document may only contain alphanumeric characters.", field="document"
            )
        self._document = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise InvalidClientError("Email cannot be empty.", field="email")
        value = value.strip().lower()
        if not self._EMAIL_REGEX.match(value):
            raise InvalidClientError(f"Invalid email format: '{value}'.", field="email")
        self._email = value

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            self._phone = None
            return
        if not isinstance(value, str):
            raise InvalidClientError("Phone must be text.", field="phone")
        value = value.strip()
        if not self._PHONE_REGEX.match(value):
            raise InvalidClientError(f"Invalid phone format: '{value}'.", field="phone")
        self._phone = value

    @property
    def active(self) -> bool:
        return self._active

    def deactivate(self):
        self._active = False

    def activate(self):
        self._active = True

    def describe(self) -> str:
        phone = self._phone if self._phone else "no phone"
        status = "active" if self._active else "inactive"
        return (
            f"Client(id={self.id}, name='{self.name}', document='{self._document}', "
            f"email='{self._email}', phone='{phone}', status={status})"
        )

    def validate(self) -> bool:
        try:
            if not self._document or not self._email:
                return False
            if not self._EMAIL_REGEX.match(self._email):
                return False
            if self._phone is not None and not self._PHONE_REGEX.match(self._phone):
                return False
            if not self._active:
                return False
            return True
        except Exception:
            return False

    def update_email(self, new_email: str):
        previous = self._email
        try:
            self.email = new_email
        except InvalidClientError as exc:
            self._email = previous
            raise InvalidClientError(
                "Could not update email; previous value kept.",
                field="email",
                cause=exc,
            ) from exc
