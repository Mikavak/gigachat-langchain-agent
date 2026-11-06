import json
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat import GigaChat
from sqlalchemy import select, update

from database.models import KnowledgeEntry
from database.session import SessionLocal


load_dotenv()


def normalize_question(
    llm: GigaChat,
    question: str,
    context: list,
) -> str:

    # Убираем текущий вопрос из истории
    previous_context = context

    if (
        context
        and context[-1]["role"] == "client"
        and context[-1]["content"] == question
    ):
        previous_context = context[:-1]

    # Получаем предыдущие вопросы клиента
    client_history = [
        message["content"]
        for message in previous_context
        if message["role"] == "client"
    ]

    # Для нашего прототипа:
    # если предыдущих вопросов нет, сохраняем оригинал
    if not client_history:
        return question

    messages = [
        SystemMessage(
            content=(
                "Ты нормализуешь уточняющие вопросы клиентов.\n"
                "Твоя задача — восстановить полный смысл "
                "последнего вопроса из предыдущих вопросов клиента.\n\n"

                "Правила:\n"
                "1. Определи действие, которое клиент хотел выполнить.\n"
                "2. Сохрани это действие в итоговом вопросе.\n"
                "3. Добавь условие из последнего уточнения.\n"
                "4. Не придумывай дополнительных обстоятельств.\n"
                "5. Не добавляй пояснения или вступления.\n"
                "6. Верни только один самостоятельный вопрос.\n\n"

                "Пример:\n"
                "Предыдущий вопрос: Как отменить доставку?\n"
                "Уточнение: А если заказ уже отправили?\n"
                "Результат: Как отменить доставку, "
                "если заказ уже отправили?"
            )
        ),
        HumanMessage(
            content=(
                "Предыдущие вопросы клиента:\n"
                f"{json.dumps(client_history, ensure_ascii=False)}\n\n"
                f"Последний вопрос:\n{question}"
            )
        ),
    ]

    response = llm.invoke(messages)

    if not isinstance(response.content, str):
        raise ValueError("GigaChat вернул нетекстовый ответ")

    normalized = response.content.strip()

    # Проверяем базовые требования к формату
    if (
        "\n" in normalized
        or normalized.count("?") != 1
        or not normalized.endswith("?")
    ):
        raise ValueError(
            f"Некорректный формат ответа: {normalized}"
        )

    return normalized

def normalize_knowledge() -> None:
    llm = GigaChat(
        model=os.getenv("GIGACHAT_MODEL", "GigaChat"),
        temperature=0,
    )

    # Получаем записи, которые ещё не обработаны
    with SessionLocal() as session:
        entries = session.execute(
            select(
                KnowledgeEntry.id,
                KnowledgeEntry.question,
                KnowledgeEntry.dialogue_context,
            )
            .where(KnowledgeEntry.normalized_question.is_(None))
            .order_by(KnowledgeEntry.id)
        ).all()

    print(f"Найдено необработанных записей: {len(entries)}")

    for entry_id, question, context in entries:
        try:
            normalized = normalize_question(
                llm=llm,
                question=question,
                context=context,
            )

            # Сохраняем результат отдельной транзакцией
            with SessionLocal.begin() as session:
                result = session.execute(
                    update(KnowledgeEntry)
                    .where(
                        KnowledgeEntry.id == entry_id,
                        KnowledgeEntry.normalized_question.is_(None),
                    )
                    .values(normalized_question=normalized)
                )

            if result.rowcount == 1:
                print(f"\nЗапись ID: {entry_id}")
                print(f"Исходный вопрос: {question}")
                print(f"Нормализованный: {normalized}")
            else:
                print(f"Запись {entry_id} уже обработана")

        except Exception as exc:
            print(f"Ошибка обработки записи {entry_id}: {exc}")

    print("\nОбработка завершена")


if __name__ == "__main__":
    normalize_knowledge()