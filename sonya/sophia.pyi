from typing import Union, Tuple, Dict, Iterable


class SophiaError(Exception): ...

class SophiaClosed(SophiaError): ...
class DocumentClosed(SophiaClosed): ...

class BadQuery(SophiaError): ...

class TransactionError(SophiaError): ...
class TransactionRollback(TransactionError): ...
class TransactionLocked(TransactionError): ...


class IndexType:
    def __new__(cls, value: str, is_bytes: bool): ...


class Types:
    string = ...
    u64 = ...
    u32 = ...
    u16 = ...
    u8 = ...
    u64_rev = ...
    u32_rev = ...
    u16_rev = ...
    u8_rev = ...


class Environment:
    @property
    def configuration(self) -> Dict[str, Union[str, int]]: ...

    @property
    def is_closed(self) -> bool: ...

    def open(self) -> int: ...
    def close(self) -> int: ...
    def get_string(self, key: str) -> bytes: ...
    def get_int(self, key: str) -> bytes: ...
    def set_string(self, key: str, value: bytes) -> int: ...
    def set_int(self, key: str, value: int) -> int: ...
    def get_object(self, name: str) -> Database: ...
    def transaction(self) -> Transaction: ...


class Transaction:
    @property
    def env(self) -> Environment: ...

    @property
    def closed(self) -> bool: ...

    def set(self, document: Document) -> int: ...
    def commit(self) -> int: ...
    def rollback(self) -> int: ...
    def __enter__(self) -> Transaction: ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...


class Database:
    @property
    def name(self) -> str: ...

    @property
    def env(self) -> Environment: ...

    def get(self, query: Document) -> Document: ...
    def set(self, document: Document) -> int: ...
    def delete(self, query: Document) -> int: ...
    def cursor(self, query: dict) -> Cursor: ...
    def transaction(self) -> Transaction: ...


class Cursor:
    @property
    def env(self) -> Environment: ...

    @property
    def db(self) -> Database: ...

    @property
    def query(self) -> dict: ...

    def __init__(self, env: Environment, query: dict, db: Database): ...
    def __iter__(self) -> Iterable[Document]: ...


class Document:
    @property
    def db(self) -> Database: ...

    @property
    def closed(self) -> bool: ...


    def get_string(self, key: str) -> bytes: ...
    def get_int(self, key: str) -> int: ...
    def set_string(self, key: str, value: bytes) -> int: ...
    def set_int(self, key: str, value: int) -> int: ...
