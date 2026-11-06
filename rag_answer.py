import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat import GigaChat

from retrieval import retrieve_answer


load_dotenv()


def generate_answer(question: str, llm: GigaChat) -> dict:
    # Шаг 1. Ищем подходящую запись в базе знаний
    knowledge = retrieve_answer(question)

    # Шаг 2. Если ответа нет, направляем вопрос оператору
    if knowledge is None:
        return {
            "status": "needs_operator",
            "answer": "Не удалось найти подходящий ответ. Требуется оператор.",
            "similarity": None,
        }

    # Шаг 3. Передаём найденную информацию в GigaChat
    messages = [
        SystemMessage(
            content=(
                "Ты интеллектуальный AI-ассистент службы поддержки.\n\n"

                "Твоя задача — помогать пользователям, используя "
                "информацию из базы знаний и свои общие знания.\n\n"

                "Правила:\n"

                "1. Информация из базы знаний является основным "
                "источником фактов о нашем сервисе.\n"

                "2. Ты можешь использовать собственные знания, "
                "чтобы давать полезные пояснения, объяснять термины "
                "и делать ответ понятнее.\n"

                "3. Учитывай конкретный вопрос пользователя, "
                "а не просто повторяй текст из базы знаний.\n"

                "4. Можешь расширять ответ, если дополнения "
                "логически следуют из предоставленной информации "
                "и не противоречат ей.\n"

                "5. Не придумывай тарифы, сроки, правила компании, "
                "ссылки, контакты и процедуры, "
                "которых нет в базе знаний.\n"

                "6. Если информация из базы знаний противоречит "
                "твоим общим знаниям, придерживайся базы знаний "
                "в вопросах работы нашего сервиса.\n"

                "7. Если для корректного ответа не хватает "
                "важных сведений, верни строго NEED_OPERATOR.\n"

                "8. Отвечай естественно, понятно и по существу.\n"
                "9. Не упоминай базу знаний в ответе пользователю."
            )
        ),
        HumanMessage(
            content=(
                f"Вопрос пользователя:\n{question}\n\n"
                f"Вопрос из базы знаний:\n{knowledge['question']}\n\n"
                f"Ответ из базы знаний:\n{knowledge['answer']}"
            )
        ),
    ]

    response = llm.invoke(messages)
    print(f"DEBUG GigaChat response: {response.content!r}")

    if not isinstance(response.content, str):
        raise ValueError("GigaChat вернул нетекстовый ответ")

    answer = response.content.strip()

    if not answer or answer == "NEED_OPERATOR":
        return {
            "status": "needs_operator",
            "answer": "Требуется оператор.",
            "similarity": knowledge["similarity"],
        }

    return {
        "status": "answered",
        "answer": answer,
        "similarity": knowledge["similarity"],
    }


if __name__ == "__main__":
    llm = GigaChat(
        model=os.getenv("GIGACHAT_MODEL", "GigaChat"),
        temperature=0,
    )

    questions = [
        "Как поменять телефон, если нет доступа к старому номеру?",
        "Какая комиссия за денежный перевод?",
    ]

    for question in questions:
        result = generate_answer(question, llm)

        print(f"\nВопрос: {question}")
        print(f"Статус: {result['status']}")
        print(f"Ответ: {result['answer']}")
        print(f"Similarity: {result['similarity']}")