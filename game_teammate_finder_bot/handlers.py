from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import save_user_data, get_teammates, get_teammate_by_id

# Стан користувача в чаті
PLATFORM, GAME, LANGUAGE, SKILL_LEVEL = range(4)


def start(update: Update, context: CallbackContext):
    """Початок взаємодії з користувачем, пропонуємо вибрати платформу."""
    update.message.reply_text("Ласкаво просимо! Виберіть свою платформу: ПК, Консоль або Мобільний.")
    return PLATFORM


def platform(update: Update, context: CallbackContext):
    """Обробляємо вибір платформи користувача."""
    user_platform = update.message.text
    context.user_data['platform'] = user_platform
    update.message.reply_text("Виберіть гру, в яку ви хочете грати.")
    return GAME


def game(update: Update, context: CallbackContext):
    """Обробляємо вибір гри користувача."""
    user_game = update.message.text
    context.user_data['game'] = user_game
    update.message.reply_text("Виберіть мову для спілкування.")
    return LANGUAGE


def language(update: Update, context: CallbackContext):
    """Обробляємо вибір мови користувача."""
    user_language = update.message.text
    context.user_data['language'] = user_language
    update.message.reply_text("Вкажіть ваш рівень навичок від 1 до 10.")
    return SKILL_LEVEL


def skill_level(update: Update, context: CallbackContext):
    """Обробляємо рівень навичок користувача та зберігаємо дані."""
    try:
        user_skill_level = int(update.message.text)
        if not (1 <= user_skill_level <= 10):
            raise ValueError
    except ValueError:
        update.message.reply_text("Будь ласка, введіть число від 1 до 10.")
        return SKILL_LEVEL

    context.user_data['skill_level'] = user_skill_level

    # Збереження даних користувача в базі даних
    save_user_data(context.user_data)

    update.message.reply_text("Ваш профіль збережено! Ви можете шукати товаришів по команді за допомогою /find_teammates.")
    return ConversationHandler.END


def find_teammates_command(update: Update, context: CallbackContext):
    """Обробляємо команду для пошуку товаришів по команді."""
    user_data = context.user_data

    if not user_data:
        update.message.reply_text("Спочатку створіть профіль, використовуючи /start.")
        return

    platform = user_data.get('platform')
    game = user_data.get('game')
    language = user_data.get('language')
    skill_level = user_data.get('skill_level')

    # Отримуємо товаришів по команді з бази даних
    teammates = get_teammates(platform, game, language, skill_level)

    if not teammates:
        update.message.reply_text("Не знайдено товаришів по команді з вашими критеріями.")
        return

    buttons = []
    for teammate in teammates:
        buttons.append([
            InlineKeyboardButton(teammate['username'], callback_data=str(teammate['id']))
        ])

    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text("Ось потенційні товариші по команді:", reply_markup=reply_markup)


def button_callback(update: Update, context: CallbackContext):
    """Обробляємо вибір товариша по команді за допомогою кнопок."""
    query = update.callback_query
    query.answer()

    # Отримуємо ID вибраного товариша та надсилаємо деталі
    teammate_id = query.data
    teammate_info = get_teammate_by_id(teammate_id)

    if teammate_info:
        query.edit_message_text(
            f"Ім'я користувача: {teammate_info['username']}\n"
            f"Платформа: {teammate_info['platform']}\n"
            f"Гра: {teammate_info['game']}\n"
            f"Мова: {teammate_info['language']}\n"
            f"Рівень навичок: {teammate_info['skill_level']}\n"
            f"Контакт: @{teammate_info['username']}"
        )
    else:
        query.edit_message_text("Користувача не знайдено.")
