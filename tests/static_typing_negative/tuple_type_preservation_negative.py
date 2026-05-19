from __future__ import annotations

from base_typed_id import BasePrefixedTypedId, BaseTypedId


class UserId(BaseTypedId):
    pass


class WorkspaceId(BasePrefixedTypedId):
    prefix = "workspace"


user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")
user_id_reduce_tuple: tuple[type[UserId], tuple[str]] = user_id.__reduce__()

# This file is intentionally invalid for static type checkers.
#
# The purpose of this negative test is to verify that __reduce__()
# preserves the exact subclass type statically.
#
# If these assignments ever become valid, then the typing contract
# for __reduce__ regressed and exact subtype preservation was lost.
wrong_workspace_id_type: type[WorkspaceId] = user_id_reduce_tuple[0]
wrong_workspace_id: WorkspaceId = user_id_reduce_tuple[0](*user_id_reduce_tuple[1])
