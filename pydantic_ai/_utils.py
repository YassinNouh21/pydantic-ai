import asyncio
from dataclasses import dataclass, is_dataclass
from functools import partial
from typing import Any, Callable, Generic, ParamSpec, TypeAlias, TypeVar, get_args, is_typeddict, overload

from pydantic import BaseModel

_P = ParamSpec('_P')
_R = TypeVar('_R')


async def run_in_executor(func: Callable[_P, _R], *args: _P.args, **kwargs: _P.kwargs) -> _R:
    if kwargs:
        return await asyncio.get_running_loop().run_in_executor(None, partial(func, *args, **kwargs))
    else:
        return await asyncio.get_running_loop().run_in_executor(None, func, *args)  # type: ignore


_UnionType = type(int | str)


def allow_plain_str(response_type: Any) -> bool:
    """Check if the response type allows plain strings."""
    return isinstance(response_type, _UnionType) and any(t is str for t in get_args(response_type))


def is_model_like(response_type: Any) -> bool:
    """Check if the response type is model-like."""
    return isinstance(response_type, type) and (
        issubclass(response_type, BaseModel) or is_dataclass(response_type) or is_typeddict(response_type)
    )


_T = TypeVar('_T')


@dataclass
class Some(Generic[_T]):
    """Analogous to Rust's `Option::Some` type."""

    value: _T


# Analogous to Rust's `Option` type, usage: `Option[Thing]` is equivalent to `Some[Thing] | None`
Option: TypeAlias = Some[_T] | None


_Left = TypeVar('_Left')
_Right = TypeVar('_Right')


class Either(Generic[_Left, _Right]):
    """Two member Union that records which member was set.

    Usage:

    ```py
    if left_thing := either.left:
        use_left(left_thing)
    else:
        use_right(either.right)
    ```
    """

    @overload
    def __init__(self, *, left: _Left) -> None: ...

    @overload
    def __init__(self, *, right: _Right) -> None: ...

    def __init__(self, *, left: _Left | None = None, right: _Right | None = None) -> None:
        if (left is not None and right is not None) or (left is None and right is None):
            raise TypeError('Either must have exactly one value')
        self._left = left
        self._right = right

    @property
    def left(self) -> _Left | None:
        return self._left

    @property
    def right(self) -> _Right:
        if self._right is None:
            raise TypeError('Right not set')
        return self._right
