from typing import Literal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from database.models import Conversation, Message
from database.session import SessionLocal


def get_or_create_conversation(
    session: Session,
    external_id: str,
) -> Conversation:

    stmt = (
        insert(Conversation)
        .values(external_id=external_id)
        .on_conflict_do_nothing(
            index_elements=[Conversation.external_id]
        )
    )

    session.execute(stmt)

    conversation = session.scalar(
        select(Conversation).where(
            Conversation.external_id == external_id
        )
    )

    if conversation is None:
        raise RuntimeError("Не удалось получить диалог")

    return conversation


def save_message(
    external_id: str,
    role: Literal["client", "operator"],
    content: str,
) -> None:

    if role not in ("client", "operator"):
        raise ValueError("Недопустимая роль")

    with SessionLocal.begin() as session:

        conversation = get_or_create_conversation(
            session=session,
            external_id=external_id,
        )

        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
        )

        session.add(message)