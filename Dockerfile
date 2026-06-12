# Используем официальный slim-образ Python 3.14
FROM python:3.14-slim

# Переменные окружения для корректной работы Python в Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем uv, копируя бинарный файл из официального образа Astral
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Устанавливаем рабочую директорию
WORKDIR /app

# 1. Копируем только файлы зависимостей для использования кэша Docker
# Если pyproject.toml и uv.lock не меняются, этот шаг и следующий будут закэшированы
COPY pyproject.toml uv.lock ./

# Синхронизируем зависимости в замороженном режиме (строго по uv.lock)
# --no-install-project ускоряет сборку, не устанавливая сам проект на этом этапе
RUN uv sync --frozen --no-install-project

# 2. Копируем исходный код проекта
COPY main.py ./
COPY src/ ./src/

# Устанавливаем сам проект (если он описан как пакет в pyproject.toml)
# Это свяжет ваш код с виртуальным окруuv, созданным на предыдущем шаге
RUN uv sync --frozen

# Команда для запуска приложения
# uv run автоматически активирует окружение и запускает скрипт
CMD ["uv", "run", "main.py"]
