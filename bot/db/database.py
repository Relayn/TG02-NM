import aiosqlite
import logging
from bot.config import DB_PATH # Импортируем путь к БД из конфига

async def init_db():
    """Инициализирует базу данных и создает таблицу студентов, если она не существует."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Создаем таблицу students, если она еще не существует
            await db.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    grade TEXT
                )
            ''')
            await db.commit()
        logging.info(f"База данных инициализирована по пути: {DB_PATH}")
    except Exception as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}", exc_info=True)
        raise # Поднимаем исключение дальше, чтобы бот не запустился с нерабочей БД

async def add_student(name: str, age: int, grade: str):
    """Добавляет нового студента в базу данных."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Вставляем данные студента
            await db.execute(
                'INSERT INTO students (name, age, grade) VALUES (?, ?, ?)',
                (name, age, grade)
            )
            await db.commit()
        logging.info(f"Студент {name} (Возраст: {age}, Класс: {grade}) добавлен в базу данных.")
        return True # Возвращаем True в случае успеха
    except Exception as e:
        logging.error(f"Ошибка при добавлении студента {name}: {e}", exc_info=True)
        return False # Возвращаем False в случае ошибки