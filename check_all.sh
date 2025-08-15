#!/bin/bash

# Комплексный скрипт для проверки качества кода

echo "🔍 Комплексная проверка качества кода..."
echo "========================================"

# Активируем виртуальное окружение
source venv/bin/activate

# Счетчики
TOTAL_FILES=$(find app/ frontend/ -name "*.py" | wc -l)
TYPE_ERRORS=0
STYLE_ERRORS=0
FORMAT_ERRORS=0

echo ""
echo "📋 1. Проверка типов (mypy)..."
echo "-------------------------------"
./check_types.sh
if [ $? -eq 0 ]; then
    echo "✅ Типы проверены успешно"
else
    TYPE_ERRORS=1
    echo "❌ Ошибки в типах"
fi

echo ""
echo "📋 2. Проверка стиля кода (ruff)..."
echo "-----------------------------------"
ruff check app/ frontend/
if [ $? -eq 0 ]; then
    echo "✅ Стиль кода корректен"
else
    STYLE_ERRORS=1
    echo "❌ Ошибки в стиле кода"
fi

echo ""
echo "📋 3. Проверка форматирования (ruff format)..."
echo "----------------------------------------------"
ruff format --check app/ frontend/
if [ $? -eq 0 ]; then
    echo "✅ Форматирование корректно"
else
    FORMAT_ERRORS=1
    echo "❌ Код нуждается в форматировании"
fi

echo ""
echo "📋 4. Проверка синтаксиса Python..."
echo "-----------------------------------"
python3 -m py_compile app/main.py app/database.py app/vector_store.py app/process_question.py app/callbacks.py frontend/gradio_app.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Синтаксис Python корректен"
else
    echo "❌ Ошибки синтаксиса Python"
    exit 1
fi

echo ""
echo "========================================"
echo "📊 ИТОГОВАЯ СТАТИСТИКА:"
echo "========================================"
echo "   📁 Проверено файлов: $TOTAL_FILES"
echo "   ✅ Ошибок типов: $TYPE_ERRORS"
echo "   ✅ Ошибок стиля: $STYLE_ERRORS"
echo "   ✅ Ошибок форматирования: $FORMAT_ERRORS"
echo "   ✅ Ошибок синтаксиса: 0"

echo ""
if [ $TYPE_ERRORS -eq 0 ] && [ $STYLE_ERRORS -eq 0 ] && [ $FORMAT_ERRORS -eq 0 ]; then
    echo "🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!"
    echo "🚀 Код готов к выкладке в GitHub"
    echo "🏆 Профессиональное качество кода"
else
    echo "⚠️  НАЙДЕНЫ ПРОБЛЕМЫ:"
    [ $TYPE_ERRORS -eq 1 ] && echo "   - Ошибки типов (mypy)"
    [ $STYLE_ERRORS -eq 1 ] && echo "   - Ошибки стиля (ruff)"
    [ $FORMAT_ERRORS -eq 1 ] && echo "   - Ошибки форматирования (ruff format)"
    echo ""
    echo "💡 Рекомендации по исправлению:"
    echo "   - ruff check --fix app/ frontend/     # Исправить стиль"
    echo "   - ruff format app/ frontend/          # Отформатировать код"
    exit 1
fi

echo ""
echo "🔧 Полезные команды:"
echo "   - ./check_types.sh      # Только проверка типов"
echo "   - ./check_ruff.sh       # Только проверка ruff"
echo "   - ruff format app/ frontend/     # Форматирование"
echo "   - ruff check --fix app/ frontend/ # Автоисправление" 