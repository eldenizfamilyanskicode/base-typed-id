from __future__ import annotations

import builtins
from collections.abc import Callable
from typing import Any
from unittest.mock import patch

import pytest

from base_typed_id import (
    BasePrefixedTypedId,
    BaseTypedId,
    BaseTypedIdInvariantViolationError,
)


class UserId(BasePrefixedTypedId):
    prefix = "user"


def test_base_typed_id_schema_error_when_pydantic_core_is_missing() -> None:
    original_import_function: Callable[..., Any] = builtins.__import__

    def import_with_forced_pydantic_core_failure(
        module_name: str,
        globals_dict: Any = None,
        locals_dict: Any = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if module_name == "pydantic_core":
            raise ImportError("forced test import error for pydantic_core")

        return original_import_function(
            module_name,
            globals_dict,
            locals_dict,
            fromlist,
            level,
        )

    with patch(
        "builtins.__import__",
        side_effect=import_with_forced_pydantic_core_failure,
    ):
        with pytest.raises(BaseTypedIdInvariantViolationError) as caught_error:
            BaseTypedId.__get_pydantic_core_schema__(
                source_type=BaseTypedId,
                handler=None,
            )

    assert str(caught_error.value) == (
        "pydantic-core is required to build BaseTypedId schema."
    )


def test_base_prefixed_schema_error_when_pydantic_core_is_missing() -> None:
    original_import_function: Callable[..., Any] = builtins.__import__

    def import_with_forced_pydantic_core_failure(
        module_name: str,
        globals_dict: Any = None,
        locals_dict: Any = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if module_name == "pydantic_core":
            raise ImportError("forced test import error for pydantic_core")

        return original_import_function(
            module_name,
            globals_dict,
            locals_dict,
            fromlist,
            level,
        )

    with patch(
        "builtins.__import__",
        side_effect=import_with_forced_pydantic_core_failure,
    ):
        with pytest.raises(BaseTypedIdInvariantViolationError) as caught_error:
            UserId.__get_pydantic_core_schema__(
                source_type=UserId,
                handler=None,
            )

    assert str(caught_error.value) == (
        "pydantic-core is required to build BasePrefixedTypedId schema."
    )
