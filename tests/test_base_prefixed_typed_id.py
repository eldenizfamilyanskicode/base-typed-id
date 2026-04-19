from __future__ import annotations

import re
from typing import Any, cast
from uuid import UUID

import pytest

from base_typed_id import (
    BasePrefixedTypedId,
    BaseTypedIdInvalidInputValueError,
    BaseTypedIdInvariantViolationError,
)


class UserId(BasePrefixedTypedId):
    prefix = "user"


class ExternalEventId(BasePrefixedTypedId):
    prefix = "external_event"
    uuid_version = 5


class FlexibleUserId(BasePrefixedTypedId):
    prefix = "flexible_user"
    uuid_version = None


def test_none_generates_prefixed_uuid_v4_typed_id() -> None:
    generated_user_id: UserId = UserId()
    parsed_uuid_value: UUID = UUID(str(generated_user_id).split("_", maxsplit=1)[1])

    assert type(generated_user_id) is UserId
    assert str(generated_user_id).startswith("user_")
    assert parsed_uuid_value.version == 4


def test_plain_uuid_string_is_canonicalized_to_prefixed_value() -> None:
    user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")

    assert type(user_id) is UserId
    assert user_id == "user_123e4567-e89b-42d3-a456-426614174000"


def test_prefixed_string_input_preserves_exact_subtype() -> None:
    raw_prefixed_uuid_string: str = "user_123e4567-e89b-42d3-a456-426614174000"

    user_id: UserId = UserId(raw_prefixed_uuid_string)

    assert type(user_id) is UserId
    assert user_id == raw_prefixed_uuid_string


def test_uuid_input_is_canonicalized_to_prefixed_value() -> None:
    raw_uuid_value: UUID = UUID("123e4567-e89b-42d3-a456-426614174000")

    user_id: UserId = UserId(raw_uuid_value)

    assert type(user_id) is UserId
    assert user_id == "user_123e4567-e89b-42d3-a456-426614174000"


def test_invalid_prefixed_string_raises_error() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        UserId("user_not-a-uuid")


def test_unsupported_input_type_raises_error() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        UserId(123)  # type: ignore[arg-type]


def test_uuid_version_mismatch_raises_error() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        UserId("user_123e4567-e89b-52d3-a456-426614174000")


def test_non_v4_subclass_cannot_auto_generate_from_none() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        ExternalEventId()


def test_uuid_version_none_accepts_non_v4_uuid() -> None:
    flexible_user_id: FlexibleUserId = FlexibleUserId(
        "123e4567-e89b-52d3-a456-426614174000"
    )

    assert type(flexible_user_id) is FlexibleUserId
    assert flexible_user_id == "flexible_user_123e4567-e89b-52d3-a456-426614174000"


def test_normal_string_operations_return_plain_str() -> None:
    user_id: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")

    uppercased_value: str = user_id.upper()
    concatenated_value: str = user_id + "_debug"

    assert type(uppercased_value) is str
    assert type(concatenated_value) is str


def test_repr_contains_exact_subtype_name() -> None:
    user_id: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")

    assert repr(user_id) == "UserId('user_123e4567-e89b-42d3-a456-426614174000')"


def test_regex_contains_prefix_derived_pattern() -> None:
    assert UserId.regex.pattern == (
        "^user_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )


def test_regex_match_with_invalid_uuid_suffix_raises_invariant_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(UserId, "regex", re.compile(r"^user_invalid$"))

    with pytest.raises(BaseTypedIdInvariantViolationError):
        UserId("user_invalid")


def test_missing_prefix_definition_raises_invariant_error() -> None:
    with pytest.raises(BaseTypedIdInvariantViolationError):
        type(
            "MissingPrefixTypedId",
            (BasePrefixedTypedId,),
            {},
        )


def test_non_string_prefix_raises_invariant_error() -> None:
    with pytest.raises(BaseTypedIdInvariantViolationError):
        type(
            "InvalidPrefixTypeTypedId",
            (BasePrefixedTypedId,),
            {
                "prefix": cast(Any, 123),
            },
        )


def test_non_canonical_prefix_raises_invariant_error() -> None:
    with pytest.raises(BaseTypedIdInvariantViolationError):
        type(
            "InvalidPrefixFormatTypedId",
            (BasePrefixedTypedId,),
            {
                "prefix": "User",
            },
        )


def test_overriding_regex_raises_invariant_error() -> None:
    with pytest.raises(BaseTypedIdInvariantViolationError):
        type(
            "InvalidRegexOverrideTypedId",
            (BasePrefixedTypedId,),
            {
                "prefix": "user",
                "regex": UserId.regex,
            },
        )
