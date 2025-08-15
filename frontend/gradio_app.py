import logging
import os
from datetime import datetime
from typing import Any

import gradio as gr
import requests

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Конфигурация API
# Используем относительный путь для работы через nginx
API_BASE_URL = os.getenv("API_BASE_URL", "http://nginx/api")


def send_message(message: str) -> tuple[str, list[list[str]]]:
    """
    Отправить сообщение в чат с документом

    Args:
        message: Текст сообщения

    Returns:
        Tuple с пустой строкой (для очистки поля ввода) и списком сообщений
    """
    if not message.strip():
        logger.warning("Попытка отправить пустое сообщение")
        return "", []

    logger.info(
        f"Отправка сообщения: '{message[:50]}{'...' if len(message) > 50 else ''}'"
    )

    try:
        # Создаем объект сообщения
        message_data = {
            "text": message,
            "timestamp": datetime.now().isoformat(),
            "user_id": "user",
        }

        # Отправляем сообщение на бэкенд
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=message_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            # Получаем обновленную историю с бэкенда
            history_response = requests.get(f"{API_BASE_URL}/history")
            if history_response.status_code == 200:
                history_data = history_response.json()

                # Преобразуем историю в формат для Gradio
                chat_messages = []
                for item in history_data:
                    timestamp = datetime.fromisoformat(
                        item["timestamp"].replace("Z", "+00:00")
                    )
                    formatted_time = timestamp.strftime("%H:%M:%S")
                    chat_messages.append(
                        [f"[{formatted_time}] Вы", item["user_message"]]
                    )
                    chat_messages.append(
                        [f"[{formatted_time}] Документ", item["bot_response"]]
                    )

                return "", chat_messages
            else:
                error_message = [
                    [
                        "Система",
                        f"Ошибка получения истории: {history_response.status_code}",
                    ]
                ]
                return "", error_message
        else:
            error_message = [
                ["Система", f"Ошибка отправки сообщения: {response.status_code}"]
            ]
            return "", error_message

    except requests.exceptions.RequestException as e:
        error_message = [["Система", f"Ошибка соединения с сервером: {str(e)}"]]
        return "", error_message
    except Exception as e:
        error_message = [["Система", f"Неожиданная ошибка: {str(e)}"]]
        return "", error_message


def load_chat_history() -> list[list[str]]:
    """
    Загрузить историю чата с бэкенда

    Returns:
        Список сообщений в формате для Gradio
    """
    logger.info("Загрузка истории чата с backend")
    try:
        response = requests.get(f"{API_BASE_URL}/history")
        logger.info(f"GET /history - статус: {response.status_code}")
        if response.status_code == 200:
            history_data = response.json()
            logger.info(f"Получено {len(history_data)} сообщений из истории")

            # Преобразуем историю в формат для Gradio
            chat_messages = []
            for item in history_data:
                timestamp = datetime.fromisoformat(
                    item["timestamp"].replace("Z", "+00:00")
                )
                formatted_time = timestamp.strftime("%H:%M:%S")
                chat_messages.append([f"[{formatted_time}] Вы", item["user_message"]])
                chat_messages.append(
                    [f"[{formatted_time}] Документ", item["bot_response"]]
                )

            logger.info(
                f"Подготовлено {len(chat_messages)} элементов для отображения в Gradio"
            )
            return chat_messages
        else:
            logger.error(f"Ошибка получения истории чата: HTTP {response.status_code}")
            return [["Система", f"Ошибка загрузки истории: {response.status_code}"]]
    except Exception as e:
        logger.error(f"Исключение при загрузке истории чата: {str(e)}")
        return [["Система", f"Ошибка загрузки истории: {str(e)}"]]


def clear_chat() -> list[list[str]]:
    """
    Очистить историю чата на бэкенде

    Returns:
        Пустой список сообщений
    """
    try:
        response = requests.delete(f"{API_BASE_URL}/history")
        if response.status_code == 200:
            return []
        else:
            return [["Система", f"Ошибка очистки истории: {response.status_code}"]]
    except Exception as e:
        return [["Система", f"Ошибка очистки истории: {str(e)}"]]


def get_document_info() -> tuple[str, str]:
    """
    Получить информацию о документе с бэкенда

    Returns:
        Tuple с названием документа и названием файла
    """
    logger.info(
        f"Попытка получить информацию о документе из: {API_BASE_URL}/document-info"
    )
    try:
        response = requests.get(f"{API_BASE_URL}/document-info")
        logger.info(f"Ответ от API: статус {response.status_code}")

        if response.status_code == 200:
            doc_info: dict[str, Any] = response.json()
            logger.info(f"Получена информация о документе: {doc_info}")

            document_name = str(doc_info.get("name", "Документ"))
            filename = str(doc_info.get("filename", "unknown.pdf"))

            logger.info(f"Извлечено: название='{document_name}', файл='{filename}'")
            return document_name, filename
        else:
            logger.error(f"API вернул ошибку: {response.status_code} - {response.text}")
            return "Документ", "unknown.pdf"
    except Exception as e:
        logger.error(f"Ошибка получения информации о документе: {e}")
        return "Документ", "unknown.pdf"


def create_chat_interface() -> gr.Interface:
    """
    Создать интерфейс чата с документом

    Returns:
        Gradio интерфейс
    """
    with gr.Blocks(title="Чат с документом", theme=gr.themes.Soft()) as interface:
        # Создаем компоненты для отображения информации о документе
        header_markdown = gr.Markdown("# 📄 Чат с документом: Загрузка...")
        file_info_markdown = gr.Markdown("**Файл:** Загрузка...")

        gr.Markdown("Задайте вопрос о документе и получите ответ")

        # Область чата (вверху)
        chat_area = gr.Chatbot(label="Чат", height=400, show_label=True)

        # Поле ввода и кнопки (внизу)
        with gr.Row():
            with gr.Column(scale=4):
                # Поле ввода сообщения
                message_input = gr.Textbox(
                    label="Вопрос",
                    placeholder="Задайте вопрос о документе...",
                    lines=1,
                    max_lines=5,
                )

            with gr.Column(scale=1):
                # Кнопка отправки
                send_button = gr.Button("Отправить", variant="primary", size="lg")

        # Кнопка очистки чата
        clear_button = gr.Button("Очистить чат", variant="secondary", size="sm")

        # Обработчики событий
        send_button.click(
            fn=send_message, inputs=[message_input], outputs=[message_input, chat_area]
        )

        message_input.submit(
            fn=send_message, inputs=[message_input], outputs=[message_input, chat_area]
        )

        clear_button.click(fn=clear_chat, outputs=[chat_area])

        # Функция для загрузки информации о документе
        def load_document_info() -> tuple[str, str]:
            try:
                document_name, filename = get_document_info()
                header_text = f"# 📄 Чат с документом: {document_name}"
                file_info_text = f"**Файл:** `{filename}`"
                return header_text, file_info_text
            except Exception as e:
                logger.error(f"Ошибка получения информации о документе: {e}")
                return "# 📄 Чат с документом: Документ", "**Файл:** `unknown.pdf`"

        # Загружаем информацию о документе при запуске
        interface.load(
            fn=load_document_info, outputs=[header_markdown, file_info_markdown]
        )

        # Загружаем историю при запуске
        interface.load(fn=load_chat_history, outputs=[chat_area])

    return interface


if __name__ == "__main__":
    # Создаем и запускаем интерфейс
    chat_interface = create_chat_interface()
    chat_interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        quiet=True,
        max_threads=1,
        prevent_thread_lock=True,
    )
