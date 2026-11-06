from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from database.models import KnowledgeEntry
from database.session import SessionLocal
from functools import lru_cache

MODEL_NAME = "intfloat/multilingual-e5-small"


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(MODEL_NAME)


def search_knowledge(question: str, limit: int = 3):
    model = get_model()

    # Преобразуем вопрос пользователя в вектор
    vector = model.encode(
        f"query: {question}",
        normalize_embeddings=True,
    ).tolist()

    # Вычисляем косинусное расстояние
    distance = KnowledgeEntry.embedding.cosine_distance(vector)

    # Преобразуем расстояние в similarity
    similarity = (1 - distance).label("similarity")

    with SessionLocal() as session:
        stmt = (
            select(
                KnowledgeEntry.normalized_question,
                KnowledgeEntry.answer,
                similarity,
            )
            .where(KnowledgeEntry.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        )

        results = session.execute(stmt).all()

    return results


if __name__ == "__main__":
    question = (
        "Как поменять телефон, "
        "если нет доступа к старому номеру?"
    )

    print(f"Вопрос пользователя: {question}\n")

    results = search_knowledge(question)

    for index, result in enumerate(results, start=1):
        print(f"Результат №{index}")
        print(f"Вопрос из БЗ: {result.normalized_question}")
        print(f"Ответ: {result.answer}")
        print(f"Similarity: {result.similarity:.4f}")
        print()