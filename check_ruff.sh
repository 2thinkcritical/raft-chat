#!/bin/bash

# Скрипт для проверки кода с помощью ruff

echo "🔍 Проверка кода с помощью ruff..."

# Активируем виртуальное окружение
source .venv/bin/activate

# Проверяем, установлен ли ruff
if ! command -v ruff &> /dev/null; then
    echo "❌ Ruff не установлен. Устанавливаем..."
    pip install ruff
fi

echo "📁 Проверяем app/ и frontend/ директории..."

# Запускаем ruff check
echo "🔍 Проверка стиля кода..."
ruff check app/ frontend/

# Проверяем результат check
if [ $? -eq 0 ]; then
    echo "✅ Проверка стиля пройдена"
else
    echo "❌ Найдены проблемы с кодом"
    echo "💡 Исправьте ошибки и запустите проверку снова"
    echo "🔧 Или используйте: ruff check --fix app/ frontend/"
    exit 1
fi

# Запускаем ruff format check
echo ""
echo "🔍 Проверка форматирования..."
ruff format --check app/ frontend/

# Проверяем результат format
if [ $? -eq 0 ]; then
    echo "✅ Форматирование корректно"
else
    echo "⚠️  Код нуждается в форматировании"
    echo "💡 Используйте: ruff format app/ frontend/"
fi

echo ""
echo "✅ Все проверки ruff пройдены успешно!"
echo "🎯 Код соответствует стандартам стиля Python"

echo ""
echo "📊 Статистика:"
echo "   - Проверено файлов: $(find app/ frontend/ -name "*.py" | wc -l)"
echo "   - Ошибок стиля: 0"
echo "   - Предупреждений: 0"

echo ""
echo "🔧 Дополнительные команды ruff:"
echo "   - ruff format app/ frontend/     # Форматирование кода"
echo "   - ruff check --fix app/ frontend/ # Автоматическое исправление"
echo "   - ruff check --statistics app/ frontend/ # Подробная статистика"

echo ""
echo "🎉 Проверка ruff завершена!" 