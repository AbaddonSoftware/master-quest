from sqlalchemy.dialects.postgresql import ENUM

Role = ENUM(
    "owner",
    "admin",
    "member",
    "viewer",
    name="room_role",
    create_type=True,
)

RoomKind = ENUM(
    "guest",
    "normal",
    name="room_kind",
    create_type=True,
)

LaneType = ENUM(
    "standard",
    "expedite",
    "fixed_date",
    "intangible",
    "maintenance",
    "defect",
    "research",
    "vip",
    name="lane_type",
    create_type=True,
)

AttachmentKind = ENUM(
    "twee",
    "file",
    "link",
    name="attachment_kind",
    create_type=True,
)
