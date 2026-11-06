from sentence_transformers import SentenceTransformer


def test_embeddings():
    model = SentenceTransformer(
        "intfloat/multilingual-e5-small"
    )

    question = "Как изменить номер телефона?"

    vector = model.encode(
        f"query: {question}",
        normalize_embeddings=True,
    )

    print(f"Исходный вопрос: {question}")
    print(f"Размерность вектора: {len(vector)}")
    print(f"Первые пять значений: {vector[:5]}")

    assert len(vector) == 384

    print("Эмбеддинг успешно создан!")


if __name__ == "__main__":
    test_embeddings()