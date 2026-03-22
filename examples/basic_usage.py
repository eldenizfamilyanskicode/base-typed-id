from __future__ import annotations

from uuid import UUID

from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


class Account:
    def __init__(self, user_id: UserId) -> None:
        self.user_id: UserId = user_id


def print_section(title: str) -> None:
    separator: str = "=" * len(title)
    print()
    print(separator)
    print(title)
    print(separator)


def print_value_state(label: str, value: object) -> None:
    print(f"{label}:")
    print(f"  repr                  : {value!r}")
    print(f"  runtime type          : {type(value).__name__}")
    print(f"  isinstance(value, str): {isinstance(value, str)}")
    print()


def demonstrate_direct_runtime_identity() -> None:
    print_section("1. direct construction")

    user_id_from_string: UserId = UserId(
        "123e4567-e89b-42d3-a456-426614174000"
    )
    user_id_from_uuid: UserId = UserId(
        UUID("123e4567-e89b-42d3-a456-426614174001")
    )
    generated_user_id: UserId = UserId()

    print_value_state("user_id_from_string", user_id_from_string)
    print_value_state("user_id_from_uuid", user_id_from_uuid)
    print_value_state("generated_user_id", generated_user_id)

    print(
        f"user_id_from_string exact subtype : "
        f"{type(user_id_from_string) is UserId}"
    )
    print(
        f"user_id_from_uuid exact subtype   : "
        f"{type(user_id_from_uuid) is UserId}"
    )
    print(
        f"generated_user_id exact subtype   : "
        f"{type(generated_user_id) is UserId}"
    )
    print(
        f"generated_user_id is UUID v4      : "
        f"{UUID(str(generated_user_id)).version == 4}"
    )


def demonstrate_container_and_attribute_behavior() -> None:
    print_section("2. containers and class attributes")

    source_user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")

    user_id_list: list[UserId] = [source_user_id]
    user_id_by_field_name: dict[str, UserId] = {
        "user_id": source_user_id,
    }
    values_by_user_id: dict[str, str] = {
        source_user_id: "present",
    }
    account: Account = Account(user_id=source_user_id)

    retrieved_from_list: UserId = user_id_list[0]
    retrieved_from_dict_value: UserId = user_id_by_field_name["user_id"]
    retrieved_from_attribute: UserId = account.user_id
    retrieved_by_typed_key: str = values_by_user_id[source_user_id]
    retrieved_by_plain_string_key: str = values_by_user_id[
        "123e4567-e89b-42d3-a456-426614174000"
    ]

    stored_keys: tuple[str, ...] = tuple(values_by_user_id.keys())
    stored_key_object: str = stored_keys[0]

    print_value_state("source_user_id", source_user_id)
    print_value_state("retrieved_from_list", retrieved_from_list)
    print_value_state("retrieved_from_dict_value", retrieved_from_dict_value)
    print_value_state("retrieved_from_attribute", retrieved_from_attribute)
    print_value_state("stored_key_object", stored_key_object)

    print(
        f"list keeps same object            : "
        f"{retrieved_from_list is source_user_id}"
    )
    print(
        f"dict value keeps same object      : "
        f"{retrieved_from_dict_value is source_user_id}"
    )
    print(
        f"class attribute keeps same object : "
        f"{retrieved_from_attribute is source_user_id}"
    )
    print(
        f"dict key object is same object    : "
        f"{stored_key_object is source_user_id}"
    )
    print(f"typed key lookup works            : {retrieved_by_typed_key == 'present'}")
    print(
        f"plain str key lookup works        : "
        f"{retrieved_by_plain_string_key == 'present'}"
    )
    print(f"stored key exact subtype kept     : {type(stored_key_object) is UserId}")


def demonstrate_normal_string_operations() -> None:
    print_section("3. normal string operations")

    user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")

    uppercased_value: str = user_id.upper()
    replaced_value: str = user_id.replace("-", "_")
    concatenated_value: str = user_id + "_debug"

    print_value_state("user_id", user_id)
    print_value_state("uppercased_value", uppercased_value)
    print_value_state("replaced_value", replaced_value)
    print_value_state("concatenated_value", concatenated_value)

    print(f"type(uppercased_value) is str     : {type(uppercased_value) is str}")
    print(f"type(replaced_value) is str       : {type(replaced_value) is str}")
    print(f"type(concatenated_value) is str   : {type(concatenated_value) is str}")
    print("verdict                           : normal str operations return plain str")


def main() -> None:
    demonstrate_direct_runtime_identity()
    demonstrate_container_and_attribute_behavior()
    demonstrate_normal_string_operations()


if __name__ == "__main__":
    main()