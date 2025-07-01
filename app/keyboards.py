
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_answers_keyboard(answers: list, answered_ids: list) -> InlineKeyboardMarkup:
    buttons = []
    shuffled_answers = random.sample(answers, len(answers))
    for answer in shuffled_answers:
        answer_id = answer['answer_id']
        text = answer['answer_text']
        if answer_id in answered_ids:
            text = f"✅ {text}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"ans:{answer_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
