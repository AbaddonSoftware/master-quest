from __future__ import annotations

from enum import Enum


class Permission(str, Enum):
    # Rooms & membership
    ROOM_READ = "room.read"
    ROOM_INVITE = "room.invite"
    ROOM_KICK = "room.kick"
    ROOM_RESTORE = "room.restore"
    ROOM_DELETE_HARD = "room.delete_hard"

    # Boards / structure
    BOARD_READ = "board.read"
    BOARD_CREATE = "board.create"
    BOARD_UPDATE = "board.update"
    BOARD_DELETE = "board.delete"
    BOARD_RESTORE = "board.restore"

    COLUMN_CREATE = "column.create"
    COLUMN_UPDATE = "column.update"
    COLUMN_DELETE = "column.delete"

    LANE_CREATE = "lane.create"
    LANE_UPDATE = "lane.update"
    LANE_DELETE = "lane.delete"

    # Cards
    CARD_READ = "card.read"
    CARD_CREATE = "card.create"
    CARD_UPDATE = "card.update"  # edit text, move, assign
    CARD_DELETE = "card.delete"
    CARD_RESTORE = "card.restore"

    # Comments
    COMMENT_CREATE = "comment.create"
    COMMENT_UPDATE = "comment.update"  # author or moderator
    COMMENT_DELETE = "comment.delete"  # author or moderator

    # Labels
    LABEL_MANAGE = "label.manage"

    # Attachments / Twee
    ATTACHMENT_ADD = "attachment.add"
    ATTACHMENT_DELETE = "attachment.delete"
    TWEE_UPLOAD = "twee.upload"

    # Admin ops
    PURGE = "purge"  # permanent delete of soft-deleted items
