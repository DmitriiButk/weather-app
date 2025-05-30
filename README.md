# Weather App

## О проекте:

Weather App - это веб-приложение для получения информации о текущей погоде и прогнозе для различных городов. Приложение
написано на Python с использованием FastAPI, с HTML и CSS для пользовательского интерфейса. Данные о погоде получаются
через API сервиса [Open-Meteo](https://open-meteo.com/).

## Стек технологий:

- Python 3.11
- FastAPI
- SQLite (база данных)
- sqlite3 (стандартный модуль Python)
- Jinja2 (шаблонизатор)
- Docker/Docker Compose

## Функциональность:

- Получение данных о текущей погоде по названию города
- Отображение прогноза погоды на ближайшие часы
- Автодополнение при вводе названий городов
- Статистика запрошенных городов
- Адаптивный пользовательский интерфейс

## Запуск с помощью Docker:

Убедитесь, что у вас установлены Docker и Docker Compose:

```bash
docker --version
docker-compose --version
```

Клонируйте репозиторий и перейдите в директорию проекта:

```bash
git clone https://github.com/DmitriiButk/weather-app.git
cd weather-app
```

Соберите и запустите контейнер:

```bash
docker-compose up --build
```

Остановка контейнеров:

```bash 
docker-compose down
```

**Доступ к приложению**

После запуска приложение будет доступно по адресу [http://localhost:8000](http://localhost:8000)

## Запуск тестов:

#### Локальный запуск тестов:

```bash
# Активируйте виртуальное окружение
.venv\Scripts\activate  # Для Windows
source .venv/bin/activate  # Для Linux/Mac
```

#### Установите pytest, если его нет:

```bash
pip install pytest
```

#### Запуск всех тестов:

```bash
python -m pytest
```

#### Запуск с отображением подробного вывода:

```bash
python -m pytest -v
```

### Запуск тестов в Docker:
```bash
docker-compose run --rm app pytest
```

#### Запуск с подробным выводом:
```bash
docker-compose run --rm app pytest -v
```
