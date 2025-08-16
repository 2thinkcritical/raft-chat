# 📄 Чат с документом (RAG Chat)

Полнофункциональное веб-приложение для чата с документами на основе RAG (Retrieval Augmented Generation), построенное на FastAPI и Gradio, упакованное в Docker Compose с PostgreSQL и векторной базой данных.

## 🏗️ Архитектура

Приложение состоит из шести основных компонентов:

### 🌐 Nginx (Reverse Proxy)
- **Порт**: 80
- **Функции**:
  - Единая точка входа для всех запросов
  - Маршрутизация API запросов на backend
  - Маршрутизация веб-запросов на frontend
  - Gzip сжатие и оптимизация

### 🔧 Backend (FastAPI)
- **Внутренний порт**: 8000
- **Функции**:
  - Обработка сообщений пользователя
  - RAG система для работы с документами
  - API для получения и очистки истории
  - Интеграция с векторной базой данных
  - Логирование и мониторинг

### 🗄️ PostgreSQL
- **Порт**: 5432
- **Функции**:
  - Персистентное хранение истории чата
  - Таблица messages для сообщений
  - Поддержка множественных пользователей

### 🔍 Vector Database (ChromaDB)
- **Функции**:
  - Хранение эмбеддингов документов
  - Семантический поиск по документам
  - Персистентное хранение на диске
  - Интеграция с Ollama для эмбеддингов

### 🎨 Frontend (Gradio)
- **Внутренний порт**: 7860
- **Функции**:
  - Веб-интерфейс для чата
  - Отправка сообщений на бэкенд
  - Отображение истории чата
  - Кнопка очистки истории
  - Профессиональное логирование

### 🌍 Cloudflared (Public Access)
- **Функции**:
  - Публичный HTTPS доступ без настройки домена
  - Автоматическое получение публичного URL
  - Безопасный туннель к локальному приложению

## 🚀 Быстрый старт

### Предварительные требования
- Docker
- Docker Compose
- Ollama (для эмбеддингов)
- OpenAI API ключ (для RAG)

### Запуск приложения

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd Raft
   ```

2. **Настройте переменные окружения:**
   ```bash
   # Создайте файл .env в корне проекта
   cp .env_example .env
   
   # Отредактируйте .env файл, указав ваши значения:
   # - OPENAI_API_KEY - ваш API ключ OpenAI
   # - Другие настройки можно оставить по умолчанию
   ```

3. **Запустите Ollama (если не запущен):**
   ```bash
   # Установите Ollama если нужно
   # https://ollama.ai/
   
   # Скачайте модель для эмбеддингов
   ollama pull mxbai-embed-large
   ```

4. **Запустите приложение:**
   ```bash
   docker-compose up --build
   ```

5. **Откройте браузер:**
   - **Основное приложение**: http://localhost
   - **API endpoints**: http://localhost/api/
   - **Health check**: http://localhost/health
   - **PostgreSQL**: localhost:5432 (для DBeaver)

6. **Получите публичный URL (опционально):**
   ```bash
   ./get_tunnel_url.sh
   ```

> **Примечание**: Все сервисы теперь доступны через единый порт 80 через Nginx reverse proxy.

## 📋 API Endpoints

### Backend API (http://localhost/api/)

- `GET /` - Проверка работоспособности API
- `POST /chat` - Отправка сообщения в чат
- `GET /history` - Получение истории чата
- `DELETE /history` - Очистка истории чата
- `GET /health` - Проверка состояния сервиса

### Примеры запросов

#### Отправка сообщения
```bash
curl -X POST "http://localhost/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Что такое HIPAA?",
    "timestamp": "2025-08-04T16:00:00",
    "user_id": "user"
  }'
```

#### Получение истории
```bash
curl "http://localhost/api/history"
```

#### Очистка истории
```bash
curl -X DELETE "http://localhost/api/history"
```

#### Проверка состояния
```bash
curl "http://localhost/api/health"
```

## 🧪 Тестирование

### Проверка типов
```bash
./check_types.sh
```

### Проверка стиля кода (ruff)
```bash
./check_ruff.sh
```

### Комплексная проверка качества
```bash
./check_all.sh
```

### Тестирование API
```bash
# Проверка работоспособности
curl http://localhost/api/health

