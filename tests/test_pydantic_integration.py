from __future__ import annotations

import json

import pytest
from pydantic import BaseModel, Field, ValidationError

from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


class UserModel(BaseModel):
    user_id: UserId


class GeneratedUserModel(BaseModel):
    user_id: UserId = Field(default_factory=UserId)


def test_model_validation_builds_exact_subtype() -> None:
    user_model: UserModel = UserModel.model_validate(
        {"user_id": "123e4567-e89b-42d3-a456-426614174000"}
    )

    assert type(user_model.user_id) is UserId


def test_model_dump_flattens_to_plain_string() -> None:
    user_model: UserModel = UserModel.model_validate(
        {"user_id": "123e4567-e89b-42d3-a456-426614174000"}
    )

    dumped_python: dict[str, object] = user_model.model_dump()

    assert type(dumped_python["user_id"]) is str
    assert dumped_python["user_id"] == "123e4567-e89b-42d3-a456-426614174000"


def test_model_dump_json_flattens_to_plain_string() -> None:
    user_model: UserModel = UserModel.model_validate(
        {"user_id": "123e4567-e89b-42d3-a456-426614174000"}
    )

    dumped_json: str = user_model.model_dump_json()
    loaded_json_payload: dict[str, object] = json.loads(dumped_json)

    assert type(loaded_json_payload["user_id"]) is str
    assert loaded_json_payload["user_id"] == "123e4567-e89b-42d3-a456-426614174000"


def test_model_validate_from_dump_reconstructs_exact_subtype() -> None:
    source_model: UserModel = UserModel.model_validate(
        {"user_id": "123e4567-e89b-42d3-a456-426614174000"}
    )
    dumped_python: dict[str, object] = source_model.model_dump()

    restored_model: UserModel = UserModel.model_validate(dumped_python)

    assert type(restored_model.user_id) is UserId


def test_json_schema_uses_native_uuid_format() -> None:
    json_schema: dict[str, object] = UserModel.model_json_schema()
    properties_schema: dict[str, object] = json_schema["properties"]  # type: ignore[assignment]
    user_id_schema: dict[str, object] = properties_schema["user_id"]  # type: ignore[assignment]

    assert user_id_schema["type"] == "string"
    assert user_id_schema["format"] == "uuid"


def test_default_factory_generates_typed_id() -> None:
    generated_user_model: GeneratedUserModel = GeneratedUserModel.model_validate({})

    assert type(generated_user_model.user_id) is UserId


def test_none_is_rejected_for_required_field() -> None:
    with pytest.raises(ValidationError):
        UserModel.model_validate({"user_id": None})