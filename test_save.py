from database.crud import save_message

save_message(
    external_id="chat-101",
    role="client",
    content="Здравствуйте! Как восстановить пароль?",
)

print("Сообщение успешно сохранено")