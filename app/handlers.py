import asyncio
import logging
import random
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, URLInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.gsheets import GoogleSheetsDB
from app.keyboards import generate_answers_keyboard
from config import GOOGLE_CREDENTIALS_PATH, GOOGLE_CREDENTIALS_JSON, SPREADSHEET_KEY

logging.basicConfig(level=logging.INFO)

router = Router()

class Introduction(StatesGroup):
    awaiting_promo_confirmation = State()
    awaiting_quiz_start = State()

class Quiz(StatesGroup):
    in_progress = State()
    awaiting_result_confirmation = State()

# Инициализация Google Sheets будет происходить в функциях
google_sheets_db = None

def get_google_sheets_db():
    global google_sheets_db
    if google_sheets_db is None:
        try:
            google_sheets_db = GoogleSheetsDB(
                credentials_json=GOOGLE_CREDENTIALS_JSON,
                credentials_path=GOOGLE_CREDENTIALS_PATH,
                spreadsheet_key=SPREADSHEET_KEY
            )
            logging.info("Google Sheets успешно инициализирован")
        except Exception as e:
            logging.critical(f"Критическая ошибка при инициализации Google-таблицы: {e}")
            logging.critical(f"SPREADSHEET_KEY: {SPREADSHEET_KEY}")
            logging.critical(f"GOOGLE_CREDENTIALS_JSON присутствует: {bool(GOOGLE_CREDENTIALS_JSON)}")
            logging.critical(f"GOOGLE_CREDENTIALS_PATH: {GOOGLE_CREDENTIALS_PATH}")
            raise
    return google_sheets_db


async def send_question(message: Message, state: FSMContext):
    try:
        db = get_google_sheets_db()
    except Exception as e:
        await message.answer("Извините, бот временно недоступен.")
        return

    user_data = await state.get_data()
    question_id = user_data.get('current_question_id', 1)

    question_data = db.get_question(question_id)
    answers = db.get_answers(question_id)

    if not question_data or not answers:
        await message.answer("Ошибка при загрузке вопроса. Пожалуйста, /start.")
        logging.error(f"Не удалось загрузить данные для вопроса ID: {question_id}")
        return

    # Перемешиваем ответы для каждого нового вопроса
    shuffled_answers = answers.copy()
    random.shuffle(shuffled_answers)
    
    # --- ИЗМЕНЕНИЕ: Формируем нумерованный список ответов ---
    answers_text_list = []
    for i, answer in enumerate(shuffled_answers):
        num = i + 1
        text = answer.get('answer_text', '')
        answers_text_list.append(f"<b>{num}.</b> {text}")
    
    answers_formatted_text = "\n\n".join(answers_text_list)

    full_question_text = (
        f"<b>{question_data.get('question_text', '')}</b>\n\n"
        f"{answers_formatted_text}\n\n"
        f"<i>{question_data.get('prompt_text', '')}</i>"
    )
    
    # Сохраняем текущий перемешанный список ответов
    await state.update_data(current_answers_order=shuffled_answers)

    await message.answer(
        full_question_text,
        reply_markup=generate_answers_keyboard(shuffled_answers, []),
        parse_mode="HTML"
    )

    await state.update_data(
        current_question_id=question_id,
        answered_in_question=[],
        click_count=0
    )
    await state.set_state(Quiz.in_progress)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    try:
        db = get_google_sheets_db()
    except Exception as e:
        await message.answer("Извините, бот временно недоступен.")
        return
        
    logging.info(f"User {message.from_user.id} started the conversation.")
    await state.clear()
    msg1_text = db.get_config_value('welcome_sequence_1').replace('\\n', '\n')
    msg2_text = db.get_config_value('welcome_sequence_2').replace('\\n', '\n')
    promo_text = db.get_config_value('promo_sequence').replace('\\n', '\n')
    
    await message.answer(msg1_text)
    await asyncio.sleep(1.5)
    
    await message.answer(msg2_text)
    await asyncio.sleep(1.5)

    button_text = db.get_config_value('promo_button_text')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, callback_data="start_instructions")]
    ])
    
    await message.answer(promo_text, reply_markup=keyboard)

    await state.set_state(Introduction.awaiting_promo_confirmation)


