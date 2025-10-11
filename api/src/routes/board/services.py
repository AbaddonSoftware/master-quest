from flask import abort, g
from src.extensions import db
from src.persistence.models import Board, Room


def create_board(*, room_id: int, name: str) -> Board:
    board = Board(
        room_id=room_id,
        name=name.strip(),
    )
    db.session.add(board)
    db.session.flush()
    db.session.commit()
    return board


def soft_delete_board(board_id: str):
    board = Board.query.filter_by(public_id=board_id).first()
    board or abort(404, f"Board '{board_id}' not found")
    board.soft_delete(g.user.id)
    db.session.flush()
    db.session.commit()


def view_board(room_public_id: str):
    boards = (
        Board.query.join(Room, Room.id == Board.room_id)
        .filter(Board.deleted_at.is_(None), Room.public_id == room_public_id)
        .all()
    )
    return boards


def create_board_column(
    board_public_id: str, title: str, wip_limit: int, column_type: str
):
    pass
