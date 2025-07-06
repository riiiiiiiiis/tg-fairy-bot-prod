import gspread
from oauth2client.service_account import ServiceAccountCredentials
from cachetools import cached, TTLCache
import logging

logging.basicConfig(level=logging.INFO)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

class GoogleSheetsDB:
    def __init__(self, credentials_path=None, credentials_json=None, spreadsheet_key=None):
        try:
            if credentials_json:
                # Use JSON string from environment variable
                import json
                if isinstance(credentials_json, str):
                    creds_dict = json.loads(credentials_json)
                else:
                    creds_dict = credentials_json
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            elif credentials_path:
                # Fallback to file path
                creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
            else:
                raise ValueError("Either credentials_json or credentials_path must be provided")
            
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(spreadsheet_key)
            logging.info("Успешное подключение к Google-таблице.")
        except Exception as e:
            logging.error(f"Не удалось инициализировать Google-таблицу: {e}")
            raise

    @cached(cache=TTLCache(maxsize=128, ttl=300))
    def get_config_value(self, key):
        try:
            sheet = self.spreadsheet.worksheet('Config')
            cell = sheet.find(key)
            return sheet.cell(cell.row, cell.col + 1).value
        except gspread.exceptions.WorksheetNotFound:
            logging.error("Лист 'Config' не найден.")
            return None
        except gspread.exceptions.CellNotFound:
            logging.error(f"Ключ '{key}' не найден на листе 'Config'.")
            return None

    @cached(cache=TTLCache(maxsize=128, ttl=300))
    def get_question(self, question_id):
        try:
            sheet = self.spreadsheet.worksheet('Questions')
            all_rows = sheet.get_all_values()
            for row in all_rows:
                if row and row[0] == str(question_id):
                    return {'question_text': row[1], 'prompt_text': row[2]}
            return None
        except gspread.exceptions.WorksheetNotFound:
            logging.error("Лист 'Questions' не найден.")
            return None

    @cached(cache=TTLCache(maxsize=128, ttl=300))
    def get_answers(self, question_id):
        try:
            sheet = self.spreadsheet.worksheet('Answers')
            records = sheet.get_all_records()
            return [record for record in records if record.get('question_id') == question_id]
        except gspread.exceptions.WorksheetNotFound:
            logging.error("Лист 'Answers' не найден.")
            return []

    @cached(cache=TTLCache(maxsize=128, ttl=300))
    def get_archetype_result(self, archetype_id):
        try:
            sheet = self.spreadsheet.worksheet('Archetypes')
            all_rows = sheet.get_all_values()
            for row in all_rows:
                if row and row[0] == archetype_id:
                    return {'main_description': row[1], 'secondary_description': row[2]}
            return None
        except gspread.exceptions.WorksheetNotFound:
            logging.error("Лист 'Archetypes' не найден.")
            return None

    @cached(cache=TTLCache(maxsize=10, ttl=3600))
    def get_all_archetypes(self):
        try:
            sheet = self.spreadsheet.worksheet('Archetypes')
            records = sheet.get_all_records()
            return records
        except gspread.exceptions.WorksheetNotFound:
            logging.error("Лист 'Archetypes' не найден.")
            return []
        except Exception as e:
            logging.error(f"Не удалось получить список архетипов: {e}")
            return []