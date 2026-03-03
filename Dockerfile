# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ ./app/

# Копируем файл с переменными окружения
COPY .env .

# Создаем пользователя для запуска (без прав root)
RUN addgroup --system --gid 1001 bot && \
    adduser --system --uid 1001 --gid 1001 bot && \
    chown -R bot:bot /app

# Переключаемся на пользователя bot
USER bot

# Запускаем бота
CMD ["python", "-m", "app.main"]