@router.callback_query(Introduction.awaiting_promo_confirmation, F.data == "start_instructions")
async def instructions_handler(callback_query: CallbackQuery, state: FSMContext):
    # ... (код этой функции остается без изменений)
    await callback_query.message.edit_reply_markup(reply_markup=None) 
    
    db = get_google_sheets_db()
    instruction_text = db.get_config_value('instruction_sequence').replace('\\n', '\n')
    button_text = db.get_config_value('start_button_text')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, callback_data="start_quiz_now")]
    ])
    
    await callback_query.message.answer(
        instruction_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await state.set_state(Introduction.awaiting_quiz_start)
    await callback_query.answer()


@router.callback_query(Introduction.awaiting_quiz_start, F.data == "start_quiz_now")
async def quiz_start_handler(callback_query: CallbackQuery, state: FSMContext):
    # ... (код этой функции остается без изменений)
    await callback_query.message.edit_reply_markup(reply_markup=None)
    
    db = get_google_sheets_db()
    all_archetypes = db.get_all_archetypes()
    if not all_archetypes:
        await callback_query.message.answer("Ошибка: не удалось загрузить данные. /start.")
        logging.error("Список архетипов пуст.")
        return
        
    initial_scores = {archetype['archetype_id']: 0 for archetype in all_archetypes if 'archetype_id' in archetype}
    await state.update_data(scores=initial_scores, current_question_id=1)
    
    await send_question(callback_query.message, state)
    await callback_query.answer()


@router.callback_query(Quiz.in_progress, F.data.startswith('ans_num:'))
async def callback_answer_handler(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    click_count = user_data.get('click_count', 0)

    if click_count >= 3:
        await callback_query.answer("Вы уже выбрали 3 варианта.", show_alert=True)
        return

    # --- ИЗМЕНЕНИЕ: Получаем номер ответа и находим его ID ---
    answer_num = int(callback_query.data.split(':')[1])
    answers = user_data.get('current_answers_order', [])
    
    # Номер - это индекс + 1
    if not (0 < answer_num <= len(answers)):
        await callback_query.answer("Ошибка! Неверный номер ответа.", show_alert=True)
        return

    selected_answer = answers[answer_num - 1]
    answer_id = selected_answer.get('answer_id')
    
    answered_in_question = user_data.get('answered_in_question', [])
    if answer_id in answered_in_question:
        await callback_query.answer("Этот вариант уже выбран.", show_alert=False)
        return

    click_count += 1
    answered_in_question.append(answer_id)
    
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
        await callback_query.answer("Принято! Все 3 варианта выбраны.", show_alert=False)
        await asyncio.sleep(1.5)

        current_question_id = user_data.get('current_question_id')
        if current_question_id == 19:
            await ask_to_show_results(callback_query.message, state)
        else:
            # Удаляем старое сообщение с вопросом перед отправкой нового
            await callback_query.message.delete()
            await state.update_data(current_question_id=current_question_id + 1)
            await send_question(callback_query.message, state)
    else:
        await callback_query.answer()


async def ask_to_show_results(message: Message, state: FSMContext):
    # ... (код этой функции остается без изменений)
    db = get_google_sheets_db()
    final_text = db.get_config_value('final_cta_text').replace('\\n', '\n')
    button_text = db.get_config_value('final_cta_button')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, callback_data="show_final_result")]
    ])
    
    await message.answer(final_text, reply_markup=keyboard)
    await state.set_state(Quiz.awaiting_result_confirmation)


@router.callback_query(Quiz.awaiting_result_confirmation, F.data == "show_final_result")
async def show_results_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)

    user_data = await state.get_data()
    scores = user_data.get('scores', {})
    
    if not scores:
        await callback_query.message.answer("Не удалось рассчитать результаты. /start.")
        return
        
    sorted_archetypes = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    # Отправляем основной архетип
    if len(sorted_archetypes) > 0:
        primary_archetype_id = sorted_archetypes[0][0]
        db = get_google_sheets_db()
        primary_result = db.get_archetype_result(primary_archetype_id)
        if primary_result:
            text = primary_result.get('main_description', '').replace('\\n', '\n')
            if text:
                await callback_query.message.answer(text, parse_mode="HTML")
                await asyncio.sleep(2)  # Пауза между сообщениями
    
    # Отправляем второй архетип
    if len(sorted_archetypes) > 1:
        secondary_1_id = sorted_archetypes[1][0]
        secondary_1_result = db.get_archetype_result(secondary_1_id)
        if secondary_1_result:
            text = secondary_1_result.get('secondary_description', '').replace('\\n', '\n')
            if text:
                await callback_query.message.answer(text, parse_mode="HTML")
                await asyncio.sleep(2)  # Пауза между сообщениями

    # Отправляем третий архетип
    if len(sorted_archetypes) > 2:
        secondary_2_id = sorted_archetypes[2][0]
        secondary_2_result = db.get_archetype_result(secondary_2_id)
        if secondary_2_result:
            text = secondary_2_result.get('secondary_description', '').replace('\\n', '\n')
            if text:
                await callback_query.message.answer(text, parse_mode="HTML")
                await asyncio.sleep(2)  # Пауза между сообщениями

    # Отправляем финальное сообщение с PDF, видео и ссылкой на оплату
    await send_final_media_and_payment(callback_query.message)
    
    await state.clear()
    await callback_query.answer()


async def send_final_media_and_payment(message: Message):
    """Отправляет PDF файл, видео и ссылку на оплату в конце теста"""
    try:
        # Получаем данные из Google Sheets
        db = get_google_sheets_db()
        pdf_url = db.get_config_value('final_pdf_url')
        video_url = db.get_config_value('final_video_url')
        payment_url = db.get_config_value('payment_url')
        final_message_text = db.get_config_value('final_message_text')
        payment_button_text = db.get_config_value('payment_button_text')

        # Отправляем PDF файл, если указан
        if pdf_url:
            try:
                await message.answer_document(
                    document=URLInputFile(pdf_url),
                    caption="📄 Ваш персональный отчет по результатам теста"
                )
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Ошибка при отправке PDF: {e}")

        # Отправляем видео, если указано
        if video_url:
            try:
                await message.answer_video(
                    video=URLInputFile(video_url),
                    caption="🎥 Дополнительная информация о вашем архетипе"
                )
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Ошибка при отправке видео: {e}")

        # Отправляем финальное сообщение со ссылкой на оплату
        if final_message_text:
            keyboard = None
            if payment_url and payment_button_text:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=payment_button_text, url=payment_url)]
                ])
            
            await message.answer(
                final_message_text.replace('\\n', '\n'),
                reply_markup=keyboard,
                parse_mode="HTML"
            )

    except Exception as e:
        logging.error(f"Ошибка при отправке финальных материалов: {e}")
        # Отправляем базовое сообщение в случае ошибки
        await message.answer("Спасибо за прохождение теста! 🎉")


@router.message(Command("help"))
async def help_handler(message: Message):
    # ... (код этой функции остается без изменений)
    help_text = (
        "<b>Доступные команды:</b>\n"
        "<code>/start</code> — Начать тест заново\n"
        "<code>/help</code> — Помощь по работе с ботом"
    )
    await message.answer(help_text, parse_mode="HTML")