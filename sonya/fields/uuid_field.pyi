from uuid import UUID
from .bytes_field import BytesField


class UUIDField(BytesField):
    DEFAULT = ...

    def from_python(self, value: UUID) -> bytes: ...
    def to_python(self, value: bytes) -> UUID: ...