# Тестирование чата
curl -X POST "http://localhost/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "Тест", "timestamp": "2025-08-04T16:00:00", "user_id": "user"}'
```

## 📁 Структура проекта

```
Raft/
├── app/
│   ├── main.py              # FastAPI backend
│   ├── database.py          # PostgreSQL модели и сессии
│   ├── vector_store.py      # ChromaDB и обработка PDF
│   ├── process_question.py  # RAG логика
│   ├── callbacks.py         # LangChain колбэки
│   └── resources/
│       └── hipaa-combined.pdf  # Документ для RAG
├── frontend/
│   └── gradio_app.py        # Gradio frontend
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile.backend       # Dockerfile для backend
├── Dockerfile.frontend      # Dockerfile для frontend
├── Dockerfile.nginx         # Dockerfile для Nginx
├── nginx.conf               # Конфигурация Nginx
├── requirements.txt         # Python зависимости
├── mypy.ini                 # Конфигурация проверки типов
├── check_types.sh           # Скрипт проверки типов
├── check_ruff.sh            # Скрипт проверки стиля кода
├── check_all.sh             # Комплексный скрипт проверок
├── get_tunnel_url.sh        # Получение публичного URL
├── .env                     # Переменные окружения
├── README.md                # Документация
├── USAGE.md                 # Инструкции по использованию
├── TYPE_CHECKING.md         # Документация по типам
└── .dockerignore            # Исключения для Docker
```

## 🔧 Конфигурация

### Переменные окружения

#### Основные настройки
- `OPENAI_API_KEY` - Ключ API OpenAI для RAG
- `DOCUMENT_FILENAME` - Имя PDF файла документа (по умолчанию: hipaa-combined.pdf)

#### База данных PostgreSQL
- `POSTGRES_DB` - Имя базы данных (по умолчанию: chat_db)
- `POSTGRES_USER` - Пользователь базы данных (по умолчанию: chat_user)
- `POSTGRES_PASSWORD` - Пароль базы данных (по умолчанию: chat_password)
- `POSTGRES_HOST` - Хост базы данных (по умолчанию: postgres)
- `POSTGRES_PORT` - Порт базы данных (по умолчанию: 5432)

#### RAG настройки
- `EMBEDDING_MODEL` - Модель для эмбеддингов (по умолчанию: mxbai-embed-large)
- `OLLAMA_EMBEDDING_BASE_URL` - URL Ollama сервера для эмбеддингов (по умолчанию: http://host.docker.internal:11434)
- `CHUNK_SIZE` - Размер чанков для разбивки документа (по умолчанию: 1200)
- `CHUNK_OVERLAP` - Перекрытие между чанками (по умолчанию: 200)
- `SEARCH_K` - Количество документов для поиска (по умолчанию: 10)

#### LLM настройки
- `LLM_MODEL` - Модель для генерации ответов (по умолчанию: gpt-4.1)
- `LLM_TEMPERATURE` - Температура для LLM (0.0 = детерминированный, 1.0 = креативный, по умолчанию: 0.0)

#### Сетевые настройки
- `API_BASE_URL` - URL бэкенда (по умолчанию: http://nginx/api)
- `FRONTEND_PORT` - Порт frontend (по умолчанию: 7860)
- `BACKEND_PORT` - Порт backend (по умолчанию: 8000)
- `NGINX_PORT` - Порт nginx (по умолчанию: 80)



### Порты
- Nginx: 80 (основной)
- PostgreSQL: 5432 (для DBeaver)
- Backend: 8000 (внутренний)
- Frontend: 7860 (внутренний)

## 📝 Особенности

### RAG система
- **Векторная база**: ChromaDB с персистентным хранением
- **Эмбеддинги**: Ollama mxbai-embed-large модель (настраивается)
- **LLM**: OpenAI GPT-4 для генерации ответов (модель и температура настраиваются)
- **Документ**: HIPAA PDF для демонстрации (имя файла настраивается)
- **Поиск**: MultiQueryRetriever с переформулировкой вопросов
- **Чанкинг**: Настраиваемый размер чанков и перекрытие
- **Поиск**: Настраиваемое количество документов для поиска (SEARCH_K)
- **Логирование**: Детальные колбэки для отладки

### История сообщений
- История чата хранится в PostgreSQL
- Сообщения сохраняются между перезапусками
- Поддержка очистки истории через API и UI
- Автоматическая загрузка истории при открытии интерфейса

### Интерфейс
- Современный UI с использованием Gradio
- Поле ввода внизу интерфейса
- Кнопка отправки и очистки
- Отображение времени сообщений
- Адаптивный дизайн

### Безопасность
- Валидация входных данных через Pydantic
- Обработка ошибок на всех уровнях
- Типизация кода (type annotations)
- Проверка типов с помощью mypy
- Логирование всех операций

## 🔮 Планы развития

### RAG система
- [x] Интеграция с векторными базами данных (ChromaDB)
- [x] Система эмбеддингов (Ollama)
- [x] Поиск по документам (MultiQueryRetriever)
- [x] Генерация ответов на основе контекста (OpenAI)
- [ ] Поддержка множественных документов
- [ ] Загрузка документов через UI

### Улучшения
- [x] Персистентное хранение истории (PostgreSQL)
- [x] Публичный доступ (Cloudflared)
- [x] Проверка типов (mypy)
- [x] Профессиональное логирование
- [ ] Аутентификация пользователей
- [ ] Экспорт истории чата
- [ ] Мониторинг и метрики

## 🐛 Устранение неполадок

### Проблемы с Docker
```bash
# Остановить и удалить контейнеры
docker-compose down

# Очистить кэш Docker
docker system prune -a

# Пересобрать образы
docker-compose build --no-cache
```

### Проблемы с портами
Если порты заняты, измените их в `docker-compose.yml`:
```yaml
ports:
  - "8080:80"    # Nginx
  - "5433:5432"  # PostgreSQL
```

### Проблемы с RAG
```bash
# Проверьте, что Ollama запущен
ollama list

# Проверьте OpenAI API ключ
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Проверьте логи
docker-compose logs backend
```

## 📄 Лицензия

MIT License

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 🗄️ Подключение к базе данных

### DBeaver
1. Создайте новое подключение PostgreSQL
2. **Host**: localhost
3. **Port**: 5432
4. **Database**: chatdb
5. **Username**: chatuser
6. **Password**: chatpass

### Прямое подключение
```bash
# Через Docker
docker exec -it chat-postgres psql -U chatuser -d chatdb

# Через psql (если установлен)
psql -h localhost -p 5432 -U chatuser -d chatdb
```

## 📚 Дополнительная документация

- [USAGE.md](USAGE.md) - Подробные инструкции по использованию
- [TYPE_CHECKING.md](TYPE_CHECKING.md) - Документация по проверке типов

## 📞 Поддержка

Если у вас есть вопросы или проблемы, создайте Issue в репозитории. 