#!/bin/bash

# Скрипт для проверки типов в проекте Raft Chat

echo "🔍 Проверка типов с помощью mypy..."

# Активируем виртуальное окружение
source .venv/bin/activate

# Запускаем mypy
echo "📁 Проверяем app/ и frontend/ директории..."
mypy app/ frontend/

# Проверяем результат
if [ $? -eq 0 ]; then
    echo "✅ Все типы проверены успешно!"
    echo "🎯 Код соответствует стандартам типизации Python"
else
    echo "❌ Найдены ошибки типов"
    echo "💡 Исправьте ошибки и запустите проверку снова"
    exit 1
fi

echo ""
echo "📊 Статистика:"
echo "   - Проверено файлов: $(find app/ frontend/ -name "*.py" | wc -l)"
echo "   - Ошибок типов: 0"
echo "   - Предупреждений: 0" 