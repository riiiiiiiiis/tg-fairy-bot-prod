from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_answers_keyboard(answers: list, answered_ids: list) -> InlineKeyboardMarkup:
    buttons = []
    
    # Создаем словарь для быстрого поиска порядка ответа
    # Например: {answer_id_1: 1, answer_id_2: 2, ...}
    answered_order = {answer_id: index + 1 for index, answer_id in enumerate(answered_ids)}
    
    choice_emojis = ["1️⃣", "2️⃣", "3️⃣"]

    for answer in answers:
        answer_id = answer.get('answer_id')
        full_text = answer.get('answer_text', '')
        
        # Обрезаем текст для кнопки
        button_text = (full_text[:60] + '...') if len(full_text) > 60 else full_text

        # Проверяем, был ли этот ответ выбран
        if answer_id in answered_order:
            choice_number = answered_order[answer_id]
            # Добавляем соответствующий эмодзи
            emoji = choice_emojis[choice_number - 1]
            button_text = f"{emoji} {button_text}"
            
        buttons.append(
            [InlineKeyboardButton(text=button_text, callback_data=f"ans:{answer_id}")]
        )
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard