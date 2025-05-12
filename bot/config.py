import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if BOT_TOKEN is None:
    raise ValueError("Необходимо установить TELEGRAM_BOT_TOKEN в .env файле")

# Папки для ассетов
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(os.path.dirname(BASE_DIR), 'assets', 'img') # telegram_translator_bot/assets/img
AUDIO_DIR = os.path.join(os.path.dirname(BASE_DIR), 'assets', 'audio') # telegram_translator_bot/assets/audio

# Убедимся, что директории существуют
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)