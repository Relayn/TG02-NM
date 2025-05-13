import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if BOT_TOKEN is None:
    raise ValueError("Необходимо установить TELEGRAM_BOT_TOKEN в .env файле")

# Базовая директория проекта (telegram_translator_bot)
PROJECT_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Папки для ассетов
ASSETS_DIR = os.path.join(PROJECT_BASE_DIR, 'bot', 'assets')
IMG_DIR = os.path.join(ASSETS_DIR, 'img')
AUDIO_DIR = os.path.join(ASSETS_DIR, 'audio')

# --- Новое: Настройки базы данных ---
DB_DIR = os.path.join(PROJECT_BASE_DIR, 'bot', 'db') # Папка для БД
DB_NAME = 'school_data.db'                          # Имя файла БД
DB_PATH = os.path.join(DB_DIR, DB_NAME)             # Полный путь к БД
# ------------------------------------

# Убедимся, что директории существуют
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True) # Создаем папку для БД