import asyncio
import logging
import random
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, URLInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.gsheets import GoogleSheetsDB, UnifiedGoogleSheetsDB
from app.keyboards import generate_answers_keyboard, generate_gender_selection_keyboard, generate_final_buttons_keyboard, generate_about_us_keyboard, generate_workbook_keyboard
from config import GOOGLE_CREDENTIALS_PATH, GOOGLE_CREDENTIALS_JSON, SPREADSHEET_KEY

logging.basicConfig(level=logging.INFO)

router = Router()

# Глобальный экземпляр БД - создается один раз при запуске
try:
    global_db = UnifiedGoogleSheetsDB(
        credentials_path=GOOGLE_CREDENTIALS_PATH,
        credentials_json=GOOGLE_CREDENTIALS_JSON,
        spreadsheet_key=SPREADSHEET_KEY
    )
    logging.info("✅ Глобальный экземпляр БД успешно создан")
except Exception as e:
    logging.error(f"❌ Ошибка создания глобального экземпляра БД: {e}")
    global_db = None

class Introduction(StatesGroup):
    awaiting_gender_selection = State()
    awaiting_promo_confirmation = State()
    awaiting_quiz_start = State()

class Quiz(StatesGroup):
    in_progress = State()
    awaiting_result_confirmation = State()


async def send_question(message: Message, state: FSMContext):
    user_data = await state.get_data()
    
    # Получаем пол пользователя из состояния
    user_gender = user_data.get('selected_gender', 'female')
    
    if not global_db:
        await message.answer("Ошибка подключения к базе данных. Попробуйте /start.")
        return
    question_id = user_data.get('current_question_id', 1)

    question_data = global_db.get_question(question_id, user_gender)
    answers = global_db.get_answers(question_id, user_gender)

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
    logging.info(f"User {message.from_user.id} started the conversation.")
    await state.clear()
    
    # Показываем приветствие и выбор пола
    await message.answer("Добро пожаловать в тест архетипов! 🌟")
    await asyncio.sleep(1)
    
    await message.answer(
        "Для получения наиболее точных результатов, пожалуйста, выберите ваш пол:",
        reply_markup=generate_gender_selection_keyboard()
    )
    
    await state.set_state(Introduction.awaiting_gender_selection)


