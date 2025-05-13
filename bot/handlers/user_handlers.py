import os
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from bot.config import IMG_DIR, AUDIO_DIR
from googletrans import Translator
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.db.database import add_student

# Класс состояний для регистрации студента
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_grade = State()

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
@user_router.message(Command("register"))
async def cmd_register_start(message: Message, state: FSMContext):
    """
    Начинает процесс регистрации студента.
    Устанавливает первое состояние FSM (ожидание имени).
    """
    await state.clear() # На случай, если пользователь был в каком-то состоянии
    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer(
        "Начинаем регистрацию нового студента.\n"
        "Пожалуйста, введите имя студента.\n\n"
        "Для отмены регистрации в любой момент отправьте /cancel."
    )
    logging.info(f"Пользователь {message.from_user.id} начал регистрацию. Установлено состояние waiting_for_name.")

@user_router.message(Command("cancel"))
async def cmd_cancel_registration(message: Message, state: FSMContext):
    """
    Отменяет текущий процесс регистрации (или любой другой FSM процесс).
    """
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активной операции для отмены.")
        return

    logging.info(f"Пользователь {message.from_user.id} отменил операцию из состояния {current_state}.")
    await state.clear() # Очищает состояние и данные FSM
    await message.answer(
        "Действие отменено. Все введенные данные сброшены.\n"
        "Вы можете начать заново с помощью /register или использовать другие команды."
    )

@user_router.message(RegistrationStates.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext):
    """
    Обрабатывает введенное имя студента.
    Сохраняет имя в FSM, переключает состояние на waiting_for_age
    и запрашивает возраст.
    """
    if not message.text or message.text.startswith('/'):
        await message.answer(
            "Пожалуйста, введите корректное имя (не команду и не пустое сообщение).\n"
            "Попробуйте еще раз или отмените регистрацию командой /cancel."
        )
        return

    student_name = message.text.strip()
    await state.update_data(name=student_name) # Сохраняем имя в хранилище FSM

    await state.set_state(RegistrationStates.waiting_for_age) # Переключаем состояние
    await message.answer(
        f"Отлично, имя студента: {student_name}.\n"
        "Теперь, пожалуйста, введите возраст студента (только цифры)."
    )
    logging.info(f"Пользователь {message.from_user.id} ввел имя: {student_name}. Установлено состояние waiting_for_age.")

@user_router.message(RegistrationStates.waiting_for_age, F.text)
async def process_age(message: Message, state: FSMContext):
    """
    Обрабатывает введенный возраст студента.
    Проверяет, что возраст - это число.
    Сохраняет возраст в FSM, переключает состояние на waiting_for_grade
    и запрашивает класс.
    """
    if not message.text or not message.text.isdigit():
        await message.answer(
            "Возраст должен быть числом. Пожалуйста, введите корректный возраст.\n"
            "Например: 10\n\n"
            "Или отмените регистрацию командой /cancel."
        )
        return

    student_age = int(message.text)
    if not (5 <= student_age <= 100): # Примерная валидация диапазона возраста
         await message.answer(
            "Пожалуйста, введите реалистичный возраст (например, от 5 до 100 лет).\n"
            "Попробуйте еще раз или отмените регистрацию командой /cancel."
        )
         return

    await state.update_data(age=student_age) # Сохраняем возраст

    await state.set_state(RegistrationStates.waiting_for_grade) # Переключаем состояние
    await message.answer(
        f"Возраст студента: {student_age}.\n"
        "Теперь введите класс (например, '5А', '10Б', '11')."
    )
    logging.info(f"Пользователь {message.from_user.id} ввел возраст: {student_age}. Установлено состояние waiting_for_grade.")


@user_router.message(RegistrationStates.waiting_for_grade, F.text)
async def process_grade_and_finish(message: Message, state: FSMContext):
    """
    Обрабатывает введенный класс студента.
    Сохраняет класс, извлекает все данные из FSM, добавляет студента в БД
    и завершает процесс регистрации.
    """
    if not message.text or message.text.startswith('/'):
        await message.answer(
            "Пожалуйста, введите корректный класс (не команду и не пустое сообщение).\n"
            "Например: '7Б' или '11'\n\n"
            "Попробуйте еще раз или отмените регистрацию командой /cancel."
        )
        return

    student_grade = message.text.strip()
    # Сохраняем класс во временные данные FSM (хотя можно и сразу использовать)
    await state.update_data(grade=student_grade)

    # Извлекаем все данные из FSM
    user_data = await state.get_data()
    student_name = user_data.get('name')
    student_age = user_data.get('age')
    # student_grade уже есть

    if not all([student_name, student_age, student_grade]):
        logging.error(f"Не все данные были собраны для пользователя {message.from_user.id} в FSM: {user_data}")
        await message.answer(
            "Произошла ошибка: не все данные были собраны. "
            "Пожалуйста, начните регистрацию заново с /register."
        )
        await state.clear()  # Очищаем состояние в случае ошибки
        return

    # Добавляем студента в базу данных
    success = await add_student(name=student_name, age=student_age, grade=student_grade)

    if success:
        await message.answer(
            f"🎉 Студент успешно зарегистрирован!\n"
            f"Имя: {student_name}\n"
            f"Возраст: {student_age}\n"
            f"Класс: {student_grade}\n\n"
            "Спасибо!"
        )
        logging.info(
            f"Пользователь {message.from_user.id} успешно зарегистрировал студента: "
            f"Имя={student_name}, Возраст={student_age}, Класс={student_grade}"
        )
    else:
        await message.answer(
            "Произошла ошибка при сохранении данных в базу. "
            "Пожалуйста, попробуйте позже или свяжитесь с администратором."
        )
        logging.error(
            f"Ошибка БД при регистрации студента от пользователя {message.from_user.id}: "
            f"Имя={student_name}, Возраст={student_age}, Класс={student_grade}"
        )

    await state.clear()  # Очищаем состояние FSM после завершения или ошибки

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