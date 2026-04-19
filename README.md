# base-typed-id

`base_typed_id` is a small Python library for building domain-specific UUID identifier types that remain real `str` objects at runtime.

It provides two base classes:

* `BaseTypedId` for plain UUID-backed typed identifiers
* `BasePrefixedTypedId` for canonical prefixed identifiers like `user_<uuid>`

Strict typed UUID identifier base classes with exact runtime subtype preservation and optional Pydantic v2 support.

---

## Why

Sometimes an identifier is semantically important enough to deserve its own type, but operationally it should still behave like a normal string.

Examples:

* `UserId`
* `OrderId`
* `ExternalEventId`
* `WorkspaceId`
* `IntegrationId`

Sometimes you want plain UUID text:

* `123e4567-e89b-42d3-a456-426614174000`

Sometimes you want a canonical prefixed form:

* `user_123e4567-e89b-42d3-a456-426614174000`
* `workspace_123e4567-e89b-42d3-a456-426614174000`

Using plain `str` everywhere loses domain meaning.
Using plain `uuid.UUID` changes runtime behavior.
Using wrappers adds interoperability friction.
Using `NewType` helps only static typing.

`base_typed_id` gives you a middle ground:
domain-specific UUID-backed identifiers with validation, while keeping real `str` behavior at runtime.

---

## What it provides

### `BaseTypedId`

A transparent domain-typed UUID identifier.

Canonical runtime form:

* `<uuid>`

Example:

```python
from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass
```

Runtime value:

```python
UserId("123e4567-e89b-42d3-a456-426614174000")
```

### `BasePrefixedTypedId`

A transparent domain-typed UUID identifier with a class-level canonical prefix.

Canonical runtime form:

* `<prefix>_<uuid>`

Example:

```python
from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"
```

Runtime value:

```python
UserId("user_123e4567-e89b-42d3-a456-426614174000")
```

---

## What it guarantees

### Shared guarantees

Both base classes:

* accept valid UUID strings and `uuid.UUID` values
* support auto-generation when called without an explicit value when `uuid_version` is `4` or `None`
* validate UUID structure at construction time
* preserve the exact subclass type at construction and validation boundaries
* behave like normal `str`
* normal string operations return plain `str`
* preserve subtype through pickle roundtrip
* support Pydantic v2, but do not require it
* serialize and export as plain string
* ship `py.typed`

### Additional guarantees for `BaseTypedId`

* canonical runtime form is plain UUID text
* Pydantic / OpenAPI schema uses:

  * `type: string`
  * `format: uuid`

### Additional guarantees for `BasePrefixedTypedId`

* canonical runtime form is `<prefix>_<uuid>`
* prefix is a class-level invariant
* prefix must be canonical lowercase snake case
* regex is derived from the declared prefix and cannot be overridden
* Pydantic / OpenAPI schema uses:

  * `type: string`
  * `pattern: ^<prefix>_<uuid-regex>$`

---

## What it intentionally does not do

* no built-in domain rules beyond UUID parsing, prefix invariants, and optional version checks
* no normalization layer beyond canonical runtime construction
* no non-UUID identifier support
* no domain-specific methods
* no wrapper objects
* no built-in deterministic factory for prefixed identifiers in the current implementation

This package is intentionally minimal.

Domain rules should live in your subclasses or in your application layer.

---

## Why not plain `str` / `uuid.UUID` / `NewType` / `Annotated` / custom wrapper?

### Why not plain `str`?

Because plain `str` does not communicate domain intent.

```python
def get_user(user_id: str, workspace_id: str) -> None:
    ...
```

This is easy to misuse:

* parameters can be swapped accidentally
* type annotations do not explain domain meaning
* static analysis cannot distinguish semantic identifier types

With typed subclasses:

```python
def get_user(user_id: UserId, workspace_id: WorkspaceId) -> None:
    ...
```

the intent is explicit.

### Why not `uuid.UUID`?

`uuid.UUID` validates structure, but it is not the same thing as a domain identifier type.

```python
from uuid import UUID

def get_user(user_id: UUID, workspace_id: UUID) -> None:
    ...
```

