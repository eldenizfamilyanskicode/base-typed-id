from __future__ import annotations

import pickle

from base_typed_id import BaseTypedId


class EmailId(BaseTypedId):
    pass


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
    print_section("pickle roundtrip preserves exact subtype")

    source_email_id: EmailId = EmailId("123e4567-e89b-42d3-a456-426614174000")
    serialized_email_id: bytes = pickle.dumps(source_email_id)
    restored_email_id: object = pickle.loads(serialized_email_id)

    print_value_state("source_email_id", source_email_id)
    print_value_state("restored_email_id", restored_email_id)

    print(
        f"plain value preserved             : "
        f"{restored_email_id == '123e4567-e89b-42d3-a456-426614174000'}"
    )
    print(f"exact subtype preserved           : {type(restored_email_id) is EmailId}")
    print(f"isinstance(restored_email_id, str): {isinstance(restored_email_id, str)}")
    print(
        f"isinstance(restored_email_id, EmailId): "
        f"{isinstance(restored_email_id, EmailId)}"
    )
    print(f"serialized byte length            : {len(serialized_email_id)}")


if __name__ == "__main__":
    main()