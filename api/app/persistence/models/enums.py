from sqlalchemy.dialects.postgresql import ENUM

Role = ENUM(
    "owner",
    "admin",
    "member",
    "viewer",
    name="room_role",
    create_type=False,
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
    create_type=False,
)

AttachmentKind = ENUM(
    "twee",
    "file",
    "link",
    name="attachment_kind",
    create_type=False,
)