This still loses semantic distinction:

* `user_id` and `workspace_id` are the same runtime type
* static analysis cannot distinguish one UUID-based domain identifier from another
* annotations do not preserve domain meaning
* exported JSON often requires explicit conversion to string
* many integrations expect plain `str`, not `UUID`
* exact domain subtype identity such as `type(user_id) is UserId` is not available

`base_typed_id` keeps UUID validation while preserving domain-specific type identity and plain string interoperability.

### Why not `typing.NewType`?

`NewType` is a static typing tool, not a runtime type.

```python
from typing import NewType

UserId = NewType("UserId", str)

user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")

assert type(user_id) is str
assert isinstance(user_id, str)
```

This means:

* runtime values are still plain `str`
* there is no real subclass at runtime
* runtime boundaries cannot preserve a concrete semantic subtype
* introspection and runtime behavior cannot distinguish `UserId` from plain `str`
* UUID validation is not part of construction

`base_typed_id` creates a real runtime subtype with UUID validation.

### Why not `Annotated[str, ...]`?

`Annotated` can attach metadata for validators and frameworks, but it still does not create a distinct runtime type.

That means:

* runtime values are still plain `str`
* `type(value)` is not your domain identifier type
* exact subtype identity is not preserved inside Python objects

If you need runtime identity such as `type(user_id) is UserId`, `Annotated[str, ...]` is not enough.

### Why not a custom wrapper class?

A wrapper can model a domain value, but it stops being a real string.

Typical trade-offs:

* `isinstance(value, str)` becomes `False`
* JSON serialization often needs custom handling
* many libraries expect plain `str`, not wrapper objects
* you often need explicit `.value` extraction
* interoperability becomes noisier

A wrapper is useful when you want rich behavior and strict encapsulation.

`base_typed_id` is for the opposite case:
keep the identifier operationally identical to `str`, while still having a named domain type with UUID guarantees.

### When `base_typed_id` is the right choice

Use it when you want:

* semantic identifier types in annotations
* UUID validation at construction and validation boundaries
* real `str` behavior at runtime
* plain string serialization
* clean interoperability with Python and library code
* Pydantic / OpenAPI compatibility

Use `BaseTypedId` when you want plain UUID runtime strings.

Use `BasePrefixedTypedId` when you want canonical prefixed runtime strings.

Do not use it when you need:

* heavy domain logic on the identifier itself
* mutable state
* multiple fields
* non-UUID runtime representation
* non-UUID identifiers

---

## Installation

### Base package

```bash
pip install base-typed-id
```

### With Pydantic v2 support

```bash
pip install "base-typed-id[pydantic]"
```

### For development

```bash
pip install "base-typed-id[dev]"
```

---

## Quick start

### Plain UUID typed identifier

```python
from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")
generated_user_id: UserId = UserId()

assert user_id == "123e4567-e89b-42d3-a456-426614174000"
assert isinstance(user_id, str)
assert isinstance(user_id, UserId)
assert type(user_id) is UserId
assert type(generated_user_id) is UserId
```

### Prefixed typed identifier

```python
from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


user_id_from_plain_uuid: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")
user_id_from_prefixed_string: UserId = UserId(
    "user_123e4567-e89b-42d3-a456-426614174000"
)
generated_user_id: UserId = UserId()

assert user_id_from_plain_uuid == "user_123e4567-e89b-42d3-a456-426614174000"
assert user_id_from_prefixed_string == "user_123e4567-e89b-42d3-a456-426614174000"
assert isinstance(user_id_from_plain_uuid, str)
assert isinstance(user_id_from_plain_uuid, UserId)
assert type(user_id_from_plain_uuid) is UserId
assert type(generated_user_id) is UserId
```

---

## How to use it in your project

Create a module for your domain identifier types.

For example, create a file named `domain_identifiers.py`:

```python
from base_typed_id import BasePrefixedTypedId, BaseTypedId


class UserId(BasePrefixedTypedId):
    """User identifier."""

    prefix = "user"


class WorkspaceId(BasePrefixedTypedId):
    """Workspace identifier."""

    prefix = "workspace"


class ExternalEventId(BaseTypedId):
    """External event identifier."""

    uuid_version = 5
```

