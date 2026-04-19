from __future__ import annotations

import pickle

from base_typed_id import BasePrefixedTypedId


class UserId(BasePrefixedTypedId):
    prefix = "user"


def test_getnewargs_returns_plain_string_tuple() -> None:
    user_id: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")

    new_arguments: tuple[str] = user_id.__getnewargs__()

    assert new_arguments == ("user_123e4567-e89b-42d3-a456-426614174000",)


def test_pickle_roundtrip_preserves_exact_subtype() -> None:
    source_user_id: UserId = UserId("user_123e4567-e89b-42d3-a456-426614174000")

    serialized_user_id: bytes = pickle.dumps(source_user_id)
    restored_user_id: object = pickle.loads(serialized_user_id)

    assert restored_user_id == "user_123e4567-e89b-42d3-a456-426614174000"
    assert type(restored_user_id) is UserId
    assert isinstance(restored_user_id, str)
    assert isinstance(restored_user_id, UserId)
