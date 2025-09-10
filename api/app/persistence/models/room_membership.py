from app.extensions import db


class RoomMembership(db.Model):
    __tablename__ = "room_memberships"

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE" ), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    role = db.Column(db.String(255), nullable=True)
    joined_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)


    __table_args__ = (
    db.Index("index_room_memberships_user_id", "user_id"),
)