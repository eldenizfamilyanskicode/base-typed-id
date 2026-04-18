from __future__ import annotations

from typing import Any, ClassVar, Literal, TypeVar
from uuid import UUID, uuid4

from ._exceptions import (
    BaseTypedIdInvalidInputValueError,
    BaseTypedIdInvariantViolationError,
)

BaseTypedIdType = TypeVar(
    "BaseTypedIdType",
    bound="BaseTypedId",
)


class BaseTypedId(str):
    """
    Transparent domain-typed identifier based on UUID.

    Design rules:
    - stores an exact runtime subtype
    - serializes as plain str
    - preserves subtype in containers, pickle, and Pydantic model fields
    - uses native pydantic-core uuid schema for OpenAPI format "uuid"
    - defaults to UUID v4 and auto-generates on None
    """

    __slots__ = ()

    uuid_version: ClassVar[Literal[1, 3, 4, 5, 6, 7, 8] | None] = 4

    def __new__(
        cls: type[BaseTypedIdType],
        value: str | UUID | None = None,
    ) -> BaseTypedIdType:
        parsed_uuid_value: UUID = cls._parse_uuid_value(value=value)
        cls._validate_uuid_version(parsed_uuid_value=parsed_uuid_value)
        return str.__new__(cls, str(parsed_uuid_value))

    @classmethod
    def _parse_uuid_value(
        cls,
        value: str | UUID | None,
    ) -> UUID:
        if value is None:
            if cls.uuid_version not in (None, 4):
                raise BaseTypedIdInvalidInputValueError(
                    f"{cls.__name__} cannot auto-generate from None when "
                    f"uuid_version is {cls.uuid_version!r}. "
                    "Provide an explicit UUID value."
                )
            return uuid4()

        if isinstance(value, UUID):
            return value

        # Runtime guard is intentional because the library is callable from untyped code
        if not isinstance(value, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise BaseTypedIdInvalidInputValueError(
                "BaseTypedId must be initialized with None, str, or uuid.UUID. "
                f"Got: {type(value).__name__}."
            )

        try:
            return UUID(value)
        except ValueError as validation_error:
            raise BaseTypedIdInvalidInputValueError(
                "BaseTypedId must be initialized with a valid UUID string. "
                f"Got: {value!r}."
            ) from validation_error

    @classmethod
    def _validate_uuid_version(
        cls,
        parsed_uuid_value: UUID,
    ) -> None:
        expected_uuid_version: int | None = cls.uuid_version
        if expected_uuid_version is None:
            return

        actual_uuid_version: int | None = parsed_uuid_value.version
        if actual_uuid_version != expected_uuid_version:
            raise BaseTypedIdInvalidInputValueError(
                f"{cls.__name__} expects UUID v{expected_uuid_version}. "
                f"Got UUID v{actual_uuid_version}: {parsed_uuid_value}."
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)!r})"

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: Any,
    ) -> Any:
        """
        Provide Pydantic v2 validation and serialization.

        Validation:
        - accepts UUID objects
        - accepts strict UUID strings
        - rejects bytes and other non-declared runtime inputs
        - returns the exact subclass instance

        Serialization:
        - serializes as plain str in both python and json dump modes

        Schema:
        - uses native uuid schema for JSON/OpenAPI, so format stays `uuid`
        """
        del source_type
        del handler

        try:
            from pydantic_core import core_schema
        except ImportError as import_error:  # pragma: no cover
            raise BaseTypedIdInvariantViolationError(
                "pydantic-core is required to build BaseTypedId schema."
            ) from import_error

        def serialize_to_plain_string(value: BaseTypedId) -> str:
            return str(value)

        python_input_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(UUID),
                core_schema.str_schema(strict=True),
            ]
        )

        json_input_schema = core_schema.uuid_schema(version=cls.uuid_version)

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

    def __reduce__(
        self,
    ) -> tuple[type[BaseTypedId], tuple[str]]:
        return (self.__class__, (str(self),))
