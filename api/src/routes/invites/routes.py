from flask import jsonify

from ...domain.validators import validate_user_logged_in
from ..rooms.services import accept_invite_code
from . import invite_bp


@invite_bp.post("/<string:invite_code>/accept")
def accept_invite_route(invite_code: str):
    user_id = validate_user_logged_in()
    membership, invite, room = accept_invite_code(code=invite_code, user_id=user_id)
    return (
        jsonify(
            {
                "room": {
                    "public_id": str(room.public_id),
                    "name": room.name,
                },
                "membership": {
                    "role": membership.role.value,
                },
                "invite": {
                    "code": invite.code,
                    "role": invite.role.value,
                },
            }
        ),
        200,
    )
