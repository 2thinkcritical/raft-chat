# 📖 Инструкция по использованию RAG Chat

## 🚀 Быстрый старт

### 1. Предварительная настройка
```bash
# Клонируйте репозиторий (если необходимо)
git clone <repository-url>
cd Raft

# Создайте файл с переменными окружения
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Убедитесь, что Ollama запущен и модель скачана
ollama pull mxbai-embed-large
```

### 2. Запуск приложения
```bash
# Запустите все сервисы
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### 3. Открытие интерфейса
- **Веб-интерфейс**: http://localhost
- **API документация**: http://localhost/api/docs
- **Health check**: http://localhost/health
- **PostgreSQL**: localhost:5432 (для DBeaver)

## 💬 Использование чата

### Основные функции
1. **Отправка сообщения**:
   - Введите вопрос о документе в поле "Вопрос" внизу интерфейса
   - Нажмите кнопку "Отправить" или Enter
   - Получите ответ на основе содержимого HIPAA документа

2. **История сообщений**:
   - Все сообщения автоматически сохраняются в PostgreSQL
   - История загружается при открытии интерфейса
   - Сообщения сохраняются между перезапусками сервера

3. **Очистка истории**:
   - Нажмите кнопку "Очистить чат" для удаления всей истории
   - История очищается как в интерфейсе, так и в базе данных

### Особенности работы
- **RAG система**: Система использует Retrieval Augmented Generation
- **Семантический поиск**: Поиск по векторной базе ChromaDB
- **Контекстные ответы**: Ответы основаны на содержимом HIPAA документа
- **Персистентность**: История хранится в PostgreSQL
- **Время**: Каждое сообщение отображается с временной меткой
- **Логирование**: Все операции логируются для отладки

## 🔧 API использование

### Отправка сообщения
```bash
curl -X POST "http://localhost/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Что такое HIPAA?",
    "timestamp": "2025-08-04T16:00:00",
    "user_id": "user"
  }'
```

### Получение истории
```bash
curl "http://localhost/api/history"
```

### Очистка истории
```bash
curl -X DELETE "http://localhost/api/history"
```

### Проверка состояния
```bash
curl "http://localhost/api/health"
```

### Получение публичного URL
```bash
./get_tunnel_url.sh
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

### Ручное тестирование
1. Откройте http://localhost
2. Отправьте вопрос о HIPAA (например: "Что такое HIPAA?")
3. Получите ответ на основе документа
4. Обновите страницу - история должна сохраниться
5. Нажмите "Очистить чат" - история должна исчезнуть
6. Отправьте новое сообщение - история должна начаться заново

### Тестирование RAG
```bash
# Проверьте, что векторная база инициализирована
curl http://localhost/api/health | jq '.vector_db_status'

# Проверьте количество сообщений в истории
curl http://localhost/api/health | jq '.history_count'
```

## 🐛 Устранение проблем

### Проблемы с запуском
```bash
# Остановить приложение
docker-compose down

# Очистить Docker кэш
docker system prune -a

# Пересобрать и запустить
docker-compose up --build
```

### Проблемы с портами
Если порт 80 занят:
1. Измените порт в `docker-compose.yml` (nginx service)
2. Пересоберите приложение
3. Используйте новый URL

### Проблемы с RAG
```bash
# Проверьте, что Ollama запущен
ollama list

# Проверьте OpenAI API ключ
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Проверьте логи backend
docker-compose logs backend
```

### Проблемы с базой данных
```bash
# Проверьте подключение к PostgreSQL
docker exec -it chat-postgres psql -U chatuser -d chatdb -c "SELECT COUNT(*) FROM messages;"

# Проверьте логи PostgreSQL
docker-compose logs postgres
```

## 📋 Команды Docker

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
docker-compose logs nginx
docker-compose logs cloudflared

# Остановка
docker-compose down

# Пересборка
docker-compose build --no-cache

# Получение публичного URL
./get_tunnel_url.sh
```

## 🔮 Текущие возможности

### Реализованные функции
- [x] RAG система с обработкой HIPAA документа
- [x] Постоянное хранение истории в PostgreSQL
- [x] Векторная база данных ChromaDB
- [x] Семантический поиск с Ollama эмбеддингами
- [x] Публичный доступ через Cloudflared
- [x] Проверка типов с mypy
- [x] Профессиональное логирование

### Планируемые улучшения
- [ ] Поддержка множественных документов
- [ ] Загрузка документов через интерфейс
- [ ] Экспорт истории чата
- [ ] Аутентификация пользователей
- [ ] Мониторинг и метрики

### Текущие ограничения
- Работает только с одним документом (HIPAA)
- Нет поддержки загрузки новых документов через UI
- Нет аутентификации пользователей

## 🗄️ Работа с базой данных

### Подключение через DBeaver
1. Создайте новое подключение PostgreSQL
2. **Host**: localhost
3. **Port**: 5432
4. **Database**: chatdb
5. **Username**: chatuser
6. **Password**: chatpass

### Прямые команды
```bash
# Подключение к базе
docker exec -it chat-postgres psql -U chatuser -d chatdb

# Просмотр сообщений
SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10;

# Подсчет сообщений
SELECT COUNT(*) FROM messages;

# Очистка истории
DELETE FROM messages;
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs`
2. Убедитесь, что порты свободны
3. Проверьте переменные окружения
4. Убедитесь, что Ollama запущен
5. Попробуйте пересобрать приложение
6. Создайте Issue в репозитории 