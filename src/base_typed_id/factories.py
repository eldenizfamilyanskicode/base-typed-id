from __future__ import annotations

import json
from collections.abc import Iterable
from typing import TypeVar
from uuid import UUID, uuid5

from ._base_typed_id import BaseTypedId
from ._exceptions import (
    BaseTypedIdInvalidInputValueError,
    BaseTypedIdInvariantViolationError,
)

BaseTypedIdType = TypeVar("BaseTypedIdType", bound=BaseTypedId)

_DEFAULT_DETERMINISTIC_NAMESPACE: UUID = UUID("0b8d2f0f-5c07-4fd9-a7d3-2c9d9d7c0f52")


def deterministically_from_words(
    typed_id_type: type[BaseTypedIdType],
    *,
    words: Iterable[str],
) -> BaseTypedIdType:
    """
    Build a stable typed identifier from ordered semantic words.

    Rules:
    - same words -> same identifier
    - order matters
    - words are serialized as canonical JSON before UUID v5 generation

    Important:
    - intended only for idempotent identifiers
    - requires `uuid_version = 5` or `uuid_version = None`
    """
    # Runtime guard is intentional because the library is callable from untyped code.
    if not isinstance(typed_id_type, type) or not issubclass(  # pyright: ignore[reportUnnecessaryIsInstance]
        typed_id_type,
        BaseTypedId,
    ):
        raise BaseTypedIdInvalidInputValueError(
            "typed_id_type must inherit from BaseTypedId."
        )

    expected_uuid_version: int | None = typed_id_type.uuid_version
    if expected_uuid_version not in (None, 5):
        raise BaseTypedIdInvariantViolationError(
            "deterministically_from_words requires a BaseTypedId subclass with "
            "uuid_version = 5 or uuid_version = None."
        )

    normalized_words: list[str] = []
    for word in words:
        # Runtime guard is intentional because the library is callable from untyped code
        if not isinstance(word, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise BaseTypedIdInvalidInputValueError(
                "deterministically_from_words accepts only str items in words. "
                f"Got: {type(word).__name__}."
            )
        normalized_words.append(word)

    if len(normalized_words) == 0:
        raise BaseTypedIdInvalidInputValueError(
            "deterministically_from_words requires at least one word."
        )

    canonical_payload: str = json.dumps(
        normalized_words,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    deterministic_uuid_value: UUID = uuid5(
        _DEFAULT_DETERMINISTIC_NAMESPACE,
        canonical_payload,
    )
    return typed_id_type(deterministic_uuid_value)
