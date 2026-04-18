from __future__ import annotations

from uuid import UUID

import pytest

from base_typed_id import BaseTypedId, BaseTypedIdInvalidInputValueError


class UserId(BaseTypedId):
    pass


class ExternalEventId(BaseTypedId):
    uuid_version = 5


def test_none_generates_uuid_v4_typed_id() -> None:
    generated_user_id: UserId = UserId()
    parsed_uuid_value: UUID = UUID(str(generated_user_id))

    assert type(generated_user_id) is UserId
    assert parsed_uuid_value.version == 4


def test_string_input_preserves_exact_subtype() -> None:
    raw_uuid_string: str = "123e4567-e89b-42d3-a456-426614174000"

    user_id: UserId = UserId(raw_uuid_string)

    assert type(user_id) is UserId
    assert user_id == raw_uuid_string


def test_uuid_input_preserves_exact_subtype() -> None:
    raw_uuid_value: UUID = UUID("123e4567-e89b-42d3-a456-426614174000")

    user_id: UserId = UserId(raw_uuid_value)

    assert type(user_id) is UserId
    assert user_id == str(raw_uuid_value)


def test_invalid_uuid_string_raises_error() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        UserId("not-a-uuid")


def test_unsupported_input_type_raises_error() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        UserId(123)  # type: ignore[arg-type]


def test_uuid_version_mismatch_raises_error() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        UserId("123e4567-e89b-52d3-a456-426614174000")


def test_non_v4_subclass_cannot_auto_generate_from_none() -> None:
    with pytest.raises(BaseTypedIdInvalidInputValueError):
        ExternalEventId()


def test_normal_string_operations_return_plain_str() -> None:
    user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")

    uppercased_value: str = user_id.upper()
    concatenated_value: str = user_id + "_debug"

    assert type(uppercased_value) is str
    assert type(concatenated_value) is str


def test_repr_contains_exact_subtype_name() -> None:
    user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")

    assert repr(user_id) == "UserId('123e4567-e89b-42d3-a456-426614174000')"
