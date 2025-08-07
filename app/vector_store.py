import logging
import os
import re
from typing import Optional, Union

import fitz
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Отключаем телеметрию ChromaDB
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Настройка логирования
logger = logging.getLogger(__name__)

# Глобальная переменная для хранения векторной базы
vector_db: Optional[Chroma] = None

# Путь к директории для сохранения векторной базы
VECTOR_DB_PATH = "/app/vector_db"


def create_vector_db(pdf_path: str) -> Chroma:
    """
    Обрабатывает загруженный PDF (HIPAA), формирует
    чанки c богатыми метаданными и строит Chroma-хранилище.

    Args:
        pdf_path: Путь к PDF файлу

    Returns:
        Chroma: векторная база, готовая к поиску.
    """
    logger.info(f"Create vector DB from: {pdf_path}")

    # ── 2. Читаем весь текст страниц через PyMuPDF ───────────
    doc = fitz.open(pdf_path)
    raw_pages = [p.get_text("text") for p in doc]

    # ── 3. Регэкспы для структуры ────────────────────────────
    part_rx = re.compile(r"^PART\s+(\d{3})", re.I)
    subpart_rx = re.compile(
        r"^SUBPART\s+([A-Z])(?:[\s—\-:]+(.+))?", re.I
    )  # ← ловим доп. заголовок после SUBPART X
    header_rx = re.compile(r"^\s*§\s*(\d{3}\.\d+)\s{2,}", re.I)

    def is_header(line: str) -> bool:
        return bool(header_rx.match(line.strip()))

    # ── 4. Проход: убираем TOC, строим annotated список ──────
    state: dict[str, Optional[str]] = {
        "part": None,
        "subpart": None,
        "section": None,
        "title": None,
    }
    annotated = []
    IN_TOC = False

    for page_no, text in enumerate(raw_pages, 1):
        if IN_TOC and "HIPAA Administrative Simplification Regulation Text" in text:
            IN_TOC = False
        if IN_TOC:
            continue

        for line in text.splitlines():
            if m := part_rx.match(line):
                state["part"], state["subpart"] = m.group(1), None
            elif m := subpart_rx.match(line):
                state["subpart"] = m.group(1)
                title = m.group(2)
                if title:
                    # Убираем лишние точки, пробелы
                    title = re.sub(r"[\.—\-:]+", " ", title).strip()
                    state["title"] = title
                else:
                    state["title"] = None
            elif m := header_rx.match(line):
                state["section"] = m.group(1)
                # аккуратный заголовок после номера
                title = line.split(None, 2)[-1]
                title = re.sub(r"^[\s\.]+", "", title).strip()
                state["title"] = title
            annotated.append((page_no, state.copy(), line))

    # ── 5. Склеиваем строки в блоки § ─────────────────────────
    def new_meta(
        st: dict[str, Optional[str]], pg: int, idx: int
    ) -> dict[str, Union[str, int]]:
        cite = f"§{st['section']}" if st["section"] else "unknown"
        suf = st["section"].split(".")[1] if st["section"] else "xx"
        cid = f"{st['part']}-{suf}-{idx:02d}"
        return {
            "part": st["part"] or "unknown",
            "subpart": st["subpart"] or "unknown",
            "section": st["section"] or "unknown",
            "title": st["title"] or "unknown",
            "page_start": pg,
            "page_end": pg,
            "chunk_id": cid,
            "citation": cite,
        }

    blocks, buf, cur_meta = [], [], None
    for pg, st, line in annotated:
        if cur_meta is None:
            cur_meta = new_meta(st, pg, 0)
        elif is_header(line) and st["section"] != cur_meta["section"]:
            if any(s.strip() for s in buf) and cur_meta is not None:
                cur_meta["text"] = "\n".join(buf)
                blocks.append(cur_meta)
            cur_meta, buf = new_meta(st, pg, 0), []
        if cur_meta is not None:
            buf.append(line)
            cur_meta["page_end"] = pg
    if any(s.strip() for s in buf) and cur_meta is not None:
        cur_meta["text"] = "\n".join(buf)
        blocks.append(cur_meta)

    # ── 6. Чанкинг 1200/200 ──────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1_200, chunk_overlap=200, separators=["\n\n", "\n", ". "]
    )
    documents = []
    for b in blocks:
        for i, chunk in enumerate(splitter.split_text(b["text"]), 1):
            meta = b.copy()
            chunk_id = str(b["chunk_id"])
            base = chunk_id.rsplit("-", 1)[0]  # '164-502'
            meta["chunk_id"] = f"{base}-{i:02d}"
            documents.append(Document(page_content=chunk, metadata=meta))
    logger.info(f"Created {len(documents)} chunks")

    # ── 7. Индексация в Chroma (с persist) ─────────────────
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large", base_url="http://host.docker.internal:11434"
    )

    # Создаем persistent ChromaDB
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="hipaa_document",
        persist_directory=VECTOR_DB_PATH,
    )

    # Сохраняем базу на диск
    vectordb.persist()
    logger.info(f"Vector DB saved to: {VECTOR_DB_PATH}")

    logger.info("Vector DB ready")
    return vectordb


def load_vector_db() -> Optional[Chroma]:
    """
    Загружает векторную базу из файла, если она существует

    Returns:
        Chroma или None если файл не найден
    """
    if not os.path.exists(VECTOR_DB_PATH):
        logger.info(f"Vector DB not found at: {VECTOR_DB_PATH}")
        return None

    try:
        logger.info(f"Loading vector DB from: {VECTOR_DB_PATH}")
        embeddings = OllamaEmbeddings(
            model="mxbai-embed-large", base_url="http://host.docker.internal:11434"
        )

        vectordb = Chroma(
            collection_name="hipaa_document",
            embedding_function=embeddings,
            persist_directory=VECTOR_DB_PATH,
        )

        # Проверяем, что база действительно загружена
        collection = vectordb._collection
        if collection.count() == 0:
            logger.warning("Vector DB file exists but is empty")
            return None

        logger.info(
            f"Vector DB loaded successfully with {collection.count()} documents"
        )
        return vectordb

    except Exception as e:
        logger.error(f"Failed to load vector DB: {e}")
        return None


def initialize_vector_db() -> Chroma:
    """
    Инициализирует векторную базу при запуске приложения.
    Сначала пытается загрузить из файла, если не получается - создает новую.

    Returns:
        Chroma: инициализированная векторная база
    """
    global vector_db

    if vector_db is not None:
        logger.info("Vector DB already initialized")
        return vector_db

    # Сначала пытаемся загрузить из файла
    vector_db = load_vector_db()
    if vector_db is not None:
        logger.info("Vector DB loaded from file successfully")
        return vector_db

    # Если файл не найден или поврежден, создаем новую базу
    pdf_path = os.path.join(
        os.path.dirname(__file__), "resources", "hipaa-combined.pdf"
    )

    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        logger.info("Creating new vector database...")
        vector_db = create_vector_db(pdf_path)
        logger.info("Vector database created and saved successfully")
        return vector_db
    except Exception as e:
        logger.error(f"Failed to create vector database: {e}")
        raise


def get_vector_db() -> Optional[Chroma]:
    """
    Получить инициализированную векторную базу

    Returns:
        Chroma или None если база не инициализирована
    """
    return vector_db
