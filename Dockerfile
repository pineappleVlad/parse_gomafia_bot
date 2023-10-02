# Используем официальный образ Python
FROM python:3.8-slim-buster

# Устанавливаем виртуальное окружение
RUN python -m venv /venv

# Устанавливаем переменную среды для виртуального окружения
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Копируем файлы проекта в контейнер
WORKDIR /app
COPY . /app

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Указываем точку входа (как запускать бота)
CMD ["python", "bot.py"]
