import sqlite3
import telebot
from telebot import types

# Инициализация бота
bot = telebot.TeleBot("7422495691:AAFTjaeMeOB58gOT6pc1AtDHnXQ5_JZACHI")

# Состояния для бота
class States:
    START = "START"
    ADD_PROJECT_NAME = "ADD_PROJECT_NAME"
    ADD_PROJECT_DESCRIPTION = "ADD_PROJECT_DESCRIPTION"
    DELETE_PROJECT_NAME = "DELETE_PROJECT_NAME"
    UPDATE_PROJECT_NAME = "UPDATE_PROJECT_NAME"
    UPDATE_PROJECT_DESCRIPTION = "UPDATE_PROJECT_DESCRIPTION"
    FIND_PROJECT_NAME = "FIND_PROJECT_NAME"
    PROJECT_EXISTS_NAME = "PROJECT_EXISTS_NAME"

user_state = {}
project_data = {}

# Создание таблицы для хранения проектов, если она еще не существует
def create_table():
    try:
        with sqlite3.connect('portfolio.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                project_name TEXT,
                                project_description TEXT
                            )''')
            conn.commit()
            print("Таблица успешно создана или уже существует.")
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблицы: {e}")

create_table()

def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.KeyboardButton("/add_project"),
        types.KeyboardButton("/delete_project"),
        types.KeyboardButton("/update_project"),
        types.KeyboardButton("/list_projects"),
        types.KeyboardButton("/find_project"),
        types.KeyboardButton("/clear_projects"),
        types.KeyboardButton("/count_projects"),
        types.KeyboardButton("/project_exists"),
        types.KeyboardButton("/help")
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    """
    Приветственное сообщение.
    Пример использования: /start
    """
    bot.send_message(message.chat.id, "Добро пожаловать! Используйте клавиатуру для выбора команды.", reply_markup=create_main_keyboard())
    user_state[message.from_user.id] = States.START

@bot.message_handler(commands=['help'])
def help_command(message):
    """
    Команда для получения списка доступных команд.
    Пример использования: /help
    """
    help_text = (
        "/add_project - Добавить новый проект\n"
        "/delete_project - Удалить проект\n"
        "/update_project - Обновить описание проекта\n"
        "/list_projects - Список всех проектов\n"
        "/find_project - Найти проект по названию\n"
        "/clear_projects - Удалить все проекты\n"
        "/count_projects - Получить количество проектов\n"
        "/project_exists - Проверить, существует ли проект\n"
        "/help - Показать список доступных команд"
    )
    bot.send_message(message.chat.id, help_text, reply_markup=create_main_keyboard())

@bot.message_handler(commands=['add_project'])
def add_project_command(message):
    """
    Начинает процесс добавления проекта.
    Пример использования: /add_project
    """
    user_state[message.from_user.id] = States.ADD_PROJECT_NAME
    bot.send_message(message.chat.id, "Пожалуйста, введите название проекта:")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == States.ADD_PROJECT_NAME)
def add_project_name(message):
    """
    Обрабатывает ввод названия проекта.
    """
    project_data[message.from_user.id] = {'project_name': message.text}
    user_state[message.from_user.id] = States.ADD_PROJECT_DESCRIPTION
    bot.send_message(message.chat.id, "Пожалуйста, введите описание проекта:")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == States.ADD_PROJECT_DESCRIPTION)
def add_project_description(message):
    """
    Обрабатывает ввод описания проекта и сохраняет проект в базу данных.
    """
    user_id = message.from_user.id
    project_data[user_id]['project_description'] = message.text

    try:
        with sqlite3.connect('portfolio.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO projects (user_id, project_name, project_description)
                              VALUES (?, ?, ?)''', (user_id, project_data[user_id]['project_name'], project_data[user_id]['project_description']))
            conn.commit()
            print("Проект успешно добавлен в базу данных.")
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении проекта: {e}")

    bot.send_message(message.chat.id, "Проект успешно добавлен!", reply_markup=create_main_keyboard())
    user_state[user_id] = States.START

@bot.message_handler(commands=['delete_project'])
def delete_project_command(message):
    """
    Начинает процесс удаления проекта.
    Пример использования: /delete_project
    """
    user_state[message.from_user.id] = States.DELETE_PROJECT_NAME
    bot.send_message(message.chat.id, "Пожалуйста, введите название проекта для удаления:")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == States.DELETE_PROJECT_NAME)
def delete_project(message):
    """
    Обрабатывает ввод названия проекта для удаления.
    """
    user_id = message.from_user.id
    project_name = message.text

    try:
        with sqlite3.connect('portfolio.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM projects WHERE user_id=? AND project_name=?''', (user_id, project_name))
            conn.commit()

            if cursor.rowcount == 0:
                bot.reply_to(message, "Проект не найден", reply_markup=create_main_keyboard())
            else:
                bot.reply_to(message, "Проект успешно удален!", reply_markup=create_main_keyboard())
    except sqlite3.Error as e:
        print(f"Ошибка при удалении проекта: {e}")

    user_state[user_id] = States.START

@bot.message_handler(commands=['update_project'])
def update_project_command(message):
    """
    Начинает процесс обновления проекта.
    Пример использования: /update_project
    """
    user_state[message.from_user.id] = States.UPDATE_PROJECT_NAME
    bot.send_message(message.chat.id, "Пожалуйста, введите название проекта для обновления:")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == States.UPDATE_PROJECT_NAME)