@router.callback_query(Introduction.awaiting_gender_selection, F.data.startswith('gender:'))
async def gender_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик выбора пола пользователя"""
    # Сразу отвечаем на callback, чтобы избежать timeout
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=None)
    
    # Извлекаем выбранный пол из callback_data
    gender = callback_query.data.split(':')[1]
    
    if gender not in ["male", "female"]:
        await callback_query.message.answer("Ошибка выбора пола. Попробуйте еще раз.")
        return
    
    # Показываем индикатор загрузки
    loading_msg = await callback_query.message.answer("⏳ Загружаем данные...")
    
    # Проверяем, находимся ли мы в тест-режиме
    user_data = await state.get_data()
    test_mode = user_data.get('test_mode', False)
    
    # Проверяем доступность глобальной БД
    if not global_db:
        await callback_query.message.answer("Ошибка подключения к базе данных. Попробуйте позже.")
        await callback_query.answer()
        return
        
    # Сохраняем только выбранный пол в состоянии
    await state.update_data(selected_gender=gender)
    
    # Удаляем сообщение загрузки
    try:
        await loading_msg.delete()
    except:
        pass  # Игнорируем ошибки удаления
    
    # Показываем подтверждение выбора
    gender_text = "мужчина" if gender == "male" else "женщина"
    await callback_query.message.answer(f"Отлично! Вы выбрали: {gender_text} 👍")
    await asyncio.sleep(1)
    
    # Если тест-режим, показываем финальное сообщение и выходим
    if test_mode:
        await handle_test_final_message(callback_query.message, global_db, gender)
        await state.clear()
        return
    
    # Переходим к промо-сообщению
    msg1_text = global_db.get_config_value('welcome_sequence_1').replace('\\n', '\n')
    msg2_text = global_db.get_config_value('welcome_sequence_2').replace('\\n', '\n')
    promo_text = global_db.get_config_value('promo_sequence').replace('\\n', '\n')
    
    await callback_query.message.answer(msg1_text)
    await asyncio.sleep(1.5)
    
    await callback_query.message.answer(msg2_text)
    await asyncio.sleep(1.5)

    button_text = global_db.get_config_value('promo_button_text')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, callback_data="start_instructions")]
    ])
    
    await callback_query.message.answer(promo_text, reply_markup=keyboard)
    await state.set_state(Introduction.awaiting_promo_confirmation)


@router.callback_query(Introduction.awaiting_promo_confirmation, F.data == "start_instructions")
async def instructions_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None) 
    
    if not global_db:
        await callback_query.message.answer("Ошибка подключения к базе данных. Попробуйте /start.")
        await callback_query.answer()
        return
    
    # Config лист общий для всех, поэтому не передаем пол
    instruction_text = global_db.get_config_value('instruction_sequence').replace('\\n', '\n')
    button_text = global_db.get_config_value('start_button_text')
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
    await callback_query.message.edit_reply_markup(reply_markup=None)
    
    user_data = await state.get_data()
    user_gender = user_data.get('selected_gender', 'female')
    
    if not global_db:
        await callback_query.message.answer("Ошибка подключения к базе данных. Попробуйте /start.")
        await callback_query.answer()
        return
    all_archetypes = global_db.get_all_archetypes(user_gender)
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
    if not global_db:
        await message.answer("Ошибка подключения к базе данных. Попробуйте /start.")
        return
    
    # Config лист общий для всех, поэтому не передаем пол
    final_text = global_db.get_config_value('final_cta_text').replace('\\n', '\n')
    button_text = global_db.get_config_value('final_cta_button')
    
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
    
    # Получаем пол пользователя из состояния
    user_gender = user_data.get('selected_gender', 'female')
    
    if not global_db:
        await callback_query.message.answer("Ошибка подключения к базе данных. Попробуйте /start.")
        await callback_query.answer()
        return
    
    # Отправляем основной архетип
    if len(sorted_archetypes) > 0:
        primary_archetype_id = sorted_archetypes[0][0]
        primary_result = global_db.get_archetype_result(primary_archetype_id, user_gender)
        if primary_result:
            text = primary_result.get('main_description', '').replace('\\n', '\n')
            if text:
                await callback_query.message.answer(text, parse_mode="HTML")
                await asyncio.sleep(2)  # Пауза между сообщениями
    
    # Отправляем второй архетип
    if len(sorted_archetypes) > 1:
        secondary_1_id = sorted_archetypes[1][0]
        secondary_1_result = global_db.get_archetype_result(secondary_1_id, user_gender)
        if secondary_1_result:
            text = secondary_1_result.get('secondary_description', '').replace('\\n', '\n')
            if text:
                await callback_query.message.answer(text, parse_mode="HTML")
                await asyncio.sleep(2)  # Пауза между сообщениями

    # Отправляем третий архетип
    if len(sorted_archetypes) > 2:
        secondary_2_id = sorted_archetypes[2][0]
        secondary_2_result = global_db.get_archetype_result(secondary_2_id, user_gender)
        if secondary_2_result:
            text = secondary_2_result.get('secondary_description', '').replace('\\n', '\n')
            if text:
                await callback_query.message.answer(text, parse_mode="HTML")
                await asyncio.sleep(2)  # Пауза между сообщениями

    # Отправляем финальное сообщение с PDF, видео и ссылкой на оплату
    await send_final_media_and_payment(callback_query.message, global_db)
    
    # Состояние будет очищено после нажатия на финальные кнопки
    await callback_query.answer()


@router.callback_query(F.data == "about_us")
async def about_us_handler(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Узнать больше про нас'"""
    await callback_query.answer()
    
    if not global_db:
        await callback_query.message.answer("Ошибка подключения к базе данных. Попробуйте позже.")
        await state.clear()
        return
    
    # Получаем текст about_us из конфигурации
    about_us_text = global_db.get_config_value('about_us')
    
    if about_us_text:
        formatted_text = about_us_text.replace('\\n', '\n')
        keyboard = generate_about_us_keyboard()
        await callback_query.message.answer(formatted_text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await callback_query.message.answer("Информация временно недоступна.")
    
    # Очищаем состояние после обработки
    await state.clear()


@router.callback_query(F.data == "workbook")
async def workbook_handler(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Скачать рабочую тетрадь magic book'"""
    await callback_query.answer()
    
    if not global_db:
        await callback_query.message.answer("Ошибка подключения к базе данных. Попробуйте позже.")
        return
    
    # Получаем текст workbook из конфигурации
    workbook_text = global_db.get_config_value('workbook')
    
    if workbook_text:
        formatted_text = workbook_text.replace('\\n', '\n')
        keyboard = generate_workbook_keyboard()
        await callback_query.message.answer(formatted_text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await callback_query.message.answer("Информация о рабочей тетради временно недоступна.")


async def send_final_media_and_payment(message: Message, db: GoogleSheetsDB):
    """Отправляет PDF ссылку, видео и ссылку на оплату в конце теста"""
    try:
        # Получаем данные из Google Sheets (используем существующие ключи)
        pdf_url = db.get_config_value('final_pdf_url')
        video_url = db.get_config_value('final_video_url')
        payment_url = db.get_config_value('payment_url')
        
        # Используем существующие ключи из Config
        final_message_text = db.get_config_value('final_message_text')
        payment_button_text = db.get_config_value('final_cta_button')
        
        # Подробное логирование для отладки
        logging.info(f"📊 Финальные настройки:")
        logging.info(f"   PDF URL: '{pdf_url}' (длина: {len(pdf_url) if pdf_url else 0})")
        logging.info(f"   Video URL: '{video_url}' (длина: {len(video_url) if video_url else 0})")
        logging.info(f"   Payment URL: '{payment_url}'")
        logging.info(f"   Final message: {bool(final_message_text)}")
        logging.info(f"   Button text: '{payment_button_text}'")

        # Отправляем финальное сообщение с кнопками
        message_text = final_message_text or "🎉 <b>Поздравляем!</b>\n\nВы успешно прошли тест архетипов!\n\nСпасибо за участие!"
        formatted_text = message_text.replace('\\n', '\n')
        
        logging.info("📨 Отправляем финальное сообщение с кнопками")
        keyboard = generate_final_buttons_keyboard()
        await message.answer(formatted_text, parse_mode="HTML", reply_markup=keyboard)
        
        # Больше ничего не отправляем автоматически - только кнопки для взаимодействия

    except Exception as e:
        logging.error(f"Ошибка при отправке финальных материалов: {e}")
        # Отправляем базовое сообщение в случае ошибки
        await message.answer("Спасибо за прохождение теста! 🎉")


@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "<b>Доступные команды:</b>\n"
        "<code>/start</code> — Начать тест заново\n"
        "<code>/test</code> — Тест финального сообщения\n"
        "<code>/debug</code> — Проверка конфигурации\n"
        "<code>/help</code> — Помощь по работе с ботом"
    )
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("test"))
async def test_handler(message: Message, state: FSMContext):
    """Тестовая команда для проверки финального сообщения"""
    await message.answer("🧪 Тестируем финальное сообщение...")
    
    # Показываем выбор пола для теста
    await message.answer(
        "Выберите пол для тестирования:",
        reply_markup=generate_gender_selection_keyboard()
    )
    
    # Устанавливаем специальное состояние для теста
    await state.set_state(Introduction.awaiting_gender_selection)
    await state.update_data(test_mode=True)


@router.message(Command("debug"))
async def debug_handler(message: Message):
    """Отладочная команда для проверки Config листа"""
    if not global_db:
        await message.answer("❌ Глобальная БД недоступна")
        return
    
    try:
        
        # Проверяем основные ключи
        basic_keys = ['welcome_sequence_1', 'welcome_sequence_2', 'promo_sequence', 'promo_button_text', 'start_button_text']
        final_keys = ['final_cta_text', 'final_cta_button', 'final_proposition', 'final_pdf_url', 'final_video_url', 'payment_url']
        
        debug_info = "🔍 <b>Отладочная информация:</b>\n\n"
        
        debug_info += "<b>Основные ключи:</b>\n"
        for key in basic_keys:
            value = global_db.get_config_value(key)
            status = "✅" if value else "❌"
            debug_info += f"{status} {key}: {bool(value)}\n"
        
        debug_info += "\n<b>Финальные ключи:</b>\n"
        for key in final_keys:
            value = global_db.get_config_value(key)
            status = "✅" if value else "❌"
            debug_info += f"{status} {key}: {bool(value)}\n"
            
            # Показываем содержимое медиа-ссылок
            if key in ['final_pdf_url', 'final_video_url'] and value:
                debug_info += f"   📎 {key}: {value[:50]}{'...' if len(value) > 50 else ''}\n"
        
        await message.answer(debug_info, parse_mode="HTML")
        
        # Дополнительная информация о медиа-файлах
        pdf_url = db.get_config_value('final_pdf_url')
        video_url = db.get_config_value('final_video_url')
        
        if pdf_url or video_url:
            media_info = "\n🔗 <b>Медиа-ссылки (полные):</b>\n\n"
            
            if pdf_url:
                media_info += f"📄 <b>PDF:</b>\n"
                media_info += f"   Длина: {len(pdf_url)} символов\n"
                media_info += f"   Ссылка: <code>{pdf_url}</code>\n\n"
            
            if video_url:
                media_info += f"🎥 <b>Видео:</b>\n"
                media_info += f"   Длина: {len(video_url)} символов\n"
                media_info += f"   Ссылка: <code>{video_url}</code>\n"
            
            await message.answer(media_info, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка отладки: {e}")


# Модифицируем обработчик выбора пола для поддержки тест-режима
async def handle_test_final_message(message: Message, db: UnifiedGoogleSheetsDB, user_gender: str = "female"):
    """Отправляет тестовое финальное сообщение с примерными результатами"""
    await message.answer("🎯 <b>Результаты теста (ТЕСТОВЫЙ РЕЖИМ)</b>", parse_mode="HTML")
    await asyncio.sleep(1)
    
    # Получаем все архетипы для демонстрации
    all_archetypes = db.get_all_archetypes(user_gender)
    if not all_archetypes:
        await message.answer("❌ Ошибка: не удалось загрузить архетипы из таблицы")
        return
    
    # Берем первые 3 архетипа для демонстрации
    demo_archetypes = all_archetypes[:3] if len(all_archetypes) >= 3 else all_archetypes
    
    # Отправляем основной архетип
    if len(demo_archetypes) > 0:
        primary_archetype_id = demo_archetypes[0].get('archetype_id')
        if primary_archetype_id:
            primary_result = global_db.get_archetype_result(primary_archetype_id, user_gender)
            if primary_result:
                text = primary_result.get('main_description', '').replace('\\n', '\n')
                if text:
                    await message.answer(f"🥇 <b>Основной архетип:</b>\n\n{text}", parse_mode="HTML")
                    await asyncio.sleep(0.5)
    
    # Отправляем второй архетип
    if len(demo_archetypes) > 1:
        secondary_1_id = demo_archetypes[1].get('archetype_id')
        if secondary_1_id:
            secondary_1_result = global_db.get_archetype_result(secondary_1_id, user_gender)
            if secondary_1_result:
                text = secondary_1_result.get('secondary_description', '').replace('\\n', '\n')
                if text:
                    await message.answer(f"🥈 <b>Вторичный архетип:</b>\n\n{text}", parse_mode="HTML")
                    await asyncio.sleep(0.5)

    # Отправляем третий архетип
    if len(demo_archetypes) > 2:
        secondary_2_id = demo_archetypes[2].get('archetype_id')
        if secondary_2_id:
            secondary_2_result = global_db.get_archetype_result(secondary_2_id, user_gender)
            if secondary_2_result:
                text = secondary_2_result.get('secondary_description', '').replace('\\n', '\n')
                if text:
                    await message.answer(f"🥉 <b>Третий архетип:</b>\n\n{text}", parse_mode="HTML")
                    await asyncio.sleep(0.5)

    # Отправляем финальные материалы
    await send_final_media_and_payment(message, db)
    
    await message.answer("✅ <b>Тест завершен!</b>\n\nИспользуйте /start для обычного режима.", parse_mode="HTML")