from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session

from .database import get_session as _get_session


@contextmanager
def session_scope() -> Iterator[Session]:
    with _get_session() as session:
        yield session


def get_db_session() -> Session:
    with _get_session() as session:
        yield session
