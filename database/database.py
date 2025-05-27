import sqlite3
import os
import logging
from contextlib import contextmanager


logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       'weather_history.db')


@contextmanager
def get_db_connection():
    """Контекстный менеджер для подключений к БД"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Ошибка базы данных: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """Инициализация базы данных"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                user_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                latitude REAL,
                longitude REAL
            )
            ''')

            # Добавление популярных городов для автозаполнения
            cities = [
                ("Москва", 55.7558, 37.6173),
                ("Санкт-Петербург", 59.9343, 30.3351),
                ("Новосибирск", 55.0084, 82.9357),
                ("Екатеринбург", 56.8389, 60.6057),
                ("Казань", 55.7887, 49.1221),
            ]

            cursor.executemany(
                "INSERT OR IGNORE INTO cities (name, latitude, longitude) VALUES (?, ?, ?)",
                cities
            )
            logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
        raise


def save_search(city, latitude, longitude, user_id):
    """Сохранение информации о поиске"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO searches (city, latitude, longitude, user_id) VALUES (?, ?, ?, ?)",
                (city, latitude, longitude, user_id)
            )
            cursor.execute(
                "INSERT OR IGNORE INTO cities (name, latitude, longitude) VALUES (?, ?, ?)",
                (city, latitude, longitude)
            )
    except Exception as e:
        logger.error(f"Ошибка при сохранении поиска: {e}")
        raise


def get_user_history(user_id):
    """Получение истории поисков пользователя"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT city, timestamp
                FROM searches
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 20
            """, (user_id,))
            return [{'city': row['city'], 'time': row['timestamp']} for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Ошибка при получении истории пользователя: {e}")
        return []


def get_cities_autocomplete(q):
    """Получение списка городов для автозаполнения"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM cities WHERE name LIKE ? ORDER BY name LIMIT 10",
                (f"%{q}%",)
            )
            return [row['name'] for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Ошибка при получении списка городов: {e}")
        return []


def get_cities_stats():
    """Получение статистики популярности городов"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT city, COUNT(*) as count
                FROM searches
                GROUP BY city
                ORDER BY count DESC
                LIMIT 20
            """)
            return [{'city': row['city'], 'count': row['count']} for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return []
