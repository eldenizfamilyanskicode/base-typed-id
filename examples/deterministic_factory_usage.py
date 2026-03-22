from __future__ import annotations

from base_typed_id import BaseTypedId
from base_typed_id.factories import deterministically_from_words


class ExternalEventId(BaseTypedId):
    uuid_version = 5


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
    print_section("deterministic factory produces stable typed UUID v5")

    first_event_id: ExternalEventId = deterministically_from_words(
        ExternalEventId,
        words=[
            "workspace:house-of-ai",
            "provider:telegram",
            "event:message-created",
            "message:42",
        ],
    )
    second_event_id: ExternalEventId = deterministically_from_words(
        ExternalEventId,
        words=[
            "workspace:house-of-ai",
            "provider:telegram",
            "event:message-created",
            "message:42",
        ],
    )
    reordered_event_id: ExternalEventId = deterministically_from_words(
        ExternalEventId,
        words=[
            "message:42",
            "event:message-created",
            "provider:telegram",
            "workspace:house-of-ai",
        ],
    )

    print_value_state("first_event_id", first_event_id)
    print_value_state("second_event_id", second_event_id)
    print_value_state("reordered_event_id", reordered_event_id)

    print(f"same words -> same id             : {first_event_id == second_event_id}")
    print(f"order matters                     : {first_event_id != reordered_event_id}")
    print(
        f"exact subtype preserved           : {type(first_event_id) is ExternalEventId}"
    )


if __name__ == "__main__":
    main()
