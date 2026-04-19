from __future__ import annotations

import json

from pydantic import BaseModel, ValidationError

from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


class ContactModel(BaseModel):
    primary_user_id: UserId
    backup_user_id: UserId


def print_section(title: str) -> None:
    separator: str = "=" * len(title)
    print()
    print(separator)
    print(title)
    print(separator)


def print_value_state(label: str, value: object) -> None:
    print(f"{label}:")
    print(f"  repr         : {value!r}")
    print(f"  runtime type : {type(value).__name__}")
    print()


def main() -> None:
    contact_model_from_python: ContactModel = ContactModel.model_validate(
        {
            "primary_user_id": "123e4567-e89b-42d3-a456-426614174000",
            "backup_user_id": "user_123e4567-e89b-42d3-a456-426614174001",
        }
    )

    dumped_python: dict[str, object] = contact_model_from_python.model_dump()
    dumped_json: str = contact_model_from_python.model_dump_json()
    loaded_from_json: dict[str, object] = json.loads(dumped_json)

    restored_from_python_dump: ContactModel = ContactModel.model_validate(dumped_python)
    restored_from_json_payload: ContactModel = ContactModel.model_validate_json(
        dumped_json
    )

    print_section("1. runtime values inside pydantic model")

    print_value_state(
        "contact_model_from_python.primary_user_id",
        contact_model_from_python.primary_user_id,
    )
    print_value_state(
        "contact_model_from_python.backup_user_id",
        contact_model_from_python.backup_user_id,
    )

    print(
        f"primary_user_id exact subtype kept: "
        f"{type(contact_model_from_python.primary_user_id) is UserId}"
    )
    print(
        f"backup_user_id exact subtype kept : "
        f"{type(contact_model_from_python.backup_user_id) is UserId}"
    )

    print_section("2. exported payload")

    print(f"model_dump() result               : {dumped_python}")
    print(f"model_dump_json() result          : {dumped_json}")
    print(f"json.loads(...) result            : {loaded_from_json}")

    print_value_state(
        "dumped_python['primary_user_id']", dumped_python["primary_user_id"]
    )
    print_value_state(
        "loaded_from_json['primary_user_id']",
        loaded_from_json["primary_user_id"],
    )

    print(
        f"python dump contains plain str    : "
        f"{type(dumped_python['primary_user_id']) is str}"
    )
    print(
        f"json payload contains plain str   : "
        f"{type(loaded_from_json['primary_user_id']) is str}"
    )

    print_section("3. validation rebuilds exact subtype")

    print_value_state(
        "restored_from_python_dump.primary_user_id",
        restored_from_python_dump.primary_user_id,
    )
    print_value_state(
        "restored_from_json_payload.primary_user_id",
        restored_from_json_payload.primary_user_id,
    )

    print(
        f"restored from python dump         : "
        f"{type(restored_from_python_dump.primary_user_id) is UserId}"
    )
    print(
        f"restored from json payload        : "
        f"{type(restored_from_json_payload.primary_user_id) is UserId}"
    )

    print_section("4. JSON validation boundary")

    canonical_json_payload: str = (
        '{"primary_user_id":"user_123e4567-e89b-42d3-a456-426614174000",'
        '"backup_user_id":"user_123e4567-e89b-42d3-a456-426614174001"}'
    )
    ContactModel.model_validate_json(canonical_json_payload)
    print("canonical prefixed JSON is valid  : True")

    try:
        ContactModel.model_validate_json(
            '{"primary_user_id":"123e4567-e89b-42d3-a456-426614174000",'
            '"backup_user_id":"123e4567-e89b-42d3-a456-426614174001"}'
        )
    except ValidationError:
        print("plain UUID JSON is valid          : False")


if __name__ == "__main__":
    main()
