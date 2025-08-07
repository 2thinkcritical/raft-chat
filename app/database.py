import os
from collections.abc import Generator
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

if TYPE_CHECKING:
    from sqlalchemy.ext.declarative import DeclarativeMeta

# Получаем URL базы данных из переменной окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://chatuser:chatpass@postgres:5432/chatdb"
)

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base: "DeclarativeMeta" = declarative_base()


class Message(Base):
    """Модель для хранения сообщений чата"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String(50), default="user", nullable=False)


def get_db() -> Generator[Session, None, None]:
    """Получить сессию базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Инициализировать базу данных (создать таблицы)"""
    Base.metadata.create_all(bind=engine)
