# from app.persistence.models import Card, Comment
from flask import g
from sqlalchemy import exists, select

from ...extensions import db


def is_comment_author(comment_public_id: str) -> bool:
    statement = (
        exists()
        .where(
            Comment.public_id == comment_public_id,
            Comment.user_id == g.user.id,
        )
        .select()
    )
    return db.session.execute(statement).scalar()


def is_card_author(card_public_id: str) -> bool:
    statement = (
        exists()
        .where(
            Card.public_id == card_public_id,
            Card.user_id == g.user.id,
        )
        .select()
    )
    return db.session.execute(statement).scalar()
