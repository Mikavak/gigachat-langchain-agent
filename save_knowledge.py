from sqlalchemy.dialects.postgresql import insert

from database.models import KnowledgeEntry
from database.session import SessionLocal
from extract_qa_pairs import extract_qa_pairs


def save_knowledge_entries() -> None:
    qa_pairs = extract_qa_pairs()

    imported = 0
    skipped = 0

    with SessionLocal.begin() as session:
        for pair in qa_pairs:
            stmt = (
                insert(KnowledgeEntry)
                .values(
                    source_message_id=pair["source_message_id"],
                    question=pair["question"],
                    answer=pair["answer"],
                    dialogue_context=pair["context"],
                )
                .on_conflict_do_nothing(
                    index_elements=[
                        KnowledgeEntry.source_message_id
                    ]
                )
                .returning(KnowledgeEntry.id)
            )

            knowledge_id = session.scalar(stmt)

            if knowledge_id is None:
                skipped += 1
            else:
                imported += 1

    print(f"Сохранено записей: {imported}")
    print(f"Пропущено записей: {skipped}")


if __name__ == "__main__":
    save_knowledge_entries()