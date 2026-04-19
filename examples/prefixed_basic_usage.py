from __future__ import annotations

from uuid import UUID

from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


class WorkspaceId(BasePrefixedTypedId):
    prefix = "workspace"


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

    user_id_from_plain_uuid_string: UserId = UserId(
        "123e4567-e89b-42d3-a456-426614174000"
    )
    user_id_from_prefixed_string: UserId = UserId(
        "user_123e4567-e89b-42d3-a456-426614174001"
    )
    user_id_from_uuid: UserId = UserId(UUID("123e4567-e89b-42d3-a456-426614174002"))
    generated_user_id: UserId = UserId()

    expected_user_id_from_plain_uuid_string: str = (
        "user_123e4567-e89b-42d3-a456-426614174000"
    )
    expected_user_id_from_prefixed_string: str = (
        "user_123e4567-e89b-42d3-a456-426614174001"
    )

    print_value_state(
        "user_id_from_plain_uuid_string",
        user_id_from_plain_uuid_string,
    )
    print_value_state("user_id_from_prefixed_string", user_id_from_prefixed_string)
    print_value_state("user_id_from_uuid", user_id_from_uuid)
    print_value_state("generated_user_id", generated_user_id)

    print(
        f"plain UUID string canonicalized   : "
        f"{user_id_from_plain_uuid_string == expected_user_id_from_plain_uuid_string}"
    )
    print(
        f"prefixed string preserved         : "
        f"{user_id_from_prefixed_string == expected_user_id_from_prefixed_string}"
    )
    print(f"generated_user_id exact subtype   : {type(generated_user_id) is UserId}")
    print(
        f"generated_user_id UUID v4         : "
        f"{UUID(str(generated_user_id).split('_', maxsplit=1)[1]).version == 4}"
    )


def demonstrate_container_and_attribute_behavior() -> None:
    print_section("2. containers and class attributes")

    source_user_id: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")
    source_workspace_id: WorkspaceId = WorkspaceId(
        "workspace_123e4567-e89b-42d3-a456-426614174010"
    )

    user_id_list: list[UserId] = [source_user_id]
    values_by_user_id: dict[str, str] = {
        source_user_id: "present",
    }
    values_by_workspace_id: dict[str, str] = {
        source_workspace_id: "active",
    }

    retrieved_user_id: UserId = user_id_list[0]
    retrieved_by_typed_key: str = values_by_user_id[source_user_id]
    retrieved_by_plain_string_key: str = values_by_user_id[
        "user_123e4567-e89b-42d3-a456-426614174000"
    ]
    retrieved_workspace_value: str = values_by_workspace_id[
        "workspace_123e4567-e89b-42d3-a456-426614174010"
    ]

    print_value_state("source_user_id", source_user_id)
    print_value_state("retrieved_user_id", retrieved_user_id)

    print(f"list keeps same object            : {retrieved_user_id is source_user_id}")
    print(f"typed key lookup works            : {retrieved_by_typed_key == 'present'}")
    print(
        f"plain str key lookup works        : "
        f"{retrieved_by_plain_string_key == 'present'}"
    )
    print(
        f"second prefixed type also works   : {retrieved_workspace_value == 'active'}"
    )


def demonstrate_normal_string_operations() -> None:
    print_section("3. normal string operations")

    user_id: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")

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
