from __future__ import annotations

from typing import Any

import pytest

from base_typed_id import (
    BaseTypedId,
    BaseTypedIdInvalidInputValueError,
    BaseTypedIdInvariantViolationError,
)
from base_typed_id.factories import deterministically_from_words


class StableEventId(BaseTypedId):
    uuid_version = 5


class FlexibleEventId(BaseTypedId):
    uuid_version = None


class UserId(BaseTypedId):
    pass


def test_same_words_produce_same_typed_id() -> None:
    first_event_id: StableEventId = deterministically_from_words(
        StableEventId,
        words=["workspace", "provider", "message", "42"],
    )
    second_event_id: StableEventId = deterministically_from_words(
        StableEventId,
        words=["workspace", "provider", "message", "42"],
    )

    assert type(first_event_id) is StableEventId
    assert type(second_event_id) is StableEventId
    assert first_event_id == second_event_id


def test_word_order_changes_identifier() -> None:
    first_event_id: StableEventId = deterministically_from_words(
        StableEventId,
        words=["workspace", "provider", "message", "42"],
    )
    second_event_id: StableEventId = deterministically_from_words(
        StableEventId,
        words=["42", "message", "provider", "workspace"],
    )

    assert first_event_id != second_event_id


def test_factory_supports_version_agnostic_subclass() -> None:
    flexible_event_id: FlexibleEventId = deterministically_from_words(
        FlexibleEventId,
        words=["workspace", "provider", "message", "42"],
    )

    assert type(flexible_event_id) is FlexibleEventId


def test_factory_rejects_version_four_subclass() -> None:
    with pytest.raises(BaseTypedIdInvariantViolationError):
        deterministically_from_words(
            UserId,
            words=["workspace", "provider", "message", "42"],
        )


def test_factory_rejects_empty_words() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        deterministically_from_words(
            StableEventId,
            words=[],
        )


def test_factory_rejects_non_string_words() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        deterministically_from_words(
            StableEventId,
            words=["workspace", "provider", 42],  # type: ignore[list-item]
        )


def test_deterministically_from_words_rejects_non_type_typed_id_type() -> None:
    invalid_typed_id_type: Any = "UserId"

    with pytest.raises(
        BaseTypedIdInvalidInputValueError,
        match="typed_id_type must inherit from BaseTypedId.",
    ):
        deterministically_from_words(
            invalid_typed_id_type,
            words=["workspace:house-of-ai"],
        )
