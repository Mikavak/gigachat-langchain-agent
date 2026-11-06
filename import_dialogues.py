import json
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from database.models import Conversation, Message
from database.session import SessionLocal


FILE_PATH = Path(__file__).resolve().parent / "data" / "mock_dialogues.json"


def import_dialogues() -> None:
    with FILE_PATH.open("r", encoding="utf-8") as file:
        dialogues = json.load(file)

    imported = 0
    skipped = 0
    total_messages = 0

    for dialogue in dialogues:
        external_id = dialogue["external_id"]
        messages = dialogue["messages"]

        with SessionLocal.begin() as session:
            stmt = (
                insert(Conversation)
                .values(external_id=external_id)
                .on_conflict_do_nothing(
                    index_elements=[Conversation.external_id]
                )
                .returning(Conversation.id)
            )

            conversation_id = session.scalar(stmt)

            if conversation_id is None:
                skipped += 1
                continue

            for message in messages:
                role = message["role"]
                content = message["content"]

                if role not in ("client", "operator"):
                    raise ValueError(f"Недопустимая роль: {role}")

                session.add(
                    Message(
                        conversation_id=conversation_id,
                        role=role,
                        content=content,
                    )
                )

            imported += 1
            total_messages += len(messages)

    print(f"Импортировано диалогов: {imported}")
    print(f"Пропущено диалогов: {skipped}")
    print(f"Сохранено сообщений: {total_messages}")


if __name__ == "__main__":
    import_dialogues()