import json

from dotenv import load_dotenv
from langchain_gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage

from database.models import KnowledgeEntry
from database.session import SessionLocal


load_dotenv()


def normalize_question():
    with SessionLocal() as session:
        entry = session.get(KnowledgeEntry, 3)

        if entry is None:
            raise ValueError("Запись не найдена")

        question = entry.question
        answer = entry.answer
        context = entry.dialogue_context

    llm = GigaChat(temperature=0)

    previous_context = (
        context[:-1]
        if context
           and context[-1]["role"] == "client"
           and context[-1]["content"] == question
        else context
    )

    messages = [
        SystemMessage(
            content=(
                "Ты нормализуешь вопросы клиентов для базы знаний.\n"
                "Твоя задача — сделать последний вопрос клиента "
                "самостоятельным и понятным без контекста.\n\n"

                "Правила:\n"
                "1. Определи основное намерение клиента.\n"
                "2. Используй историю для восстановления темы обращения.\n"
                "3. Сохраняй смысл последнего вопроса.\n"
                "4. Не добавляй инструкции и способы решения проблемы.\n"
                "5. Не придумывай дополнительные обстоятельства.\n"
                "6. Если вопрос уже самостоятельный, оставь его без изменений.\n"
                "7. Верни только один итоговый вопрос."
            )
        ),
        HumanMessage(
            content=(
                f"Предыдущая переписка:\n"
                f"{json.dumps(previous_context, ensure_ascii=False)}\n\n"
                f"Последний вопрос клиента:\n{question}"
            )
        ),
    ]

    response = llm.invoke(messages)

    print(f"Исходный вопрос: {question}")
    print(f"Обработанный вопрос: {response.content}")


if __name__ == "__main__":
    normalize_question()