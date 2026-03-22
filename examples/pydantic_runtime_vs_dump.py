from __future__ import annotations

import json

from pydantic import BaseModel

from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


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
    contact_model: ContactModel = ContactModel.model_validate(
        {
            "primary_user_id": "123e4567-e89b-42d3-a456-426614174000",
            "backup_user_id": "123e4567-e89b-42d3-a456-426614174001",
        }
    )

    dumped_python: dict[str, object] = contact_model.model_dump()
    dumped_json: str = contact_model.model_dump_json()
    loaded_from_json: dict[str, object] = json.loads(dumped_json)

    primary_user_id_from_dump: object = dumped_python["primary_user_id"]
    backup_user_id_from_dump: object = dumped_python["backup_user_id"]

    primary_user_id_from_json_payload: object = loaded_from_json["primary_user_id"]
    backup_user_id_from_json_payload: object = loaded_from_json["backup_user_id"]

    print_section("1. runtime values inside pydantic model")

    print_value_state("contact_model.primary_user_id", contact_model.primary_user_id)
    print_value_state("contact_model.backup_user_id", contact_model.backup_user_id)

    print(
        f"primary_user_id exact subtype kept: "
        f"{type(contact_model.primary_user_id) is UserId}"
    )
    print(
        f"backup_user_id exact subtype kept : "
        f"{type(contact_model.backup_user_id) is UserId}"
    )

    print_section("2. python dump")

    print(f"model_dump() result               : {dumped_python}")
    print_value_state("primary_user_id_from_dump", primary_user_id_from_dump)
    print_value_state("backup_user_id_from_dump", backup_user_id_from_dump)

    print(
        f"primary_user_id flattened to str  : "
        f"{type(primary_user_id_from_dump) is str}"
    )
    print(
        f"backup_user_id flattened to str   : "
        f"{type(backup_user_id_from_dump) is str}"
    )

    print_section("3. json dump")

    print(f"model_dump_json() result          : {dumped_json}")
    print(f"json.loads(...) result            : {loaded_from_json}")

    print_value_state(
        "primary_user_id_from_json_payload",
        primary_user_id_from_json_payload,
    )
    print_value_state(
        "backup_user_id_from_json_payload",
        backup_user_id_from_json_payload,
    )

    print(
        f"json payload contains plain str   : "
        f"{type(primary_user_id_from_json_payload) is str}"
    )
    print(
        f"json payload contains plain str   : "
        f"{type(backup_user_id_from_json_payload) is str}"
    )

    print_section("4. final verdict")

    print("inside model                      : exact subtype is preserved")
    print("after model_dump()                : exported payload is plain str")
    print("after model_dump_json()           : exported payload is plain str")
    print(
        f"original model still keeps subtype: "
        f"{type(contact_model.primary_user_id) is UserId}"
    )


if __name__ == "__main__":
    main()