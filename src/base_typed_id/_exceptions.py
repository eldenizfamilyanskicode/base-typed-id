class BaseTypedIdError(Exception):
    """Root exception for all base_typed_id errors."""


class BaseTypedIdInvalidInputValueError(BaseTypedIdError, ValueError):
    """Raised when an invalid input value is provided."""


class BaseTypedIdInvariantViolationError(BaseTypedIdError):
    """Raised when an internal invariant or contract is violated."""