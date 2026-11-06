from search_knowledge import search_knowledge


MIN_SIMILARITY = 0.90


def retrieve_answer(
    question: str,
    threshold: float = MIN_SIMILARITY,
) -> dict | None:

    results = search_knowledge(
        question=question,
        limit=1,
    )

    if not results:
        return None

    best = results[0]

    if best.similarity < threshold:
        return None

    return {
        "question": best.normalized_question,
        "answer": best.answer,
        "similarity": float(best.similarity),
    }

if __name__ == "__main__":

    questions = [
        "Как поменять телефон, если нет доступа к старому номеру?",
        "Забыл пароль от аккаунта, как восстановить доступ?",
        "Как изменить телефон в личном кабинете?",
        "Какая комиссия за денежный перевод?",
        "Как оформить кредит?",
    ]

    for question in questions:

        result = retrieve_answer(question)

        print(f"\nВопрос: {question}")

        if result is None:
            print("Ответ не найден. Требуется оператор.")
            continue

        print(f"Ответ: {result['answer']}")
        print(f"Similarity: {result['similarity']:.4f}")