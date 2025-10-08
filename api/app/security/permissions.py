from enum import StrEnum
from typing import FrozenSet, Mapping


class Permission(StrEnum):
    VIEW_BOARD = "view_board"
    CREATE_BOARD = "create_board"
    EDIT_BOARD = "edit_board"
    SOFT_DELETE_BOARD = "soft_delete_board"
    HARD_DELETE_BOARD = "hard_delete_board"
    CREATE_BOARD_COLUMN = "create_board_column"
    EDIT_BOARD_COLUMN = "edit_board_column"
    CREATE_CARD = "create_card"
    EDIT_CARD = "edit_card"
    INVITE_MEMBER = "invite_member"
    MANAGE_MEMBER = "manage_member"
    COMMENT = "comment"


class RoleType(StrEnum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class RoomType(StrEnum):
    NORMAL = "NORMAL"
    GUEST = "GUEST"


ROLE_DEFAULTS: Mapping[RoleType, FrozenSet[Permission]] = {
    RoleType.VIEWER: frozenset(
        {
            Permission.VIEW_BOARD,
            Permission.COMMENT,
        }
    ),
    RoleType.MEMBER: frozenset(
        {
            Permission.VIEW_BOARD,
            Permission.COMMENT,
            Permission.CREATE_CARD,
            Permission.EDIT_CARD,
        }
    ),
    RoleType.ADMIN: frozenset(
        {
            Permission.VIEW_BOARD,
            Permission.COMMENT,
            Permission.INVITE_MEMBER,
            Permission.CREATE_CARD,
            Permission.EDIT_CARD,
        }
    ),
}

ROLE_DEFAULTS[RoleType.OWNER] = frozenset(
    {
        *ROLE_DEFAULTS[RoleType.ADMIN],
    }
)