Then use these types in your application code:

```python
from .domain_identifiers import ExternalEventId, UserId, WorkspaceId


def get_user(
    user_id: UserId,
    workspace_id: WorkspaceId,
    external_event_id: ExternalEventId,
) -> None:
    print(user_id, workspace_id, external_event_id)
```

This gives you:

* domain-specific names in type annotations
* UUID validation at boundaries
* real `str` values at runtime
* plain string serialization behavior
* reconstruction through validation layers such as Pydantic

---

## Runtime behavior

Both base classes are real `str` subclasses backed by UUID validation.

### `BaseTypedId`

```python
from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")

assert isinstance(user_id, str)
assert isinstance(user_id, UserId)
assert type(user_id) is UserId
assert user_id == "123e4567-e89b-42d3-a456-426614174000"
```

### `BasePrefixedTypedId`

```python
from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")

assert isinstance(user_id, str)
assert isinstance(user_id, UserId)
assert type(user_id) is UserId
assert user_id == "user_123e4567-e89b-42d3-a456-426614174000"
```

### Normal string operations return plain `str`

```python
from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


user_id: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")

uppercased_value: str = user_id.upper()
concatenated_value: str = user_id + "_debug"
replaced_value: str = user_id.replace("-", "_")

assert type(uppercased_value) is str
assert type(concatenated_value) is str
assert type(replaced_value) is str
```

This behavior is intentional.

The typed subtype is preserved at construction and validation boundaries, not across ordinary string operations.

---

## Constructor rules

## `BaseTypedId`

Valid inputs are:

* no argument
* UUID string
* `uuid.UUID`

Calling the constructor without an argument auto-generates a UUID when `uuid_version` is `4` or `None`.

```python
from uuid import UUID

from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


value_from_string: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")
value_from_uuid: UserId = UserId(UUID("123e4567-e89b-42d3-a456-426614174000"))
generated_value: UserId = UserId()
```

## `BasePrefixedTypedId`

Valid inputs are:

* no argument
* canonical prefixed UUID string
* raw UUID string
* `uuid.UUID`

Calling the constructor without an argument auto-generates a UUID when `uuid_version` is `4` or `None`.

```python
from uuid import UUID

from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


value_from_prefixed_string: UserId = UserId(
    "user_123e4567-e89b-42d3-a456-426614174000"
)
value_from_plain_uuid_string: UserId = UserId(
    "123e4567-e89b-42d3-a456-426614174000"
)
value_from_uuid: UserId = UserId(UUID("123e4567-e89b-42d3-a456-426614174000"))
generated_value: UserId = UserId()

assert value_from_prefixed_string == "user_123e4567-e89b-42d3-a456-426614174000"
assert value_from_plain_uuid_string == "user_123e4567-e89b-42d3-a456-426614174000"
assert value_from_uuid == "user_123e4567-e89b-42d3-a456-426614174000"
```

Invalid input raises `BaseTypedIdInvalidInputValueError`.

```python
from base_typed_id import (
    BasePrefixedTypedId,
    BaseTypedId,
    BaseTypedIdInvalidInputValueError,
)


class UserId(BaseTypedId):
    pass


class PrefixedUserId(BasePrefixedTypedId):
    prefix = "user"


try:
    UserId("not-a-uuid")
except BaseTypedIdInvalidInputValueError:
    pass

try:
    PrefixedUserId("user_not-a-uuid")
except BaseTypedIdInvalidInputValueError:
    pass

try:
    PrefixedUserId(123)
except BaseTypedIdInvalidInputValueError:
    pass
```

---

## Prefix rules for `BasePrefixedTypedId`

Each concrete subclass must declare its own class-level `prefix`.

```python
from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"
```

Rules:

* `prefix` must be declared directly on the subclass
* `prefix` must be a `str`
* `prefix` must be canonical lowercase snake case
* `regex` is derived from `prefix`
* `regex` cannot be overridden

Examples of invalid subclasses:

