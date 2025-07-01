# app/handlers.py (ПОЛНАЯ НОВАЯ ВЕРСИЯ)

import asyncio
import logging
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart

from app.gsheets import GoogleSheetsDB
from app.keyboards import generate_answers_keyboard

# --- Инициализация ---
router = Router()

# Здесь нужно указать твой ключ таблицы
# ВАЖНО: убедись, что файл google_credentials.json лежит в корне проекта
try:
    google_sheets_db = GoogleSheetsDB(
        credentials_path='google_credentials.json',
        spreadsheet_key='1VRFG-gQmBVRVF_J1CAiQt7fU6rj8yI3BZgUKzMxU-t8' # <-- УБЕДИСЬ, ЧТО ЭТО ТВОЙ КЛЮЧ
    )
    # Предзагрузка данных для ускорения
    ALL_QUESTIONS = google_sheets_db.get_all_questions()
    ALL_ANSWERS = google_sheets_db.get_all_answers()
    ALL_ARCHETYPES_IDS = {ans['archetype_id'] for ans in ALL_ANSWERS}
    TOTAL_QUESTIONS = len(ALL_QUESTIONS)
except Exception as e:
    logging.error(f"Не удалось инициализировать Google-таблицу: {e}")
    google_sheets_db = None

class Quiz(StatesGroup):
    in_progress = State()

# --- ФУНКЦИЯ ОТПРАВКИ ВОПРОСА ---
async def send_question(chat_id: int, state: FSMContext, bot):
    user_data = await state.get_data()
    question_id = user_data.get('current_question_id', 1)

    question_data = next((q for q in ALL_QUESTIONS if q['question_id'] == question_id), None)
    answers = [ans for ans in ALL_ANSWERS if ans['question_id'] == question_id]

    if not question_data or not answers:
        await bot.send_message(chat_id, f"⚠️ Ошибка: не найден вопрос или ответы для ID={question_id}. Проверьте таблицу.")
        await state.clear()
        return

    full_question_text = f"**{question_data['question_text']}**\n\n_{question_data['prompt_text']}_"

    await bot.send_message(
        chat_id,
        full_question_text,
        reply_markup=generate_answers_keyboard(answers, []),
        parse_mode="Markdown"
    )

    await state.update_data(current_question_id=question_id, answered_in_question=[], click_count=0)
    await state.set_state(Quiz.in_progress)


# --- ОБРАБОТЧИКИ ---
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, bot):
    if not google_sheets_db:
        await message.answer("Бот временно не работает. Проблема с подключением к базе данных.")
        return

    await state.clear()

    welcome_message = google_sheets_db.get_config_value('welcome_message')
    initial_prompt = google_sheets_db.get_config_value('initial_prompt')
    fairy_intro = google_sheets_db.get_config_value('fairy_intro')
    hat_intro = google_sheets_db.get_config_value('hat_intro')

    await message.answer(f"{welcome_message}\n\n{initial_prompt}")
    await asyncio.sleep(0.8)
    await bot.send_chat_action(message.chat.id, 'typing')
    await asyncio.sleep(0.8)

    await message.answer(f"{fairy_intro}\n\n{hat_intro}")
    await asyncio.sleep(0.8)
    await bot.send_chat_action(message.chat.id, 'typing')
    await asyncio.sleep(0.8)

    initial_scores = {archetype: 0 for archetype in ALL_ARCHETYPES_IDS}
    await state.update_data(scores=initial_scores, current_question_id=1)

    await send_question(message.chat.id, state, bot)


@router.callback_query(F.data.startswith('ans:'), Quiz.in_progress)
async def callback_answer_handler(callback_query: CallbackQuery, state: FSMContext, bot):
    await callback_query.answer() # Сразу отвечаем, чтобы убрать часики на кнопке

    user_data = await state.get_data()
    click_count = user_data.get('click_count', 0)
    answered_in_question = user_data.get('answered_in_question', [])

    if click_count >= 3:
        return # Игнорируем нажатия, если уже выбрано 3

    answer_id = int(callback_query.data.split(':')[1])
    if answer_id in answered_in_question:
        return # Игнорируем повторное нажатие на ту же кнопку

    # --- Логика начисления очков ---
    click_count += 1
    answered_in_question.append(answer_id)
    
    points = 3 - (click_count - 1)
    current_question_id = user_data.get('current_question_id')
    
    selected_answer = next((ans for ans in ALL_ANSWERS if ans['answer_id'] == answer_id), None)
    if selected_answer:
        archetype_id = selected_answer['archetype_id']
        scores = user_data.get('scores', {})
        scores[archetype_id] = scores.get(archetype_id, 0) + points
        await state.update_data(scores=scores)
    
    await state.update_data(click_count=click_count, answered_in_question=answered_in_question)

    # --- Обновление клавиатуры ---
    current_answers = [ans for ans in ALL_ANSWERS if ans['question_id'] == current_question_id]
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_answers_keyboard(current_answers, answered_in_question)
    )

    # --- Переход к следующему вопросу ---
    if click_count == 3:
        # Убираем старую клавиатуру
        await callback_query.message.edit_reply_markup(reply_markup=None)

        if current_question_id == TOTAL_QUESTIONS:
            # Если это был последний вопрос, считаем результаты
            await calculate_and_send_results(callback_query.message.chat.id, state, bot)
        else:
            # Иначе переходим к следующему
            await state.update_data(current_question_id=current_question_id + 1)
            await bot.send_chat_action(callback_query.message.chat.id, 'typing')
            await asyncio.sleep(1.2)
            await send_question(callback_query.message.chat.id, state, bot)


async def calculate_and_send_results(chat_id: int, state: FSMContext, bot):
    user_data = await state.get_data()
    scores = user_data.get('scores', {})
    
    if not scores:
        await bot.send_message(chat_id, "Не удалось посчитать результаты. Попробуйте пройти тест заново /start")
        return

    sorted_archetypes = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    # Получаем результаты
    primary_archetype_id = sorted_archetypes[0][0]
    secondary_1_id = sorted_archetypes[1][0]
    secondary_2_id = sorted_archetypes[2][0]

    primary_result = google_sheets_db.get_archetype_result(primary_archetype_id)
    secondary_1_result = google_sheets_db.get_archetype_result(secondary_1_id)
    secondary_2_result = google_sheets_db.get_archetype_result(secondary_2_id)
    final_cta = google_sheets_db.get_config_value('final_cta_message')

    # Формируем итоговое сообщение
    final_message = (
        f"{primary_result['main_description']}\n\n"
        f"**Твои вторые энергии:**\n\n"
        f"{secondary_1_result['secondary_description']}\n\n"
        f"{secondary_2_result['secondary_description']}\n\n"
        f"_{final_cta}_"
    )

    await bot.send_message(chat_id, final_message, parse_mode="Markdown")
    await state.clear()