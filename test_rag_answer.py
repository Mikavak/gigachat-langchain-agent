from types import SimpleNamespace

import rag_answer


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def invoke(self, messages):
        self.calls += 1

        return SimpleNamespace(
            content="Обратитесь в службу поддержки."
        )


def test_answer_found(monkeypatch):
    def fake_retrieve(question):
        return {
            "question": "Как изменить номер телефона?",
            "answer": "Обратитесь в службу поддержки.",
            "similarity": 0.96,
        }

    monkeypatch.setattr(
        rag_answer,
        "retrieve_answer",
        fake_retrieve,
    )

    llm = FakeLLM()

    result = rag_answer.generate_answer(
        question="Как поменять телефон?",
        llm=llm,
    )

    assert result["status"] == "answered"
    assert result["similarity"] == 0.96
    assert result["answer"] == "Обратитесь в службу поддержки."
    assert llm.calls == 1


def test_answer_not_found(monkeypatch):
    monkeypatch.setattr(
        rag_answer,
        "retrieve_answer",
        lambda question: None,
    )

    llm = FakeLLM()

    result = rag_answer.generate_answer(
        question="Какая комиссия за перевод?",
        llm=llm,
    )

    assert result["status"] == "needs_operator"
    assert result["similarity"] is None

    # Если знаний нет, GigaChat не вызывается
    assert llm.calls == 0