```python
from base_typed_id import BasePrefixedTypedId


class MissingPrefix(BasePrefixedTypedId):
    pass
```

```python
from base_typed_id import BasePrefixedTypedId


class InvalidPrefixType(BasePrefixedTypedId):
    prefix = 123
```

```python
from base_typed_id import BasePrefixedTypedId


class InvalidPrefixFormat(BasePrefixedTypedId):
    prefix = "User"
```

```python
import re

from base_typed_id import BasePrefixedTypedId


class InvalidRegexOverride(BasePrefixedTypedId):
    prefix = "user"
    regex = re.compile("^custom$")
```

These raise `BaseTypedIdInvariantViolationError`.

---

## UUID version control

By default, both base classes enforce UUID v4.

```python
from base_typed_id import BasePrefixedTypedId, BaseTypedId


class UserId(BaseTypedId):
    pass


class WorkspaceId(BasePrefixedTypedId):
    prefix = "workspace"
```

Use another version explicitly:

```python
from base_typed_id import BasePrefixedTypedId, BaseTypedId


class ExternalEventId(BaseTypedId):
    uuid_version = 5


class ImportedEntityId(BasePrefixedTypedId):
    prefix = "imported_entity"
    uuid_version = 5
```

Disable version restriction:

```python
from base_typed_id import BasePrefixedTypedId, BaseTypedId


class FlexibleId(BaseTypedId):
    uuid_version = None


class FlexiblePrefixedId(BasePrefixedTypedId):
    prefix = "flexible"
    uuid_version = None
```

When `uuid_version` is not `4` or `None`, auto-generation from `None` is intentionally rejected.

---

## Deterministic identifiers

For idempotent identifiers, the package provides `deterministically_from_words`.

This factory currently works with `BaseTypedId` subclasses.

```python
from base_typed_id import BaseTypedId, deterministically_from_words


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

Properties:

* same words -> same identifier
* order matters
* deterministic generation requires `uuid_version = 5` or `uuid_version = None`

---

## Pydantic v2 support

### `BaseTypedId`

When used as a Pydantic field type:

* validation accepts UUID objects and UUID strings
* runtime model values preserve the exact subtype
* exported payloads are plain strings
* generated schema keeps `type: string` and `format: uuid`

```python
from pydantic import BaseModel

from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


class UserModel(BaseModel):
    user_id: UserId


user_model: UserModel = UserModel.model_validate(
    {
        "user_id": "123e4567-e89b-42d3-a456-426614174000",
    }
)

assert type(user_model.user_id) is UserId

dumped_python: dict[str, object] = user_model.model_dump()

assert dumped_python == {
    "user_id": "123e4567-e89b-42d3-a456-426614174000",
}
assert type(dumped_python["user_id"]) is str
```

### `BasePrefixedTypedId`

When used as a Pydantic field type:

* Python-side validation accepts:

  * UUID objects
  * raw UUID strings
  * canonical prefixed strings
* runtime model values preserve the exact subtype
* exported payloads are plain strings
* generated schema keeps `type: string` and a prefix-derived `pattern`

```python
from pydantic import BaseModel

from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


class UserModel(BaseModel):
    user_id: UserId


user_model: UserModel = UserModel.model_validate(
    {
        "user_id": "123e4567-e89b-42d3-a456-426614174000",
    }
)

assert type(user_model.user_id) is UserId
assert user_model.user_id == "user_123e4567-e89b-42d3-a456-426614174000"

dumped_python: dict[str, object] = user_model.model_dump()

assert dumped_python == {
    "user_id": "user_123e4567-e89b-42d3-a456-426614174000",
}
assert type(dumped_python["user_id"]) is str
```

### Important boundary for `BasePrefixedTypedId`

Inside the validated model, the exact subtype is preserved.

After serialization or export, values intentionally become plain strings.

For JSON input validation through Pydantic, the current implementation accepts canonical prefixed strings and rejects raw UUID strings.

```python
from pydantic import BaseModel, ValidationError

from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


class UserModel(BaseModel):
    user_id: UserId


UserModel.model_validate_json(
    '{"user_id":"user_123e4567-e89b-42d3-a456-426614174000"}'
)

