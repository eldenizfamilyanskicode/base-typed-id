from __future__ import annotations

import json
from uuid import UUID

import pytest
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


class UserModel(BaseModel):
    user_id: UserId


class GeneratedUserModel(BaseModel):
    user_id: UserId = Field(default_factory=UserId)


def test_python_model_validation_from_prefixed_string_builds_exact_subtype() -> None:
    user_model: UserModel = UserModel.model_validate(
        {"user_id": "user_123e4567-e89b-42d3-a456-426614174000"}
    )

    assert type(user_model.user_id) is UserId


def test_python_model_validation_from_plain_uuid_string_builds_exact_subtype() -> None:
    user_model: UserModel = UserModel.model_validate(
        {"user_id": "123e4567-e89b-42d3-a456-426614174000"}
    )

    assert type(user_model.user_id) is UserId
    assert user_model.user_id == "user_123e4567-e89b-42d3-a456-426614174000"


def test_python_model_validation_from_uuid_object_builds_exact_subtype() -> None:
    user_model: UserModel = UserModel.model_validate(
        {"user_id": UUID("123e4567-e89b-42d3-a456-426614174000")}
    )

    assert type(user_model.user_id) is UserId
    assert user_model.user_id == "user_123e4567-e89b-42d3-a456-426614174000"


def test_model_dump_flattens_to_plain_string() -> None:
    user_model: UserModel = UserModel.model_validate(
        {"user_id": "user_123e4567-e89b-42d3-a456-426614174000"}
    )

    dumped_python: dict[str, object] = user_model.model_dump()

    assert type(dumped_python["user_id"]) is str
    assert dumped_python["user_id"] == "user_123e4567-e89b-42d3-a456-426614174000"


def test_model_dump_json_flattens_to_plain_string() -> None:
    user_model: UserModel = UserModel.model_validate(
        {"user_id": "user_123e4567-e89b-42d3-a456-426614174000"}
    )

    dumped_json: str = user_model.model_dump_json()
    loaded_json_payload: dict[str, object] = json.loads(dumped_json)

    assert type(loaded_json_payload["user_id"]) is str
    assert loaded_json_payload["user_id"] == "user_123e4567-e89b-42d3-a456-426614174000"


def test_type_adapter_dump_python_flattens_to_plain_string() -> None:
    user_id_adapter: TypeAdapter[UserId] = TypeAdapter(UserId)
    user_id: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")

    dumped_value: object = user_id_adapter.dump_python(user_id)

    assert dumped_value == "user_123e4567-e89b-42d3-a456-426614174000"
    assert type(dumped_value) is str


def test_model_validate_from_dump_reconstructs_exact_subtype() -> None:
    source_model: UserModel = UserModel.model_validate(
        {"user_id": "user_123e4567-e89b-42d3-a456-426614174000"}
    )
    dumped_python: dict[str, object] = source_model.model_dump()

    restored_model: UserModel = UserModel.model_validate(dumped_python)

    assert type(restored_model.user_id) is UserId


def test_json_schema_uses_string_type_with_prefix_pattern() -> None:
    json_schema: dict[str, object] = UserModel.model_json_schema()
    properties_schema: dict[str, object] = json_schema["properties"]  # type: ignore[assignment]
    user_id_schema: dict[str, object] = properties_schema["user_id"]  # type: ignore[assignment]

    assert user_id_schema["type"] == "string"
    assert user_id_schema["pattern"] == (
        "^user_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )


def test_default_factory_generates_prefixed_typed_id() -> None:
    generated_user_model: GeneratedUserModel = GeneratedUserModel.model_validate({})

    assert type(generated_user_model.user_id) is UserId
    assert generated_user_model.user_id.startswith("user_")


def test_none_is_rejected_for_required_field() -> None:
    with pytest.raises(ValidationError):
        UserModel.model_validate({"user_id": None})


def test_json_validation_accepts_canonical_prefixed_string() -> None:
    user_model: UserModel = UserModel.model_validate_json(
        '{"user_id":"user_123e4567-e89b-42d3-a456-426614174000"}'
    )

    assert type(user_model.user_id) is UserId


def test_json_validation_rejects_plain_uuid_string() -> None:
    with pytest.raises(ValidationError):
        UserModel.model_validate_json(
            '{"user_id":"123e4567-e89b-42d3-a456-426614174000"}'
        )
