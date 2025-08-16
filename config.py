import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "google_credentials.json")

# Объединенная таблица - единственная переменная для новой архитектуры
SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")

# Проверяем наличие старых переменных и предупреждаем о необходимости миграции
_old_female_key = os.getenv("SPREADSHEET_KEY_FEMALE")
_old_male_key = os.getenv("SPREADSHEET_KEY_MALE")

if _old_female_key or _old_male_key:
    logging.warning("⚠️  Обнаружены устаревшие переменные окружения:")
    if _old_female_key:
        logging.warning(f"   SPREADSHEET_KEY_FEMALE={_old_female_key}")
    if _old_male_key:
        logging.warning(f"   SPREADSHEET_KEY_MALE={_old_male_key}")
    logging.warning("   Эти переменные больше не используются.")
    logging.warning("   Используйте SPREADSHEET_KEY для объединенной таблицы.")
    logging.warning("   Подробности в документации: docs/google-sheets-structure.md")

if not SPREADSHEET_KEY:
    logging.error("❌ SPREADSHEET_KEY не указан в переменных окружения")
    logging.error("   Укажите ID объединенной таблицы в переменной SPREADSHEET_KEY")
else:
    logging.info(f"✅ Используется объединенная таблица: {SPREADSHEET_KEY}")