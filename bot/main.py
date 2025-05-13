import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage # <--- Импортируем MemoryStorage

from bot.config import BOT_TOKEN
from bot.handlers.user_handlers import user_router
from bot.db.database import init_db

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Бот запускается...")

    # --- Новое: Инициализация базы данных ---
    try:
        await init_db()
    except Exception as e:
        logger.critical(f"Критическая ошибка при инициализации БД: {e}. Бот не может стартовать.")
        return # Останавливаем запуск, если БД не инициализирована
    # ------------------------------------------

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher() # Пока без FSM Storage, добавим на след. шаге

    # --- Новое: Инициализация FSM Storage ---
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключение роутеров
    dp.include_router(user_router)

    # Удаление вебхука перед запуском
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск полинга
    try:
        logger.info("Начало полинга...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Выполнение программы прервано пользователем.")
    except Exception as e:
        logging.critical(f"Непредвиденная ошибка в main: {e}", exc_info=True)