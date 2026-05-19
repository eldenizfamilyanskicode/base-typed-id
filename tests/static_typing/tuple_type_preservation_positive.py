from __future__ import annotations

from base_typed_id import BasePrefixedTypedId, BaseTypedId


class UserId(BaseTypedId):
    pass


class WorkspaceId(BasePrefixedTypedId):
    prefix = "workspace"


def accepts_user_id_type(user_id_type: type[UserId]) -> None:
    del user_id_type


def accepts_workspace_id_type(workspace_id_type: type[WorkspaceId]) -> None:
    del workspace_id_type


def accepts_user_id(user_id: UserId) -> None:
    del user_id


def accepts_workspace_id(workspace_id: WorkspaceId) -> None:
    del workspace_id


user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")
workspace_id: WorkspaceId = WorkspaceId(
    "workspace_123e4567-e89b-42d3-a456-426614174001"
)

user_id_reduce_tuple: tuple[type[UserId], tuple[str]] = user_id.__reduce__()
workspace_id_reduce_tuple: tuple[type[WorkspaceId], tuple[str]] = (
    workspace_id.__reduce__()
)

accepts_user_id_type(user_id_reduce_tuple[0])
accepts_workspace_id_type(workspace_id_reduce_tuple[0])

rebuilt_user_id: UserId = user_id_reduce_tuple[0](*user_id_reduce_tuple[1])
rebuilt_workspace_id: WorkspaceId = workspace_id_reduce_tuple[0](
    *workspace_id_reduce_tuple[1]
)

accepts_user_id(rebuilt_user_id)
accepts_workspace_id(rebuilt_workspace_id)
