from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def generate_answers_keyboard(answers: list, answered_ids: list) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру с кнопками-цифрами.
    :param answers: Полный список ответов для вопроса (для получения ID).
    :param answered_ids: Список ID ответов, которые уже выбраны.
    """
    builder = InlineKeyboardBuilder()
    
    # Создаем словарь для быстрого поиска ID по номеру и наоборот
    id_to_num_map = {answer.get('answer_id'): i + 1 for i, answer in enumerate(answers)}
    
    choice_emojis = ["1️⃣", "2️⃣", "3️⃣"]
    
    # Создаем словарь для быстрого поиска порядка ответа
    answered_order = {answer_id: index + 1 for index, answer_id in enumerate(answered_ids)}

    for i, answer in enumerate(answers):
        answer_id = answer.get('answer_id')
        num = i + 1
        text = f"{num}"

        # Проверяем, был ли этот ответ выбран
        if answer_id in answered_order:
            choice_number = answered_order[answer_id]
            # Добавляем соответствующий эмодзи
            emoji = choice_emojis[choice_number - 1]
            text = f"{emoji}"
        
        # В callback_data теперь передаем номер, а не ID
        builder.add(InlineKeyboardButton(text=text, callback_data=f"ans_num:{num}"))

    # Размещаем по 3 кнопки в ряд
    builder.adjust(3)
    return builder.as_markup()


def generate_gender_selection_keyboard() -> InlineKeyboardMarkup:
    """Генерирует клавиатуру для выбора пола"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужчина", callback_data="gender:male")],
        [InlineKeyboardButton(text="👩 Женщина", callback_data="gender:female")]
    ])


def generate_final_buttons_keyboard() -> InlineKeyboardMarkup:
    """Генерирует клавиатуру с финальными кнопками"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Присоединиться к закрытому каналу", url="https://t.me/tribute/app?startapp=sycj")],
        [InlineKeyboardButton(text="Узнать больше про нас", callback_data="about_us")]
    ])


def generate_about_us_keyboard() -> InlineKeyboardMarkup:
    """Генерирует клавиатуру для сообщения about_us"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ 🧚🏻 Присоединиться к закрытому каналу по ранней цене  — стать частью волшебного сообщества", url="https://t.me/tribute/app?startapp=sycj")],
        [InlineKeyboardButton(text="📖Скачать рабочую тетрадь magic book — твой персональный навигатор по созданию бренда", callback_data="workbook")],
        [InlineKeyboardButton(text="💬 Задать вопрос службе заботы", url="https://t.me/cooperative_skazka")]
    ])


def generate_workbook_keyboard() -> InlineKeyboardMarkup:
    """Генерирует клавиатуру для сообщения workbook с кнопкой скачивания и дополнительными действиями"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Скачать", url="https://drive.google.com/file/d/1Kemc-bGezHYzXMwzv342zr3cIR_YJfT4/view?usp=drivesdk")],
        [InlineKeyboardButton(text="✨ 🧚🏻 Присоединиться к закрытому каналу по ранней цене  — стать частью волшебного сообщества", url="https://t.me/tribute/app?startapp=sycj")],
        [InlineKeyboardButton(text="💬 Задать вопрос службе заботы", url="https://t.me/cooperative_skazka")]
    ])