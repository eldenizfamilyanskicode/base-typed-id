# base-typed-id

`base_typed_id` is a small Python library for building domain-specific UUID-backed identifier types with exact runtime subtype preservation.

## Why

`BaseTypedId` lets you define domain-specific UUID-backed string subtypes such as `UserId`, `OrderId`, or `ExternalEventId`.

Goals:

- exact runtime subtype preservation
- plain `str` compatibility
- plain string serialization
- pickle roundtrip support
- Pydantic v2 support
- OpenAPI `format: uuid`

## Why not `NewType`, `Annotated[str, ...]`, or wrapper value objects?

There are several ways to model typed identifiers in Python. This library focuses on one specific trade-off: keeping a domain-specific runtime subtype while staying fully compatible with plain `str`.

### Why not `typing.NewType`?

`NewType` is excellent when you only need a static type distinction for type checkers.

However, at runtime a `NewType` value is still just a plain `str`. It does not:

- preserve an exact runtime subtype
- validate UUID format on construction
- provide subtype-preserving pickle behavior
- integrate as a real runtime subtype inside containers and model fields

Use `NewType` when static typing alone is enough.

### Why not `Annotated[str, ...]`?

`Annotated` is useful for attaching metadata to a type, especially for validators and frameworks.

But it still does not create a distinct runtime type. If you need runtime identity such as `type(user_id) is UserId`, `Annotated[str, ...]` is not enough.

### Why not wrapper value objects?

A wrapper class such as `UserId(value: str)` gives a stronger domain boundary and is often a good choice in rich domain models.

The trade-off is interoperability friction:

- it is no longer a plain string
- JSON serialization usually needs custom handling
- dictionary key compatibility is less transparent
- many integrations require explicit `.value` extraction

Use a wrapper when you want additional domain behavior beyond typed identity.

### What this library optimizes for

`BaseTypedId` is for the narrower case where you want all of the following at once:

- exact runtime subtype preservation
- plain `str` compatibility
- UUID parsing and version checks at the boundary
- plain string serialization
- Pydantic v2 / OpenAPI compatibility
- pickle roundtrip support

## When not to use this library

This library is not the best fit if:

- static-only type distinction is enough for you (`NewType` may be simpler)
- you want rich domain behavior on the identifier itself (a wrapper value object may be better)
- your identifiers are not UUID-based

## Installation

```bash
pip install base-typed-id
```

With Pydantic support:

```bash
pip install "base-typed-id[pydantic]"
```

## Basic usage

```python
from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")
generated_user_id: UserId = UserId()

assert type(user_id) is UserId
assert isinstance(user_id, str)
```

## UUID version control

By default, `BaseTypedId` expects UUID v4.

```python
from base_typed_id import BaseTypedId


class ExternalEventId(BaseTypedId):
    uuid_version = 5
```

`uuid_version = None` disables version restriction.

## Pydantic v2

```python
from pydantic import BaseModel

from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


class UserModel(BaseModel):
    user_id: UserId
```

Behavior:

* inside model: exact subtype is preserved
* after `model_dump()` / `model_dump_json()`: plain string is exported
* generated schema keeps `type: string` and `format: uuid`

## Deterministic identifiers

```python
from base_typed_id import BaseTypedId
from base_typed_id.factories import deterministically_from_words


class ExternalEventId(BaseTypedId):
    uuid_version = 5


event_id: ExternalEventId = deterministically_from_words(
    ExternalEventId,
    words=[
        "workspace:house-of-ai",
        "provider:telegram",
        "event:message-created",
        "message:42",
    ],
)
```

Rules:

* same words -> same identifier
* order matters
* deterministic generation requires `uuid_version = 5` or `uuid_version = None`

## Guarantees

* exact subtype is preserved in runtime objects
* exact subtype is preserved in containers
* exact subtype is preserved through pickle roundtrip
* serialized/exported representation is plain string

## Non-goals

* no extra domain behavior beyond typed identity
* no automatic semantic validation beyond UUID parsing/version checks
