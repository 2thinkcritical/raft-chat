import logging
from typing import Any, Optional

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult

logger = logging.getLogger(__name__)


class QuestionLoggingCallback(BaseCallbackHandler):
    """
    Кастомный колбэк для логирования всех вопросов, включая переформулированные
    """

    def __init__(self) -> None:
        self.original_question: Optional[str] = None
        self.reformulated_questions: list[str] = []
        self.final_question: Optional[str] = None

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        """Логируем входные промпты LLM"""
        for i, prompt in enumerate(prompts):
            logger.info(f"LLM Input {i + 1}: {prompt.strip()}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Логируем ответы LLM"""
        if hasattr(response, "content"):
            logger.info(f"LLM Output: {response.content.strip()}")

    def on_retriever_start(
        self, serialized: dict[str, Any], query: str, **kwargs: Any
    ) -> None:
        """Логируем запросы к ретриверу"""
        logger.info(f"Retriever Query: {query}")

    def on_retriever_end(self, documents: list[Any], **kwargs: Any) -> None:
        """Логируем результаты ретривера"""
        logger.info(f"Retriever found {len(documents)} documents")
        for i, doc in enumerate(documents):
            cid = doc.metadata.get("chunk_id", "unknown")
            cite = doc.metadata.get("citation", "unknown")
            preview = doc.page_content.replace("\n", " ")[:60] + "…"
            logger.info(f"  Document {i + 1}: {cid} | {cite} | {preview}")


class MultiQueryLoggingCallback(BaseCallbackHandler):
    """
    Специальный колбэк для логирования MultiQueryRetriever
    """

    def __init__(self) -> None:
        self.original_question: Optional[str] = None
        self.reformulated_questions: list[str] = []

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        """Логируем промпты для переформулировки вопросов"""
        for prompt in prompts:
            if "Rewrite the question" in prompt:
                logger.info(
                    "=== MultiQueryRetriever: Generating reformulated questions ==="
                )
                logger.info(f"Original question: {self.original_question}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Логируем переформулированные вопросы"""
        if hasattr(response, "content"):
            reformulated = response.content.strip().split("\n")
            logger.info("=== Reformulated questions ===")
            for i, question in enumerate(reformulated, 1):
                if question.strip():
                    logger.info(f"  {i}. {question.strip()}")
                    self.reformulated_questions.append(question.strip())
            logger.info("=== End reformulated questions ===")