try:
    UserModel.model_validate_json(
        '{"user_id":"123e4567-e89b-42d3-a456-426614174000"}'
    )
except ValidationError:
    pass
```

This is a feature of the current schema design, not an accidental test artifact.

---

## Pickle support

Pickle roundtrip preserves the exact subtype for both base classes.

### `BaseTypedId`

```python
import pickle

from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


source_user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")
serialized_user_id: bytes = pickle.dumps(source_user_id)
restored_user_id: object = pickle.loads(serialized_user_id)

assert restored_user_id == "123e4567-e89b-42d3-a456-426614174000"
assert type(restored_user_id) is UserId
```

### `BasePrefixedTypedId`

```python
import pickle

from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


source_user_id: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")
serialized_user_id: bytes = pickle.dumps(source_user_id)
restored_user_id: object = pickle.loads(serialized_user_id)

assert restored_user_id == "user_123e4567-e89b-42d3-a456-426614174000"
assert type(restored_user_id) is UserId
```

---

## JSON behavior

Since both base classes inherit from `str`, standard JSON serialization naturally produces plain JSON strings.

### `BaseTypedId`

```python
import json

from base_typed_id import BaseTypedId


class UserId(BaseTypedId):
    pass


value: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")
serialized_value: str = json.dumps(value)
restored_value: object = json.loads(serialized_value)

assert serialized_value == '"123e4567-e89b-42d3-a456-426614174000"'
assert restored_value == "123e4567-e89b-42d3-a456-426614174000"
assert type(restored_value) is str
```

### `BasePrefixedTypedId`

```python
import json

from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


value: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")
serialized_value: str = json.dumps(value)
restored_value: object = json.loads(serialized_value)

assert serialized_value == '"user_123e4567-e89b-42d3-a456-426614174000"'
assert restored_value == "user_123e4567-e89b-42d3-a456-426614174000"
assert type(restored_value) is str
```

This behavior is intentional.

JSON is a plain data boundary.

The exact runtime subtype exists only inside Python objects.
After serialization, values become plain strings and do not carry subtype information.

---

## Public API

```python
from base_typed_id import BasePrefixedTypedId
from base_typed_id import BaseTypedId
from base_typed_id import BaseTypedIdError
from base_typed_id import BaseTypedIdInvalidInputValueError
from base_typed_id import BaseTypedIdInvariantViolationError
from base_typed_id import deterministically_from_words
```

### Exceptions

#### `BaseTypedIdError`

Root exception for all package-specific errors.

#### `BaseTypedIdInvalidInputValueError`

Raised when an invalid UUID input value is provided.

#### `BaseTypedIdInvariantViolationError`

Raised when an internal invariant or contract is violated.

---

## Examples

Current examples:

* `examples/basic_usage.py`
* `examples/deterministic_factory_usage.py`
* `examples/pickle_roundtrip.py`
* `examples/pydantic_roundtrip_from_dump.py`
* `examples/pydantic_runtime_vs_dump.py`
* `examples/prefixed_basic_usage.py`
* `examples/prefixed_pydantic_runtime_vs_dump.py`

---

## Design notes

`BaseTypedId` is intended for projects that want domain-specific UUID identifier names without giving up normal `str` runtime behavior.

`BasePrefixedTypedId` is intended for projects that want the same runtime behavior, but with canonical prefixed string values such as:

* `user_<uuid>`
* `workspace_<uuid>`
* `integration_<uuid>`

This is especially useful when you have many semantic identifiers such as:

* `UserId`
* `WorkspaceId`
* `OrderId`
* `ExternalEventId`
* `IntegrationId`

The base classes stay intentionally small so that your domain layer remains explicit and predictable.

---

## Development

### Run tests

```bash
pytest
```

### Run lint

```bash
ruff check .
```

### Run type checking

```bash
mypy src tests
pyright
```

### Build package

```bash
python -m build
```

### Validate distribution metadata

```bash
twine check dist/*
```

---

## Compatibility

* Python 3.10+
* CPython
* optional Pydantic v2 support

---

## License

MIT
