import os
from typing import Callable

from dotenv import load_dotenv
from psycopg.conninfo import make_conninfo

from langchain.agents import create_agent
from langchain.agents.middleware import (
    wrap_model_call,
    ModelRequest,
    ModelResponse,
)
from langchain_gigachat import GigaChat
from langgraph.checkpoint.postgres import PostgresSaver

from tools import multiply, add


load_dotenv()

llm = GigaChat(model="GigaChat-2")

# 1. Middleware: ограничиваем историю до 10 сообщений
@wrap_model_call
def limit_messages(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:

    # Берём последние 4 сообщения
    messages = request.messages[-4:]

    # Выводим количество сообщений
    print(f"Всего сообщений до ограничения: {len(request.messages)}")
    print(f"Сообщений передаём модели: {len(messages)}")

    # Выводим содержимое каждого сообщения
    print("\n--- Контекст GigaChat ---")

    for index, message in enumerate(messages, start=1):
        print(f"{index}. {message.type}: {message.content}")

    print("-----------------------\n")

    # Передаём сокращённую историю модели
    return handler(request.override(messages=messages))

# Подключение к PostgreSQL
db_uri = make_conninfo(
    host="127.0.0.1",
    port=5434,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

# Идентификатор диалога
config = {
    "configurable": {
        "thread_id": "conversation-1"
    }
}

with PostgresSaver.from_conn_string(db_uri) as memory:

    # Создаём необходимые таблицы
    memory.setup()

    agent = create_agent(
        model=llm,
        tools=[multiply, add],
        checkpointer=memory,
        middleware=[limit_messages],
        system_prompt="Ты полезный AI-ассистент. Отвечай на русском языке."
    )

    user_message = input("Вы: ")

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },
        config=config,
    )

    print("Агент:", result["messages"][-1].content)