def update_project_name(message):
    """
    Обрабатывает ввод названия проекта для обновления.
    """
    project_data[message.from_user.id] = {'project_name': message.text}
    user_state[message.from_user.id] = States.UPDATE_PROJECT_DESCRIPTION
    bot.send_message(message.chat.id, "Пожалуйста, введите новое описание проекта:")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == States.UPDATE_PROJECT_DESCRIPTION)
def update_project_description(message):
    """
    Обрабатывает ввод нового описания проекта и обновляет его в базе данных.
    """
    user_id = message.from_user.id
    project_data[user_id]['project_description'] = message.text

    try:
        with sqlite3.connect('portfolio.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''UPDATE projects SET project_description=? WHERE user_id=? AND project_name=?''',
                           (project_data[user_id]['project_description'], user_id, project_data[user_id]['project_name']))
            conn.commit()

            if cursor.rowcount == 0:
                bot.reply_to(message, "Проект не найден", reply_markup=create_main_keyboard())
            else:
                bot.reply_to(message, "Проект успешно обновлен!", reply_markup=create_main_keyboard())
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении проекта: {e}")

    user_state[user_id] = States.START

@bot.message_handler(commands=['list_projects'])
def list_projects(message):
    """
    Команда для получения списка всех проектов пользователя.
    Пример использования: /list_projects
    """
    user_id = message.from_user.id

    try:
        with sqlite3.connect('portfolio.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT project_name, project_description FROM projects WHERE user_id=?''', (user_id,))
            projects = cursor.fetchall()

        if not projects:
            bot.reply_to(message, "У вас нет проектов.", reply_markup=create_main_keyboard())
        else:
            response = "Ваши проекты:\n"
            for project in projects:
                response += f"Название: {project[0]}\nОписание: {project[1]}\n\n"
            bot.reply_to(message, response, reply_markup=create_main_keyboard())
    except sqlite3.Error as e:
        print(f"Ошибка при получении списка проектов: {e}")

@bot.message_handler(commands=['find_project'])
def find_project_command(message):
    """
    Начинает процесс поиска проекта.
    Пример использования: /find_project
    """
    user_state[message.from_user.id] = States.FIND_PROJECT_NAME
    bot.send_message(message.chat.id, "Пожалуйста, введите название проекта для поиска:")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == States.FIND_PROJECT_NAME)
def find_project(message):
    """
    Обрабатывает ввод названия проекта для поиска.
    """
    user_id = message.from_user.id
    project_name = message.text

    try:
        with sqlite3.connect('portfolio.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT project_description FROM projects WHERE user_id=? AND project_name=?''',
                           (user_id, project_name))
            project = cursor.fetchone()

        if project is None:
            bot.reply_to(message, "Проект не найден", reply_markup=create_main_keyboard())
        else:
            bot.reply_to(message, f"Название: {project_name}\nОписание: {project[0]}", reply_markup=create_main_keyboard())
    except sqlite3.Error as e:
        print(f"Ошибка при поиске проекта: {e}")

    user_state[user_id] = States.START

@bot.message_handler(commands=['clear_projects'])
def clear_projects(message):
    """
    Команда для удаления всех проектов пользователя.
    Пример использования: /clear_projects
    """
    user_id = message.from_user.id

    try:
        with sqlite3.connect('portfolio.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM projects WHERE user_id=?''', (user_id,))
            conn.commit()
        bot.reply_to(message, "Все ваши проекты успешно удалены!", reply_markup=create_main_keyboard())
    except sqlite3.Error as e:
        print(f"Ошибка при удалении всех проектов: {e}")

@bot.message_handler(commands=['count_projects'])
def count_projects(message):
    """
    Команда для получения количества проектов пользователя.
    Пример использования: /count_projects
    """
    user_id = message.from_user.id

    try:
        with sqlite3.connect('portfolio.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(*) FROM projects WHERE user_id=?''', (user_id,))
            count = cursor.fetchone()[0]
        bot.reply_to(message, f"У вас {count} проектов.", reply_markup=create_main_keyboard())
    except sqlite3.Error as e:
        print(f"Ошибка при подсчете проектов: {e}")

@bot.message_handler(commands=['project_exists'])
def project_exists_command(message):
    """
    Начинает процесс проверки существования проекта.
    Пример использования: /project_exists
    """
    user_state[message.from_user.id] = States.PROJECT_EXISTS_NAME
    bot.send_message(message.chat.id, "Пожалуйста, введите название проекта для проверки:")

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == States.PROJECT_EXISTS_NAME)
def project_exists(message):
    """
    Обрабатывает ввод названия проекта для проверки существования.
    """
    user_id = message.from_user.id
    project_name = message.text

    try:
        with sqlite3.connect('portfolio.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT 1 FROM projects WHERE user_id=? AND project_name=?''', (user_id, project_name))
            exists = cursor.fetchone() is not None

        if exists:
            bot.reply_to(message, "Проект существует.", reply_markup=create_main_keyboard())
        else:
            bot.reply_to(message, "Проект не найден.", reply_markup=create_main_keyboard())
    except sqlite3.Error as e:
        print(f"Ошибка при проверке существования проекта: {e}")

    user_state[user_id] = States.START

# Запуск бота
bot.polling()
