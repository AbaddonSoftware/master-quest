from flask import jsonify, request

from ...domain.decorators import require_permission
from ...domain.security.permissions import Permission
from ...domain.validators import validate_str, validate_user_logged_in
from . import room_bp
from .services import (
    create_room,
    create_room_invite,
    delete_room,
    leave_room,
    list_room_invites,
    list_room_members,
    revoke_room_invite,
    update_room_member_role,
    view_room,
    view_rooms,
)

ROLE_WEIGHT = {
    "OWNER": 0,
    "ADMIN": 1,
    "MEMBER": 2,
    "VIEWER": 3,
}


def _serialize_room(room, *, current_user_id: int):
    sorted_members = sorted(
        (member for member in room.members if member.user is not None),
        key=lambda member: (
            ROLE_WEIGHT.get(member.role.value, 99),
            member.user.display_name is None,
            (member.user.display_name or member.user.name or "").casefold(),
        ),
    )
    membership_role = None
    membership_user_public_id = None
    members_payload = []
    for member in sorted_members:
        user = member.user
        if member.user_id == current_user_id:
            membership_role = member.role.value
            membership_user_public_id = str(user.public_id)
        members_payload.append(
            {
                "user_public_id": str(user.public_id),
                "display_name": user.display_name,
                "name": user.name,
                "email": user.email,
                "role": member.role.value,
            }
        )
    membership_role = membership_role or "VIEWER"
    return {
        "public_id": room.public_id,
        "name": room.name,
        "boards": [
            {
                "public_id": board.public_id,
                "name": board.name,
            }
            for board in room.boards
            if not getattr(board, "deleted_at", None)
        ],
        "members": members_payload,
        "membership": {
            "role": membership_role,
            "user_public_id": membership_user_public_id,
        },
    }


@room_bp.post("/rooms")
def create_room_route():
    id = validate_user_logged_in()
    data = request.get_json(silent=True) or {}
    field = "name"
    name = validate_str(data.get(field), field, min_len=3, max_len=30)
    new_room = create_room(creator_user_id=id, name=name)
    return jsonify({"public_id": new_room.public_id, "name": new_room.name}), 201


@room_bp.get("/rooms/<string:room_public_id>")
@require_permission(Permission.VIEW_ROOM)
def view_room_by_public_id(room_public_id: str):
    user_id = validate_user_logged_in()
    room = view_room(room_public_id)
    if room is None:
        return jsonify({"message": "Room not found."}), 404
    return jsonify(_serialize_room(room, current_user_id=user_id)), 200


@room_bp.get("/rooms")
def view_rooms_route():
    user_id = validate_user_logged_in()
    rooms = view_rooms(user_id)
    payload = [_serialize_room(room, current_user_id=user_id) for room in rooms]
    return jsonify({"rooms": payload}), 200


@room_bp.delete("/rooms/<string:room_public_id>")
def delete_room_route(room_public_id: str):
    user_id = validate_user_logged_in()
    delete_room(room_public_id=room_public_id, actor_user_id=user_id)
    return jsonify({"message": "Room deleted."}), 200


@room_bp.get("/rooms/<string:room_public_id>/members")
@require_permission(Permission.VIEW_ROOM)
def list_members_route(room_public_id: str):
    members = list_room_members(room_public_id)
    payload = []
    for member, user in members:
        payload.append(
            {
                "user_public_id": str(user.public_id),
                "display_name": user.display_name,
                "name": user.name,
                "email": user.email,
                "role": member.role.value,
            }
        )
    return jsonify({"members": payload}), 200


@room_bp.patch("/rooms/<string:room_public_id>/members/<string:member_public_id>")
@require_permission(Permission.MANAGE_MEMBER)
def update_member_role_route(room_public_id: str, member_public_id: str):
    validate_user_logged_in()
    data = request.get_json(silent=True) or {}
    member, user = update_room_member_role(
        room_public_id=room_public_id,
        member_public_id=member_public_id,
        role=data.get("role"),
        confirmation_name=data.get("confirmation_name"),
    )
    return (
        jsonify(
            {
                "member": {
                    "user_public_id": str(user.public_id),
                    "display_name": user.display_name,
                    "name": user.name,
                    "email": user.email,
                    "role": member.role.value,
                }
            }
        ),
        200,
    )


@room_bp.get("/rooms/<string:room_public_id>/invites")
@require_permission(Permission.INVITE_MEMBER)
def list_invites_route(room_public_id: str):
    invites = list_room_invites(room_public_id)
    payload = []
    for invite in invites:
        payload.append(
            {
                "code": invite.code,
                "role": invite.role.value,
                "expires_at": (
                    invite.expires_at.isoformat() if invite.expires_at else None
                ),
                "max_uses": invite.redemption_max,
                "used": len(invite.redemptions),
                "remaining": max(invite.redemption_max - len(invite.redemptions), 0),
            }
        )
    return jsonify({"invites": payload}), 200


@room_bp.post("/rooms/<string:room_public_id>/invites")
@require_permission(Permission.INVITE_MEMBER)
def create_invite_route(room_public_id: str):
    creator_user_id = validate_user_logged_in()
    data = request.get_json(silent=True) or {}
    invite = create_room_invite(
        room_public_id=room_public_id,
        role=data.get("role"),
        max_uses=data.get("max_uses"),
        expires_in_hours=data.get("expires_in_hours"),
        creator_user_id=creator_user_id,
    )
    return (
        jsonify(
            {
                "invite": {
                    "code": invite.code,
                    "role": invite.role.value,
                    "expires_at": (
                        invite.expires_at.isoformat() if invite.expires_at else None
                    ),
                    "max_uses": invite.redemption_max,
                    "used": 0,
                    "remaining": invite.redemption_max,
                }
            }
        ),
        201,
    )


@room_bp.delete("/rooms/<string:room_public_id>/membership")
@require_permission(Permission.VIEW_ROOM)
def leave_room_route(room_public_id: str):
    user_id = validate_user_logged_in()
    leave_room(room_public_id=room_public_id, user_id=user_id)
    return jsonify({"message": "Left room."}), 200


@room_bp.delete("/rooms/<string:room_public_id>/invites/<string:invite_code>")
@require_permission(Permission.INVITE_MEMBER)
def revoke_invite_route(room_public_id: str, invite_code: str):
    actor_user_id = validate_user_logged_in()
    invite = revoke_room_invite(
        room_public_id=room_public_id,
        invite_code=invite_code,
        actor_user_id=actor_user_id,
    )
    return (
        jsonify(
            {
                "message": "Invite revoked.",
                "code": invite.code,
            }
        ),
        200,
    )
