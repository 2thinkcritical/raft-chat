#!/bin/bash

echo "🔍 Ожидание запуска Cloudflared туннеля..."
echo "⏳ Это может занять 10-30 секунд..."

# Ждем запуска контейнера
sleep 5

# Проверяем статус контейнера
if ! docker ps | grep -q chat-cloudflared; then
    echo "❌ Контейнер cloudflared не запущен"
    exit 1
fi

echo "✅ Контейнер cloudflared запущен"
echo "🔍 Ищем URL в логах..."

# Ждем появления URL в логах (максимум 60 секунд)
for i in {1..60}; do
    URL=$(docker logs chat-cloudflared 2>&1 | grep -o 'https://[a-zA-Z0-9.-]*\.trycloudflare\.com' | tail -1)
    
    if [ ! -z "$URL" ]; then
        echo ""
        echo "🎉 Публичный URL найден!"
        echo "🌐 $URL"
        echo ""
        echo "📋 Скопируйте эту ссылку для доступа к приложению"
        echo "🔒 HTTPS включен автоматически"
        echo "🌍 Доступно из любой точки мира"
        exit 0
    fi
    
    echo -n "."
    sleep 1
done

echo ""
echo "❌ URL не найден в логах"
echo "🔍 Проверьте логи вручную:"
echo "   docker logs chat-cloudflared" 