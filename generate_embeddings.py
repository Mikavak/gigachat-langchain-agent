from sentence_transformers import SentenceTransformer
from sqlalchemy import select, update

from database.models import KnowledgeEntry
from database.session import SessionLocal


MODEL_NAME = "intfloat/multilingual-e5-small"


def generate_embeddings() -> None:
    # Получаем записи без эмбеддингов
    with SessionLocal() as session:
        entries = session.execute(
            select(
                KnowledgeEntry.id,
                KnowledgeEntry.normalized_question,
            )
            .where(
                KnowledgeEntry.embedding.is_(None),
                KnowledgeEntry.normalized_question.is_not(None),
            )
            .order_by(KnowledgeEntry.id)
        ).all()

    print(f"Найдено записей без эмбеддингов: {len(entries)}")

    if not entries:
        return

    # Загружаем локальную модель один раз
    model = SentenceTransformer(MODEL_NAME)

    saved = 0

    for entry_id, question in entries:
        try:
            # Создаём эмбеддинг
            vector = model.encode(
                f"query: {question}",
                normalize_embeddings=True,
            )

            if len(vector) != 384:
                raise ValueError(
                    f"Неверная размерность: {len(vector)}"
                )

            # Сохраняем в PostgreSQL
            with SessionLocal.begin() as session:
                result = session.execute(
                    update(KnowledgeEntry)
                    .where(
                        KnowledgeEntry.id == entry_id,
                        KnowledgeEntry.embedding.is_(None),
                    )
                    .values(
                        embedding=vector.tolist()
                    )
                )

            if result.rowcount == 1:
                saved += 1
                print(
                    f"ID={entry_id}: "
                    f"эмбеддинг сохранён, "
                    f"размерность={len(vector)}"
                )

        except Exception as exc:
            print(f"Ошибка для ID={entry_id}: {exc}")

    print(f"\nВсего сохранено эмбеддингов: {saved}")


if __name__ == "__main__":
    generate_embeddings()