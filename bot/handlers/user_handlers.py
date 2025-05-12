import os
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from bot.config import IMG_DIR, AUDIO_DIR
from googletrans import Translator

# Инициализация переводчика
translator = Translator()
# Создаем роутер для пользовательских команд
user_router = Router()


@user_router.message(CommandStart())
async def handle_start(message: Message):
    """
    Обработчик команды /start
    """
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Я твой бот-помощник. Вот что я умею:\n"
        f"/help - показать это сообщение\n"
        f"\nОтправь мне фото, и я его сохраню."
        f"\nОтправь мне любой текст, и я переведу его на английский."
        f"\nИспользуй команду /sendvoice для получения тестового голосового сообщения."
    )


@user_router.message(Command('help'))
async def handle_help(message: Message):
    """
    Обработчик команды /help
    """
    await message.answer(
        "Это бот для демонстрации различных функций Telegram:\n"
        "- Сохранение отправленных фотографий в папку 'img'.\n"
        "- Отправка тестового голосового сообщения по команде /sendvoice.\n"
        "- Перевод любого текстового сообщения на английский язык.\n"
        "\nКоманды:\n"
        "/start - начало работы\n"
        "/help - это сообщение\n"
        "/sendvoice - отправить тестовое голосовое сообщение"
    )


@user_router.message(F.photo)
async def handle_photo(message: Message):  # <--- Ваша функция
    """
    Обработчик для сохранения полученных фотографий.
    """
    # В message.photo это список объектов PhotoSize, берем последний (самый большой)
    photo = message.photo[-1]

    # Формируем уникальное имя файла на основе file_id и сохраняем в папку IMG_DIR
    file_name = f"{photo.file_id}.jpg"
    save_path = os.path.join(IMG_DIR, file_name)

    try:
        # Скачиваем файл
        await message.bot.download(file=photo, destination=save_path)
        await message.answer(f"Фото сохранено как {file_name}!")
        logging.info(f"Фото {file_name} успешно сохранено по пути: {save_path}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении фото {photo.file_id}: {e}")
        await message.answer("Произошла ошибка при сохранении фото. Попробуйте пожалуйста позже.")


@user_router.message(Command('sendvoice'))
async def handle_send_voice(message: Message):
    """
    Обработчик команды /sendvoice для отправки тестового голосового сообщения.
    """
    voice_file_path = os.path.join(AUDIO_DIR, "sample.ogg")

    if not os.path.exists(voice_file_path):
        logging.error(f"Аудиофайл {voice_file_path} не найден.")
        await message.answer("Не удалось найти аудиофайл для отправки. Пожалуйста, сообщите администратору.")
        return

    try:
        # Создаем объект FSInputFile для отправки файла
        voice_to_send = FSInputFile(path=voice_file_path, filename="sample.ogg")

        # Отправляем голосовое сообщение
        await message.answer_voice(voice=voice_to_send)
        logging.info(f"Голосовое сообщение {voice_file_path} отправлено пользователю {message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке голосового сообщения: {e}")
        await message.answer("Произошла ошибка при отправке голосового сообщения.")


@user_router.message(F.text)  # Этот фильтр ловит любые текстовые сообщения
async def handle_text_translate(message: Message):
    """
    Обработчик для перевода любого полученного текста на английский язык.
    Сработает, если сообщение содержит текст и не было обработано
    более специфичными фильтрами команд.
    """
    if message.text and message.text.startswith('/'):  # Пропускаем команды, если вдруг не отфильтровались
        # В aiogram 3.x, фильтры команд обычно имеют приоритет,
        # но на всякий случай можно добавить эту проверку,
        # или убедиться, что Command-фильтры стоят выше и обработают команды первыми.
        # Для нашей текущей структуры с Router и явным Command(...) это не строго обязательно,
        # но не повредит.
        # Альтернативно, можно было бы этот обработчик регистрировать последним
        # в цепочке router.message, но с @декораторами порядок определения важен.
        # В идеале, такой хэндлер лучше ставить после всех командных.
        logging.debug(f"Пропуск команды {message.text} для перевода.")
        return

    original_text = message.text
    if not original_text:  # На случай пустого сообщения, хотя F.text этого не допустит
        return

    try:
        # Переводим текст
        # Библиотека googletrans сама определит исходный язык
        translation = translator.translate(original_text, dest='en')
        translated_text = translation.text

        await message.answer(f"<b>Перевод на английский:</b>\n{translated_text}")
        logging.info(f"Текст '{original_text}' переведен на английский для пользователя {message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка при переводе текста '{original_text}': {e}")
        await message.answer("Не удалось перевести текст. Попробуйте еще раз или измените текст.")