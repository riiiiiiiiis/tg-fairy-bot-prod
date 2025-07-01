import asyncio
import logging
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.gsheets import GoogleSheetsDB
from app.keyboards import generate_answers_keyboard
from config import GOOGLE_CREDENTIALS_PATH, SPREADSHEET_KEY

logging.basicConfig(level=logging.INFO)

router = Router()

class Quiz(StatesGroup):
    in_progress = State()

try:
    google_sheets_db = GoogleSheetsDB(
        credentials_path=GOOGLE_CREDENTIALS_PATH,
        spreadsheet_key=SPREADSHEET_KEY
    )
except Exception as e:
    logging.critical(f"Критическая ошибка при инициализации Google-таблицы: {e}")
    google_sheets_db = None


async def send_question(message: Message, state: FSMContext):
    if not google_sheets_db:
        await message.answer("Извините, бот временно недоступен из-за проблем с подключением к данным.")
        return

    user_data = await state.get_data()
    question_id = user_data.get('current_question_id', 1)

    question_data = google_sheets_db.get_question(question_id)
    answers = google_sheets_db.get_answers(question_id)

    if not question_data or not answers:
        await message.answer("Ошибка при загрузке вопроса. Пожалуйста, попробуйте перезапустить тест командой /start.")
        logging.error(f"Не удалось загрузить данные для вопроса ID: {question_id}")
        return

    full_question_text = (
        f"*{question_data.get('question_text', '')}*\n\n"
        f"_{question_data.get('prompt_text', '')}_"
    )

    try:
        await message.answer(
            full_question_text,
            reply_markup=generate_answers_keyboard(answers, []),
            parse_mode="MarkdownV2"
        )
    except Exception:
        await message.answer(
            full_question_text.replace("*", "").replace("_", ""),
            reply_markup=generate_answers_keyboard(answers, [])
        )


    await state.update_data(
        current_question_id=question_id,
        answered_in_question=[],
        click_count=0
    )
    await state.set_state(Quiz.in_progress)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    if not google_sheets_db:
        await message.answer("Извините, бот временно недоступен из-за проблем с подключением к данным.")
        return
        
    logging.info(f"User {message.from_user.id} started the quiz.")
    
    welcome_message = google_sheets_db.get_config_value('welcome_message')
    
    await message.answer(f"🔮 {welcome_message}")
    await asyncio.sleep(0.8)

    await state.clear()
    
    all_archetypes = google_sheets_db.get_all_archetypes()
    if not all_archetypes:
        await message.answer("Ошибка: не удалось загрузить данные теста. Пожалуйста, сообщите администратору.")
        logging.error("Не удалось инициализировать счет: список архетипов пуст.")
        return
        
    initial_scores = {archetype['archetype_id']: 0 for archetype in all_archetypes if 'archetype_id' in archetype}
    await state.update_data(scores=initial_scores, current_question_id=1)
    
    await send_question(message, state)


@router.callback_query(F.data.startswith('ans:'))
async def callback_answer_handler(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    click_count = user_data.get('click_count', 0)

    if click_count >= 3:
        await callback_query.answer("Вы уже выбрали 3 варианта.", show_alert=True)
        return

    answer_id = int(callback_query.data.split(':')[1])
    answered_in_question = user_data.get('answered_in_question', [])

    if answer_id in answered_in_question:
        await callback_query.answer("Этот вариант уже выбран.", show_alert=False)
        return

    click_count += 1
    answered_in_question.append(answer_id)
    
    current_question_id = user_data.get('current_question_id')
    answers = google_sheets_db.get_answers(current_question_id)
    selected_answer = next((ans for ans in answers if ans.get('answer_id') == answer_id), None)
    
    if not selected_answer:
        await callback_query.answer("Ошибка! Вариант не найден.", show_alert=True)
        return
        
    archetype_id = selected_answer.get('archetype_id')
    points = 3 - (click_count - 1)
    
    scores = user_data.get('scores', {})
    scores[archetype_id] = scores.get(archetype_id, 0) + points
    
    await state.update_data(
        click_count=click_count, 
        answered_in_question=answered_in_question,
        scores=scores
    )

    await callback_query.message.edit_reply_markup(
        reply_markup=generate_answers_keyboard(answers, answered_in_question)
    )

    if click_count == 3:
        await callback_query.answer("Принято!", show_alert=False)
        await asyncio.sleep(1.5)

        if current_question_id == 19:
            await calculate_and_send_results(callback_query.message, state)
        else:
            await state.update_data(current_question_id=current_question_id + 1)
            await send_question(callback_query.message, state)
    else:
        await callback_query.answer()


async def calculate_and_send_results(message: Message, state: FSMContext):
    user_data = await state.get_data()
    scores = user_data.get('scores', {})
    
    if not scores:
        await message.answer("Не удалось рассчитать результаты. Пожалуйста, начните заново /start.")
        return
        
    sorted_archetypes = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    final_message_parts = []
    
    if len(sorted_archetypes) > 0:
        primary_archetype_id = sorted_archetypes[0][0]
        primary_result = google_sheets_db.get_archetype_result(primary_archetype_id)
        if primary_result:
            final_message_parts.append(primary_result.get('main_description', ''))
    
    if len(sorted_archetypes) > 1:
        secondary_1_id = sorted_archetypes[1][0]
        secondary_1_result = google_sheets_db.get_archetype_result(secondary_1_id)
        if secondary_1_result:
            final_message_parts.append(secondary_1_result.get('secondary_description', ''))

    if len(sorted_archetypes) > 2:
        secondary_2_id = sorted_archetypes[2][0]
        secondary_2_result = google_sheets_db.get_archetype_result(secondary_2_id)
        if secondary_2_result:
            final_message_parts.append(secondary_2_result.get('secondary_description', ''))
            
    final_cta_message = google_sheets_db.get_config_value('result_prompt')
    if final_cta_message:
        final_message_parts.append(final_cta_message)
        
    final_message = "\n\n".join(filter(None, final_message_parts))

    await message.answer(final_message)
    await state.clear()