import logging
import os

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.retrievers import MultiQueryRetriever
from langchain.schema.output_parser import StrOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma

from app.callbacks import MultiQueryLoggingCallback, QuestionLoggingCallback

from .prompts import get_prompt

# Загружаем переменные из .env
load_dotenv()

# Настройка логирования
logger = logging.getLogger(__name__)

# Получаем API ключ из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def process_question(
    question: str, vector_db: Chroma, selected_model: str = "gpt-4.1"
) -> str:
    """
    Обрабатывает вопрос пользователя с использованием RAG (Retrieval Augmented Generation).

    Args:
        question: Вопрос пользователя
        vector_db: Векторная база данных Chroma
        selected_model: Модель OpenAI для использования

    Returns:
        str: Ответ на вопрос на основе найденных документов
    """
    logger.info("=== Starting RAG processing ===")
    logger.info(f"Original question: {question}")
    logger.info(f"Model: {selected_model}")

    # Инициализируем колбэки
    question_callback = QuestionLoggingCallback()
    mqr_callback = MultiQueryLoggingCallback()
    mqr_callback.original_question = question

    callbacks = [question_callback, mqr_callback]

    # 1) LLM for both MQR and final answer
    llm = ChatOpenAI(
        model=selected_model,  # или gpt-4, gpt-4o и т.д.
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
        callbacks=callbacks,
    )

    # 2) Multi-query prompt
    query_prompt_text = get_prompt("multi_query_retriever")
    if query_prompt_text is None:
        raise ValueError("Не удалось загрузить промпт multi_query_retriever")

    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template=query_prompt_text,
    )

    # 3) Retriever with MQR
    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(search_kwargs={"k": 10}),
        llm,
        prompt=QUERY_PROMPT,
        include_original=True,
    )

    # -------- NEW: run retriever first → log chunks -----------------
    docs = retriever.invoke(question, config={"callbacks": callbacks})  # list[Document]

    logger.info("Top-K chunks selected:")
    for d in docs:
        cid = d.metadata.get("chunk_id")
        cite = d.metadata.get("citation")
        preview = d.page_content.replace("\n", " ")[:60] + "…"
        logger.info(f"  {cid:<12} {cite:<10} {preview}")

    # Build context string the same way format_docs() does
    context_parts = []
    for d in docs:
        m = d.metadata
        context_part = (
            f"[{m['citation']}]  "
            f"title: {m.get('title', '').strip()}  |  "
            f"part: {m.get('part')}{m.get('subpart', '') or ''}  |  "
            f"pages: {m.get('page_start')}-{m.get('page_end')}\n"
            f"{d.page_content.strip()}"
        )
        context_parts.append(context_part)

    context_str = "\n\n".join(context_parts)
    logger.info(f"Context: {context_str}")

    # 4) RAG prompt
    rag_prompt_text = get_prompt("rag_prompt")
    if rag_prompt_text is None:
        raise ValueError("Не удалось загрузить промпт rag_prompt")

    RAG_PROMPT = ChatPromptTemplate.from_template(rag_prompt_text)

    messages = RAG_PROMPT.format_messages(context=context_str, question=question)

    # Логируем финальный промпт
    logger.info("Final RAG prompt:")
    for i, message in enumerate(messages):
        logger.info(f"Message {i + 1} ({message.type}): {message.content}")

    # 5) Ask LLM & parse
    raw_response = llm.invoke(messages, config={"callbacks": callbacks})
    response: str = StrOutputParser().invoke(raw_response)

    logger.info("LLM raw response:")
    logger.info(f"Content: {raw_response.content}")
    logger.info("Final parsed response generated")

    # Финальное логирование всех вопросов
    logger.info("=== Question Summary ===")
    logger.info(f"Original question: {question}")
    if mqr_callback.reformulated_questions:
        logger.info("Reformulated questions:")
        for i, q in enumerate(mqr_callback.reformulated_questions, 1):
            logger.info(f"  {i}. {q}")
    logger.info("=== End RAG processing ===")

    return response
