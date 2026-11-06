from search_knowledge import search_knowledge


TEST_QUESTIONS = [
    "Как поменять телефон, если нет доступа к старому номеру?",
    "Забыл пароль от аккаунта, как восстановить доступ?",
    "Как изменить телефон в личном кабинете?",
    "Какая комиссия за денежный перевод?",
    "Как оформить кредит?",
]


def test_search_quality():
    for question in TEST_QUESTIONS:
        print(f"\nВопрос: {question}")

        results = search_knowledge(
            question=question,
            limit=2,
        )

        for index, result in enumerate(results, start=1):
            print(
                f"{index}. "
                f"{result.normalized_question} "
                f"| similarity={result.similarity:.4f}"
            )

        if len(results) >= 2:
            difference = (
                results[0].similarity
                - results[1].similarity
            )

            print(f"Разница между результатами: {difference:.4f}")


if __name__ == "__main__":
    test_search_quality()