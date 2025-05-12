import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN
from bot.handlers.user_handlers import user_router

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Бот запускается...")

    # Инициализация бота и диспетчера
    # parse_mode=ParseMode.HTML дает возможность использовать HTML-теги в сообщениях
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Подключение роутеров
    dp.include_router(user_router)
    # Можно будет добавить и другие роутеры, если понадобится

    # Удаление вебхука перед запуском, если он был установлен
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск полинга
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Выполнение программы прервано пользователем.")