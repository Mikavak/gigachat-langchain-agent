from uuid import uuid4

from sqlalchemy import func, select

from database.crud import save_message
from database.models import Conversation, Message
from database.session import SessionLocal


def test_save_messages():
    # Уникальный идентификатор для каждого запуска теста
    external_id = f"test-chat-{uuid4()}"

    # Первое сообщение — клиент
    save_message(
        external_id=external_id,
        role="client",
        content="Здравствуйте! Как восстановить пароль?",
    )

    # Второе сообщение — оператор
    save_message(
        external_id=external_id,
        role="operator",
        content="Перейдите на страницу восстановления пароля.",
    )

    # Проверяем реальные данные в PostgreSQL
    with SessionLocal() as session:
        conversation_count = session.scalar(
            select(func.count())
            .select_from(Conversation)
            .where(Conversation.external_id == external_id)
        )

        conversation = session.scalar(
            select(Conversation)
            .where(Conversation.external_id == external_id)
        )

        assert conversation is not None

        messages = session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.id)
        ).all()

        print(f"Количество диалогов: {conversation_count}")
        print(f"Количество сообщений: {len(messages)}")

        for message in messages:
            print(
                f"id={message.id}, "
                f"conversation_id={message.conversation_id}, "
                f"role={message.role}, "
                f"content={message.content}"
            )

        # Проверяем отсутствие дубликатов диалога
        assert conversation_count == 1

        # Проверяем количество сообщений
        assert len(messages) == 2

        # Проверяем содержимое и порядок сообщений
        assert [message.role for message in messages] == [
            "client",
            "operator",
        ]

        # У сообщений разные ID
        assert messages[0].id != messages[1].id

        # Но оба относятся к одному диалогу
        assert all(
            message.conversation_id == conversation.id
            for message in messages
        )

    print("Все проверки пройдены!")


if __name__ == "__main__":
    test_save_messages()