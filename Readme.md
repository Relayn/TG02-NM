# Telegram Бот: Переводчик и Хранитель Фото
## О проекте

Этот проект представляет собой Telegram-бота, разработанного для демонстрации базовых возможностей работы с Telegram Bot API с использованием библиотеки `aiogram 3.x`. Бот умеет обрабатывать различные типы сообщений и взаимодействовать с пользователем. Проект основан на материалах "Урока TG02".

## Функционал

Бот реализует следующий функционал:

*   **Обработка команд:** Реализованы стандартные команды `/start` и `/help`.
*   **Сохранение фотографий:** Автоматически скачивает и сохраняет любую отправленную пользователем фотографию в локальную папку `bot/assets/img/`.
*   **Отправка голосовых сообщений:** По команде `/sendvoice` отправляет пользователю заранее подготовленное тестовое голосовое сообщение (`.ogg` файл).
*   **Перевод текста:** Любое текстовое сообщение, не являющееся командой, переводится на английский язык с помощью библиотеки `googletrans` и отправляется пользователю в ответ.

## Необходимые условия

Для запуска бота у вас должны быть установлены:

*   Python 3.8 или выше
*   pip (менеджер пакетов Python)
*   Активный аккаунт Telegram
*   Токен вашего Telegram-бота (получается через @BotFather)

## Установка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
    cd telegram_translator_bot
    ```

2.  **Создайте виртуальное окружение (рекомендуется):**
    ```bash
    python -m venv .venv
    ```

3.  **Активируйте виртуальное окружение:**

    *   **Для Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **Для macOS и Linux:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

## Настройка

### Obtain the Bot Token

If you do not have a token yet, create a new bot or retrieve the token of an existing one via [@BotFather](https://t.me/BotFather).

### Create a `.env` file

In the root directory of the project (next to `main.py` and `requirements.txt`), create a file named `.env`. You can copy the contents from `.env_example`.

### Add the Token to `.env`

Open the `.env` file and add the following line:

```env
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Replace `"YOUR_BOT_TOKEN"` with the token obtained from @BotFather. **Important: Do not add the `.env` file to Git.** It is already added to `.gitignore` in this project.

## Запуск бота

Убедитесь, что виртуальное окружение активно и вы находитесь в корневой директории проекта.

Запустите бота с помощью команды:

```bash
python -m bot.main
```
Бот начнет работу и будет ожидать входящих сообщений. Вы можете остановить бота, нажав Ctrl+C в терминале.
## Структура проекта

- `bot/`: Main folder containing the bot's code.
- `main.py`: Entry point, initializes the bot and the dispatcher.
- `config.py`: Reads the token and file paths.
- `handlers/user_handlers.py`: Handlers for user commands and messages.
- `assets/`: Folder for static files.
- `audio/`: For audio files (e.g., sample.ogg).
- `img/`: For saving user-uploaded photos.
- `.env`: File with environment variables (bot token).
- `.gitignore`: List of files and folders ignored by Git.
- `requirements.txt`: List of required Python libraries.

## Использование

Начните диалог с ботом в Telegram и используйте следующий функционал:

- Отправьте `/start` или `/help`, чтобы получить информацию о боте.
- Отправьте  `/sendvoice` чтобы получить тестовое голосовое сообщение.
- Отправьте любое текстовое сообщение (например, "Привет мир!", "Как дела?"), и бот ответит переводом на английский.
- Отправьте любое изображение, и бот сохранит его на сервере (в папке bot/assets/img/) и сообщит об этом.

