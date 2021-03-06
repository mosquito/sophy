from typing import Generator

from . import sophia
from .env import Environment
from .document import Document
from .schema import Schema


class Transaction:
    db = ...  # type: Database
    tx = ...  # type: sophia.Transaction

    def __init__(self, db: Database):
        self.db = ...   # type: Database
        self.tx = ...   # type: sophia.Transaction

    def set(self, document: Document): ...
    def get(self, **kwargs) -> Document: ...
    def delete(self, **kwargs): ...
    def commit(self) -> int: ...
    def rollback(self) -> int: ...
    def __enter__(self) -> "Transaction": ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...


class Database:
    def __init__(self, name: str, schema: Schema):
        self.name = ...         # type: str
        self.schema = ...       # type: Schema
        self.environment = ...  # type: Environment
        self.db = ...           # type: sophia.Database

    def define(self, environment: Environment, **kwargs) -> "Database": ...
    def transaction(self) -> Transaction: ...
    def document(self, **kwargs) -> Document: ...
    def set(self, document: Document): ...
    def get(self, **kwargs) -> Document: ...
    def delete(self, **kwargs): ...
    def cursor(self, **query) -> Generator[Document]: ...
    def __iter__(self) -> Generator[Document]: ...
    def delete_many(self, **query) -> int: ...
