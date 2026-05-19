from __future__ import annotations

from base_typed_id import BasePrefixedTypedId, BaseTypedId


class UserId(BaseTypedId):
    pass


class WorkspaceId(BasePrefixedTypedId):
    prefix = "workspace"


def require_user_id(user_id: UserId) -> None:
    print(f"accepted UserId: {user_id!r}")


def require_workspace_id(workspace_id: WorkspaceId) -> None:
    print(f"accepted WorkspaceId: {workspace_id!r}")


def demonstrate_base_typed_id_reduce_tuple() -> None:
    user_id: UserId = UserId("123e4567-e89b-42d3-a456-426614174000")
    reduce_tuple: tuple[type[UserId], tuple[str]] = user_id.__reduce__()

    rebuilt_user_id: UserId = reduce_tuple[0](*reduce_tuple[1])

    require_user_id(rebuilt_user_id)
    print(f"UserId type preserved through tuple: {type(rebuilt_user_id) is UserId}")


def demonstrate_base_prefixed_typed_id_reduce_tuple() -> None:
    workspace_id: WorkspaceId = WorkspaceId(
        "workspace_123e4567-e89b-42d3-a456-426614174001"
    )
    reduce_tuple: tuple[type[WorkspaceId], tuple[str]] = workspace_id.__reduce__()

    rebuilt_workspace_id: WorkspaceId = reduce_tuple[0](*reduce_tuple[1])

    require_workspace_id(rebuilt_workspace_id)
    print(
        "WorkspaceId type preserved through tuple: "
        f"{type(rebuilt_workspace_id) is WorkspaceId}"
    )


def main() -> None:
    demonstrate_base_typed_id_reduce_tuple()
    demonstrate_base_prefixed_typed_id_reduce_tuple()


if __name__ == "__main__":
    main()
