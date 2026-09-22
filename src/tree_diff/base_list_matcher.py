from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseListMatcher(ABC, Generic[T]):
    @staticmethod
    @abstractmethod
    def match_lists(base: Iterable[T], compare: Iterable[T]) -> list[tuple[T, T]]:
        raise NotImplementedError
