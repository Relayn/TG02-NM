import os
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
    # ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.config import IMG_DIR, AUDIO_DIR
from bot.db.database import add_student
from googletrans import Translator


# Класс состояний для регистрации студента
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_grade = State()


# Инициализация переводчика
translator = Translator()

# Создаем роутер для пользовательских команд
user_router = Router()


# --- Обработчики команд ---
@user_router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start. Показывает приветственное сообщение и меню с кнопками.
    Также очищает состояние FSM, если оно было установлено.
    """
    await state.clear()  # Очищаем состояние, если пользователь был в процессе, например, регистрации

    # Создаем клавиатуру с кнопками "Привет" и "Пока"
    greet_button = KeyboardButton(text="Привет 👋")
    bye_button = KeyboardButton(text="Пока Bye")

    start_keyboard = ReplyKeyboardMarkup(
        keyboard=[[greet_button, bye_button]],
        resize_keyboard=True,
        input_field_placeholder="Нажмите 'Привет' или 'Пока'..."
    )

    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Я твой бот-помощник. Выбери действие из меню ниже или используй команды:\n"
        f"/help - показать справку\n"
        f"/register - зарегистрировать студента\n"
        f"/links - показать полезные ссылки\n"  # Можно добавить сюда, если уже планируем
        f"/dynamic - динамическая клавиатура",  # Можно добавить сюда, если уже планируем
        reply_markup=start_keyboard
    )
    logging.info(f"Пользователь {message.from_user.id} запустил /start. Показано меню. Состояние FSM очищено.")


@user_router.message(Command('help'))
async def handle_help(message: Message):
    """
    Обработчик команды /help
    """
    # Можно обновить текст справки, чтобы включить новые команды и кнопки
    help_text = (
        "Это бот для демонстрации различных функций Telegram:\n"
        "- Используйте кнопки 'Привет 👋' и 'Пока Bye' для простого общения.\n"
        "- Отправьте `/register` для регистрации нового студента.\n"
        "- Отправьте `/cancel` для отмены текущей операции (например, регистрации).\n"
        "- Отправьте `/links` для получения набора полезных ссылок.\n"
        "- Отправьте `/dynamic` для работы с динамически изменяемой клавиатурой.\n"
        "- Отправьте фото, и я его сохраню в папку 'img'.\n"
        "- Отправьте `/sendvoice` для получения тестового голосового сообщения.\n"
        "- Отправьте любой другой текст, и я переведу его на английский язык.\n"
        "\nОсновные команды:\n"
        "/start - начало работы, показать меню\n"
        "/help - это сообщение"
    )
    await message.answer(help_text)


# --- Обработчики команд FSM ---
@user_router.message(Command("register"))
async def cmd_register_start(message: Message, state: FSMContext):
    """
    Начинает процесс регистрации студента.
    Устанавливает первое состояние FSM (ожидание имени).
    """
    await state.clear()
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
    await state.clear()
    await message.answer(
        "Действие отменено. Все введенные данные сброшены.\n"
        "Вы можете начать заново с помощью /register или использовать другие команды."
    )

@user_router.message(Command("links"))
async def cmd_links(message: Message):
    """
    Обработчик команды /links. Отправляет инлайн-кнопки с URL-ссылками.
    """
    # Создаем инлайн-кнопки
    news_button = InlineKeyboardButton(
        text="📰 Новости",
        url="https://www.youtube.com/watch?v=IlOXIhixkG8" # Замените на реальную ссылку
    )
    music_button = InlineKeyboardButton(
        text="🎵 Музыка",
        url="https://www.youtube.com/watch?v=ak-uvw-mQJA&list=RDak-uvw-mQJA&start_radio=1&ab_channel=PowerplantBand" # Замените на реальную ссылку
    )
    video_button = InlineKeyboardButton(
        text="🎬 Видео",
        url="https://www.youtube.com/watch?v=FlsrEP77jSI" # Замените на реальную ссылку
    )

    # Собираем инлайн-клавиатуру
    # Можно разместить кнопки в один ряд или каждую в своем ряду
    # [[button1, button2]] - две кнопки в одном ряду
    # [[button1], [button2]] - каждая кнопка в новом ряду
    links_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [news_button],
            [music_button],
            [video_button]
        ]
    )
    # Или так, для кнопок в один ряд, если их немного и они короткие:
    # links_keyboard = InlineKeyboardMarkup(
    #     inline_keyboard=[[news_button, music_button, video_button]]
    # )


    await message.answer(
        "Вот несколько полезных ссылок:",
        reply_markup=links_keyboard
    )
    logging.info(f"Пользователь {message.from_user.id} запросил ссылки (/links).")

# --- Обработчики кнопок ReplyKeyboard (должны быть до FSM состояний и общего F.text) ---
@user_router.message(F.text == "Привет 👋")
async def handle_hello_button(message: Message):
    """
    Обработчик для кнопки 'Привет 👋'.
    """
    user_name = message.from_user.first_name
    await message.answer(f"Привет, {user_name}!")
    logging.info(f"Пользователь {message.from_user.id} нажал кнопку 'Привет 👋'.")

@user_router.message(F.text == "Пока Bye")
async def handle_bye_button(message: Message):
    """
    Обработчик для кнопки 'Пока Bye'.
    """
    user_name = message.from_user.first_name
    await message.answer(f"До свидания, {user_name}!")
    # Для удаления клавиатуры:
    # from aiogram.types import ReplyKeyboardRemove
    # await message.answer(f"До свидания, {user_name}!", reply_markup=ReplyKeyboardRemove())
    logging.info(f"Пользователь {message.from_user.id} нажал кнопку 'Пока Bye'.")

@user_router.message(Command("dynamic"))
async def cmd_dynamic(message: Message):
    """
    Обработчик команды /dynamic. Отправляет начальную инлайн-кнопку.
    """
    show_more_button = InlineKeyboardButton(
        text="Показать больше",
        callback_data="show_more_options" # Уникальный callback_data
    )
    dynamic_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[show_more_button]]
    )
    await message.answer(
        "Нажмите кнопку ниже, чтобы увидеть больше опций:",
        reply_markup=dynamic_keyboard
    )
    logging.info(f"Пользователь {message.from_user.id} запросил динамическую клавиатуру (/dynamic).")

@user_router.callback_query(F.data == "show_more_options")
async def cq_show_more_options(callback_query: CallbackQuery):
    """
    Обрабатывает нажатие на инлайн-кнопку 'Показать больше'.
    Заменяет клавиатуру на две новые опции.
    """
    option1_button = InlineKeyboardButton(
        text="Опция 1",
        callback_data="select_option_1"
    )
    option2_button = InlineKeyboardButton(
        text="Опция 2",
        callback_data="select_option_2"
    )
    options_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[option1_button, option2_button]]
    )

    # Изменяем существующее сообщение, прикрепив новую клавиатуру
    try:
        await callback_query.message.edit_text(
            "Выберите одну из опций:",
            reply_markup=options_keyboard
        )
        logging.info(f"Пользователь {callback_query.from_user.id} нажал 'Показать больше'. Клавиатура обновлена.")
    except Exception as e: # Может быть ошибка, если сообщение слишком старое для редактирования
        logging.error(f"Ошибка при редактировании сообщения для callback 'show_more_options': {e}")
        # Можно отправить новое сообщение, если редактирование не удалось
        await callback_query.message.answer("Не удалось обновить предыдущее меню. Пожалуйста, попробуйте /dynamic снова.")


    # Важно ответить на callback-запрос, чтобы убрать "часики" на кнопке
    await callback_query.answer()


@user_router.callback_query(F.data == "select_option_1")
async def cq_select_option_1(callback_query: CallbackQuery):
    """
    Обрабатывает нажатие на инлайн-кнопку 'Опция 1'.
    """
    user_name = callback_query.from_user.first_name
    response_text = f"{user_name}, вы выбрали Опцию 1!"

    # Можно просто отправить новое сообщение
    await callback_query.message.answer(response_text)

    logging.info(f"Пользователь {callback_query.from_user.id} выбрал Опцию 1.")
    await callback_query.answer(text="Вы выбрали Опцию 1!", show_alert=False)  # Можно показать короткое уведомление


@user_router.callback_query(F.data == "select_option_2")
async def cq_select_option_2(callback_query: CallbackQuery):
    """
    Обрабатывает нажатие на инлайн-кнопку 'Опция 2'.
    """
    user_name = callback_query.from_user.first_name
    response_text = f"{user_name}, вы выбрали Опцию 2!"
    await callback_query.message.answer(response_text)

    logging.info(f"Пользователь {callback_query.from_user.id} выбрал Опцию 2.")
    await callback_query.answer(text="Вы выбрали Опцию 2!", show_alert=False)

# --- Обработчики состояний FSM ---
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
    await state.update_data(name=student_name)

    await state.set_state(RegistrationStates.waiting_for_age)
    await message.answer(
        f"Отлично, имя студента: {student_name}.\n"
        "Теперь, пожалуйста, введите возраст студента (только цифры)."
    )
    logging.info(
        f"Пользователь {message.from_user.id} ввел имя: {student_name}. Установлено состояние waiting_for_age.")


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
    if not (5 <= student_age <= 100):
        await message.answer(
            "Пожалуйста, введите реалистичный возраст (например, от 5 до 100 лет).\n"
            "Попробуйте еще раз или отмените регистрацию командой /cancel."
        )
        return

    await state.update_data(age=student_age)

    await state.set_state(RegistrationStates.waiting_for_grade)
    await message.answer(
        f"Возраст студента: {student_age}.\n"
        "Теперь введите класс (например, '5А', '10Б', '11')."
    )
    logging.info(
        f"Пользователь {message.from_user.id} ввел возраст: {student_age}. Установлено состояние waiting_for_grade.")


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
    await state.update_data(grade=student_grade)

    user_data = await state.get_data()
    student_name = user_data.get('name')
    student_age = user_data.get('age')
    # student_grade уже есть в переменной student_grade

    if not all([student_name, student_age, student_grade]):
        logging.error(f"Не все данные были собраны для пользователя {message.from_user.id} в FSM: {user_data}")
        await message.answer(
            "Произошла ошибка: не все данные были собраны. "
            "Пожалуйста, начните регистрацию заново с /register."
        )
        await state.clear()
        return

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

    await state.clear()


# --- Общие обработчики (должны идти ПОСЛЕ специфичных команд и состояний FSM) ---
@user_router.message(F.photo)
async def handle_photo(message: Message):
    """
    Обработчик для сохранения полученных фотографий.
    """
    photo = message.photo[-1]
    file_name = f"{photo.file_id}.jpg"
    save_path = os.path.join(IMG_DIR, file_name)

    try:
        await message.bot.download(file=photo, destination=save_path)
        await message.answer(f"Фото сохранено как {file_name}!")
        logging.info(f"Фото {file_name} успешно сохранено по пути: {save_path}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении фото {photo.file_id}: {e}")
        await message.answer("Произошла ошибка при сохранении фото. Попробуйте пожалуйста позже.")


@user_router.message(Command('sendvoice'))  # Эту команду можно было бы и выше с другими командами
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
        voice_to_send = FSInputFile(path=voice_file_path, filename="sample.ogg")
        await message.answer_voice(voice=voice_to_send)
        logging.info(f"Голосовое сообщение {voice_file_path} отправлено пользователю {message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке голосового сообщения: {e}")
        await message.answer("Произошла ошибка при отправке голосового сообщения.")


# Универсальный текстовый обработчик (должен быть одним из последних для текстовых сообщений)
@user_router.message(F.text)
async def handle_text_translate(message: Message):
    """
    Обработчик для перевода любого полученного текста на английский язык.
    Сработает, если сообщение содержит текст и не было обработано
    более специфичными фильтрами (команды, кнопки, состояния FSM).
    """
    original_text = message.text
    if not original_text:
        return

    # Эта проверка на команды здесь избыточна, если Command-фильтры и фильтры FSM
    # зарегистрированы правильно и раньше этого обработчика.
    # if original_text.startswith('/'):
    #     # ... (код пропуска команд, если он был)
    #     return

    try:
        translation = translator.translate(original_text, dest='en')
        translated_text = translation.text

        await message.answer(f"<b>Перевод на английский:</b>\n{translated_text}")
        logging.info(
            f"Текст '{original_text}' ({translation.src}) переведен на английский: '{translated_text}' для пользователя {message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка при переводе текста '{original_text}': {e}")
        await message.answer("К сожалению, не удалось перевести текст. Попробуйте еще раз или измените ваш запрос.")