"""Конфигурация проекта."""

import logging
import os
from typing import Optional

from dotenv import load_dotenv

# Настраиваем логгер для конфигурации
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env файла
try:
    # Определяем путь к .env файлу
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    load_dotenv(env_path)
    logger.info(f"Загружен .env файл: {env_path}")
except FileNotFoundError:
    logger.warning(f".env файл не найден: {env_path}")


class Config:
    """Основной класс конфигурации."""

    # Пути к документам (читаем из переменных окружения)
    DOCUMENT_FILENAME = os.getenv("DOCUMENT_FILENAME", "hipaa-combined.pdf")

    # Настройки базы данных PostgreSQL
    POSTGRES_DB = os.getenv("POSTGRES_DB", "chat_db")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "chat_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "chat_password")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

    # RAG настройки
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "mxbai-embed-large")
    OLLAMA_EMBEDDING_BASE_URL = os.getenv(
        "OLLAMA_EMBEDDING_BASE_URL", "http://host.docker.internal:11434"
    )
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    SEARCH_K = int(os.getenv("SEARCH_K", "10"))

    # LLM настройки
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    @property
    def database_url(self) -> str:
        """Получить URL для подключения к базе данных."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @classmethod
    def get_document_path(cls, base_path: Optional[str] = None) -> str:
        """
        Получить полный путь к PDF документу.

        Args:
            base_path: Базовый путь (если не указан, определяется автоматически)

        Returns:
            Полный путь к PDF документу
        """
        if base_path is None:
            # Определяем базовый путь автоматически
            if cls._is_running_in_docker():
                # В Docker контейнере
                base_path = "/app"
            else:
                # В локальной среде
                base_path = os.path.dirname(os.path.dirname(__file__))

        # Формируем полный путь
        document_path = os.path.join(
            base_path, "app", "resources", cls.DOCUMENT_FILENAME
        )

        return document_path

    @staticmethod
    def _is_running_in_docker() -> bool:
        """
        Проверить, запущено ли приложение в Docker контейнере.

        Returns:
            True, если запущено в Docker
        """
        return os.path.exists("/.dockerenv") or os.path.exists("/proc/1/cgroup")


# Создаем глобальный экземпляр конфигурации
config = Config()


# Удобные функции для быстрого доступа к настройкам
def get_document_path() -> str:
    """Получить путь к PDF документу."""
    return config.get_document_path()


# Функции для доступа к настройкам базы данных
def get_database_url() -> str:
    """Получить URL для подключения к базе данных."""
    return config.database_url


# Функции для доступа к RAG настройкам
def get_embedding_model() -> str:
    """Получить модель для эмбеддингов."""
    return config.EMBEDDING_MODEL


def get_ollama_embedding_base_url() -> str:
    """Получить URL Ollama сервера для эмбеддингов."""
    return config.OLLAMA_EMBEDDING_BASE_URL


def get_chunk_size() -> int:
    """Получить размер чанков для разбивки документа."""
    return config.CHUNK_SIZE


def get_chunk_overlap() -> int:
    """Получить перекрытие между чанками."""
    return config.CHUNK_OVERLAP


def get_search_k() -> int:
    """Получить количество документов для поиска."""
    return config.SEARCH_K


# Функции для доступа к LLM настройкам
def get_llm_model() -> str:
    """Получить модель для генерации ответов."""
    return config.LLM_MODEL


def get_llm_temperature() -> float:
    """Получить температуру для LLM модели."""
    return config.LLM_TEMPERATURE


def get_openai_api_key() -> Optional[str]:
    """Получить OpenAI API ключ."""
    return config.OPENAI_API_KEY
