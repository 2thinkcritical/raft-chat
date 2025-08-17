import logging
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_document_path
from app.database import Message as DBMessage
from app.database import get_db, init_db
from app.document_utils import get_pdf_info
from app.process_question import process_question
from app.vector_store import get_vector_db, initialize_vector_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Чат с документом API", version="1.0.0")


class Message(BaseModel):
    text: str
    timestamp: datetime
    user_id: str = "user"


class ChatResponse(BaseModel):
    text: str
    timestamp: datetime
    user_id: str
    source: str = "document"


class ChatHistoryItem(BaseModel):
    user_message: str
    bot_response: str
    timestamp: datetime
    user_id: str


class DocumentInfo(BaseModel):
    name: str
    filename: str


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    service: str
    history_count: int
    vector_db_status: str


# Убираем хранение в памяти - теперь используем базу данных


@app.on_event("startup")
async def startup_event() -> None:
    """
    Инициализация при запуске приложения
    """
    try:
        logger.info("Starting application initialization...")
        # Инициализируем базу данных
        init_db()
        logger.info("Database initialized successfully")
        # Инициализируем векторную базу
        initialize_vector_db()
        logger.info("Application initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


@app.get("/", response_model=dict[str, str])
async def root() -> dict[str, str]:
    return {"message": "Чат с документом API работает!"}


@app.post("/chat", response_model=ChatResponse)
async def chat_with_document(
    message: Message, db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Обработать сообщение пользователя с использованием RAG

    Использует векторную базу для поиска релевантной информации
    и формирует ответ на основе найденных документов
    """
    try:
        logger.info(f"[{message.timestamp}] {message.user_id}: {message.text}")

        # Получаем векторную базу
        vector_db = get_vector_db()
        if vector_db is None:
            raise HTTPException(
                status_code=500, detail="Vector database not initialized"
            )

        # Используем новую логику обработки вопросов
        response_text = process_question(message.text, vector_db)

        # Создаем ответ
        response = ChatResponse(
            text=response_text,
            timestamp=message.timestamp,
            user_id=message.user_id,
            source="document",
        )

        # Сохраняем в базу данных
        db_message = DBMessage(
            user_message=message.text,
            bot_response=response_text,
            timestamp=message.timestamp,
            user_id=message.user_id,
        )
        db.add(db_message)
        db.commit()

        return response

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(
            status_code=500, detail=f"Ошибка при обработке сообщения: {str(e)}"
        )


@app.get("/history", response_model=list[ChatHistoryItem])
async def get_chat_history(db: Session = Depends(get_db)) -> list[ChatHistoryItem]:
    """
    Получить историю чата из базы данных
    """
    db_messages = db.query(DBMessage).order_by(DBMessage.timestamp.asc()).all()

    history_items = []
    for db_msg in db_messages:
        history_item = ChatHistoryItem(
            user_message=db_msg.user_message,
            bot_response=db_msg.bot_response,
            timestamp=db_msg.timestamp,
            user_id=db_msg.user_id,
        )
        history_items.append(history_item)

    return history_items


@app.delete("/history", response_model=dict[str, str])
async def clear_chat_history(db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Очистить историю чата из базы данных
    """
    db.query(DBMessage).delete()
    db.commit()
    return {"message": "История чата очищена"}


@app.get("/document-info", response_model=DocumentInfo)
async def get_document_info() -> DocumentInfo:
    """
    Получить информацию о загруженном документе
    """
    try:
        # Путь к PDF документу
        pdf_path = get_document_path()

        # Получаем реальную информацию о PDF
        pdf_info = get_pdf_info(pdf_path)

        # Возвращаем только нужные поля
        return DocumentInfo(
            name=pdf_info.get("name", "Unknown Document"),
            filename=pdf_info.get("filename", "unknown.pdf"),
        )
    except Exception as e:
        logger.error(f"Failed to get document info: {e}")
        return DocumentInfo(name="Unknown Document", filename="unknown.pdf")


@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    vector_db_status = (
        "initialized" if get_vector_db() is not None else "not_initialized"
    )
    history_count = db.query(DBMessage).count()
    logger.info(
        f"Health check: vector_db_status={vector_db_status}, history_count={history_count}"
    )
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        service="document-chat",
        history_count=history_count,
        vector_db_status=vector_db_status,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
