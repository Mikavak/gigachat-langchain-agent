from sqlalchemy import select

from database.models import Conversation, Message
from database.session import SessionLocal


def extract_qa_pairs() -> list[dict]:
    with SessionLocal() as session:
        stmt = (
            select(
                Message.id,
                Conversation.external_id,
                Message.role,
                Message.content,
            )
            .join(
                Message,
                Message.conversation_id == Conversation.id,
            )
            .where(
                Conversation.external_id.in_(
                    ["mock-chat-001", "mock-chat-002"]
                )
            )
            .order_by(Conversation.external_id, Message.id)
        )

        rows = session.execute(stmt).all()

    qa_pairs = []
    current_dialogue = None
    current_question = None
    history = []

    for message_id, external_id, role, content in rows:
        if external_id != current_dialogue:
            current_dialogue = external_id
            current_question = None
            history = []

        if role == "client":
            current_question = content


        elif role == "operator" and current_question is not None:

            qa_pairs.append(

                {

                    "source_message_id": message_id,

                    "external_id": external_id,

                    "question": current_question,

                    "answer": content,

                    "context": history.copy(),

                }

            )

            current_question = None

        history.append(
            {
                "role": role,
                "content": content,
            }
        )

    return qa_pairs


if __name__ == "__main__":
    pairs = extract_qa_pairs()

    print(f"Извлечено пар: {len(pairs)}")

    for pair in pairs:
        print(f"\nДиалог: {pair['external_id']}")
        print(f"Вопрос: {pair['question']}")
        print(f"Ответ: {pair['answer']}")
        print(f"Предыдущих сообщений: {len(pair['context'])}")