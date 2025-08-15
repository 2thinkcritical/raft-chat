"""Утилиты для работы с документами."""

import logging
import os
from typing import Any

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


def get_pdf_info(pdf_path: str) -> dict[str, Any]:
    """Получить реальную информацию о PDF документе.

    Args:
        pdf_path: Путь к PDF файлу

    Returns:
        Словарь с информацией о документе
    """
    try:
        if not os.path.exists(pdf_path):
            return {
                "name": "Document not found",
                "type": "Unknown",
                "size": "Unknown",
                "pages": 0,
                "description": "Document file not available",
            }

        # Получаем размер файла
        file_size = os.path.getsize(pdf_path)
        size_kb = file_size / 1024

        # Открываем PDF для получения метаданных
        doc = fitz.open(pdf_path)

        # Получаем количество страниц
        page_count = len(doc)

        # Получаем метаданные
        metadata = doc.metadata

        # Извлекаем название из метаданных или имени файла
        title = metadata.get("title", "")
        if not title:
            # Если метаданные не содержат название, используем имя файла
            filename = os.path.basename(pdf_path)
            title = os.path.splitext(filename)[0]  # Убираем расширение

        # Получаем автора и другие метаданные
        author = metadata.get("author", "")
        subject = metadata.get("subject", "")
        creator = metadata.get("creator", "")

        # Формируем описание
        description_parts = []
        if author:
            description_parts.append(f"Author: {author}")
        if subject:
            description_parts.append(f"Subject: {subject}")
        if creator:
            description_parts.append(f"Created with: {creator}")

        description = (
            " | ".join(description_parts) if description_parts else "PDF document"
        )

        doc.close()

        return {
            "name": title,
            "type": "PDF",
            "size": f"{size_kb:.1f}KB",
            "pages": page_count,
            "author": author,
            "subject": subject,
            "creator": creator,
            "description": description,
            "filename": os.path.basename(pdf_path),
        }

    except Exception as e:
        logger.error(f"Error reading PDF info: {e}")
        return {
            "name": "Error reading document",
            "type": "Unknown",
            "size": "Unknown",
            "pages": 0,
            "description": f"Error: {str(e)}",
        }
