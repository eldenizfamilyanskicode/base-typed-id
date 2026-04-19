from __future__ import annotations

import re
from re import Pattern
from typing import Any, ClassVar, Literal, TypeVar
from uuid import UUID, uuid4

from ._exceptions import (
    BaseTypedIdInvalidInputValueError,
    BaseTypedIdInvariantViolationError,
)

BasePrefixedTypedIdType = TypeVar(
    "BasePrefixedTypedIdType",
    bound="BasePrefixedTypedId",
)


class BasePrefixedTypedId(str):
    """
    Transparent domain-typed identifier with a class-level canonical prefix.

    Canonical runtime form:
    - "<prefix>_<uuid>"

    Rules:
    - prefix is a class-level invariant
    - prefix must be canonical lowercase snake case
    - regex is class-level and derived from prefix
    - stores exact runtime subtype
    - serializes as plain str
    """

    __slots__ = ()

    uuid_version: ClassVar[Literal[1, 3, 4, 5, 6, 7, 8] | None] = 4
    prefix: ClassVar[str] = ""
    prefix_regex: ClassVar[Pattern[str]] = re.compile(
        r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$"
    )
    regex: ClassVar[Pattern[str]] = re.compile(r"^$")

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if "regex" in cls.__dict__:
            raise BaseTypedIdInvariantViolationError(
                f"{cls.__name__}.regex is derived from {cls.__name__}.prefix and "
                "cannot be overridden."
            )

        if "prefix" not in cls.__dict__:
            raise BaseTypedIdInvariantViolationError(
                f"{cls.__name__} must declare a class-level prefix."
            )

        declared_prefix: object = cls.__dict__["prefix"]
        if not isinstance(declared_prefix, str):
            raise BaseTypedIdInvariantViolationError(
                f"{cls.__name__}.prefix must be a str."
            )

        if not cls.prefix_regex.fullmatch(declared_prefix):
            raise BaseTypedIdInvariantViolationError(
                f"{cls.__name__}.prefix must be canonical lowercase snake case. "
                f"Got: {declared_prefix!r}."
            )

        cls.regex = re.compile(
            "^"
            + re.escape(declared_prefix)
            + "_"
            + r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
            + "$"
        )

    def __new__(
        cls: type[BasePrefixedTypedIdType],
        value: str | UUID | None = None,
    ) -> BasePrefixedTypedIdType:
        parsed_uuid_value: UUID
        canonical_value: str

        if value is None:
            if cls.uuid_version not in (None, 4):
                raise BaseTypedIdInvalidInputValueError(
                    f"{cls.__name__} cannot auto-generate from None when "
                    f"uuid_version is {cls.uuid_version!r}. "
                    "Provide an explicit UUID value."
                )

            parsed_uuid_value = uuid4()
            canonical_value = f"{cls.prefix}_{parsed_uuid_value}"

        elif isinstance(value, UUID):
            parsed_uuid_value = value
            canonical_value = f"{cls.prefix}_{parsed_uuid_value}"

        # Runtime guard is intentional because the library is callable from untyped code
        elif isinstance(value, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            prefixed_match: re.Match[str] | None = cls.regex.fullmatch(value)

            if prefixed_match is not None:
                uuid_text: str = value[len(cls.prefix) + 1 :]

                try:
                    parsed_uuid_value = UUID(uuid_text)
                except ValueError as validation_error:
                    raise BaseTypedIdInvariantViolationError(
                        f"{cls.__name__} matched its regex but contained an invalid "
                        f"UUID suffix: {value!r}."
                    ) from validation_error

                canonical_value = value
            else:
                try:
                    parsed_uuid_value = UUID(value)
                except ValueError as validation_error:
                    raise BaseTypedIdInvalidInputValueError(
                        f"{cls.__name__} must be initialized with None, uuid.UUID, "
                        f"a canonical '{cls.prefix}_<uuid>' string, or a UUID string. "
                        f"Got: {value!r}."
                    ) from validation_error

                canonical_value = f"{cls.prefix}_{parsed_uuid_value}"

        else:
            raise BaseTypedIdInvalidInputValueError(
                f"{cls.__name__} must be initialized with None, str, or uuid.UUID. "
                f"Got: {type(value).__name__}."
            )

        expected_uuid_version: int | None = cls.uuid_version
        if expected_uuid_version is not None:
            actual_uuid_version: int | None = parsed_uuid_value.version
            if actual_uuid_version != expected_uuid_version:
                raise BaseTypedIdInvalidInputValueError(
                    f"{cls.__name__} expects UUID v{expected_uuid_version}. "
                    f"Got UUID v{actual_uuid_version}: {parsed_uuid_value}."
                )

        return str.__new__(cls, canonical_value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)!r})"

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: Any,
    ) -> Any:
        del source_type
        del handler

        try:
            from pydantic_core import core_schema
        except ImportError as import_error:  # pragma: no cover
            raise BaseTypedIdInvariantViolationError(
                "pydantic-core is required to build BasePrefixedTypedId schema."
            ) from import_error

        def serialize_to_plain_string(value: BasePrefixedTypedId) -> str:
            return str(value)

        python_input_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(UUID),
                core_schema.str_schema(strict=True),
            ]
        )

        json_input_schema = core_schema.str_schema(
            strict=True,
            pattern=cls.regex.pattern,
        )

        return core_schema.json_or_python_schema(
            json_schema=core_schema.no_info_after_validator_function(
                cls,
                json_input_schema,
            ),
            python_schema=core_schema.no_info_after_validator_function(
                cls,
                python_input_schema,
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_to_plain_string,
                return_schema=core_schema.str_schema(),
            ),
        )

    def __getnewargs__(self) -> tuple[str]:
        return (str(self),)

    def __reduce__(self) -> tuple[type[BasePrefixedTypedId], tuple[str]]:
        return (self.__class__, (str(self),))
