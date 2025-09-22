import gspread
from google.oauth2 import service_account
from cachetools import cached, TTLCache
import logging
import os
import json

logging.basicConfig(level=logging.INFO)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

class GoogleSheetsDB:
    def __init__(self, credentials_path=None, credentials_json=None, spreadsheet_key=None):
        try:
            if not spreadsheet_key:
                raise ValueError("SPREADSHEET_KEY не указан в переменных окружения")

            if credentials_json:
                # Use JSON string from environment variable
                logging.info("Используем JSON credentials из переменной окружения")
                if isinstance(credentials_json, str):
                    creds_dict = json.loads(credentials_json)
                else:
                    creds_dict = credentials_json
                creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
            elif credentials_path:
                # Fallback to file path
                logging.info(f"Используем credentials из файла: {credentials_path}")
                creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scope)
            else:
                raise ValueError("Either credentials_json or credentials_path must be provided")

            logging.info("Авторизация в Google Sheets...")
            self.client = gspread.authorize(creds)
            
            logging.info(f"Открываем таблицу с ключом: {spreadsheet_key}")
            self.spreadsheet = self.client.open_by_key(spreadsheet_key)
            
            # Проверяем доступ к основным листам
            required_sheets = ['Config', 'Questions', 'Answers', 'Archetypes']
            available_sheets = [ws.title for ws in self.spreadsheet.worksheets()]
            logging.info(f"Доступные листы: {available_sheets}")
            
            missing_sheets = [sheet for sheet in required_sheets if sheet not in available_sheets]
            if missing_sheets:
                raise ValueError(f"Отсутствуют обязательные листы: {missing_sheets}")
            
            logging.info("Успешное подключение к Google-таблице.")
        except json.JSONDecodeError as e:
            logging.error(f"Ошибка парсинга JSON credentials: {e}")
            raise
        except gspread.exceptions.SpreadsheetNotFound:
            logging.error(f"Таблица с ключом {spreadsheet_key} не найдена или нет доступа")
            raise
        except gspread.exceptions.APIError as e:
            logging.error(f"Ошибка Google Sheets API: {e}")
            raise
        except Exception as e:
            logging.error(f"Не удалось инициализировать Google-таблицу: {e}")
            logging.error(f"Тип ошибки: {type(e).__name__}")
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


class GenderBasedSheetsManager:
    """Менеджер для работы с разными таблицами в зависимости от пола пользователя"""
    
    def __init__(self, credentials_json=None, credentials_path=None, female_key=None, male_key=None):
        self.female_key = female_key
        self.male_key = male_key
        self.credentials_json = credentials_json
        self.credentials_path = credentials_path
        
        # Инициализируем базы данных
        self._female_db = None
        self._male_db = None
        
        logging.info(f"Инициализация GenderBasedSheetsManager:")
        logging.info(f"Female key: {female_key}")
        logging.info(f"Male key: {male_key}")
    
    def _get_female_db(self):
        """Ленивая инициализация женской БД"""
        if self._female_db is None:
            try:
                self._female_db = GoogleSheetsDB(
                    credentials_json=self.credentials_json,
                    credentials_path=self.credentials_path,
                    spreadsheet_key=self.female_key
                )
                logging.info("Женская БД успешно инициализирована")
            except Exception as e:
                logging.error(f"Ошибка инициализации женской БД: {e}")
                raise
        return self._female_db
    
    def _get_male_db(self):
        """Ленивая инициализация мужской БД с fallback на женскую"""
        if self._male_db is None:
            try:
                if not self.male_key or self.male_key == self.female_key:
                    logging.warning("Мужская таблица не настроена, используем женскую как fallback")
                    return self._get_female_db()
                
                self._male_db = GoogleSheetsDB(
                    credentials_json=self.credentials_json,
                    credentials_path=self.credentials_path,
                    spreadsheet_key=self.male_key
                )
                logging.info("Мужская БД успешно инициализирована")
            except Exception as e:
                logging.error(f"Ошибка инициализации мужской БД: {e}")
                logging.warning("Используем женскую БД как fallback")
                return self._get_female_db()
        return self._male_db
    
    def get_db_for_gender(self, gender: str) -> GoogleSheetsDB:
        """Возвращает соответствующую БД для указанного пола"""
        if not self.validate_gender(gender):
            logging.warning(f"Некорректный пол '{gender}', используем женскую БД по умолчанию")
            return self._get_female_db()
        
        if gender == "male":
            return self._get_male_db()
        else:  # female или любой другой случай
            return self._get_female_db()
    
    def validate_gender(self, gender: str) -> bool:
        """Валидация пола"""
        return gender in ["male", "female"]
    
    def get_supported_genders(self) -> list:
        """Возвращает список поддерживаемых полов"""
        return ["male", "female"]


class UnifiedGoogleSheetsDB(GoogleSheetsDB):
    """Унифицированная база данных с поддержкой выбора листов по полу пользователя"""
    
    def __init__(self, credentials_path=None, credentials_json=None, spreadsheet_key=None):
        # Сначала инициализируем базовый класс, но без проверки старых листов
        try:
            if not spreadsheet_key:
                raise ValueError("SPREADSHEET_KEY не указан в переменных окружения")

            # Приоритет: сначала файл, потом JSON из переменной окружения
            if credentials_path and os.path.exists(credentials_path):
                logging.info(f"Используем credentials из файла: {credentials_path}")
                creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scope)
            elif credentials_json:
                logging.info("Используем JSON credentials из переменной окружения")
                if isinstance(credentials_json, str):
                    creds_dict = json.loads(credentials_json)
                else:
                    creds_dict = credentials_json
                creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
            else:
                raise ValueError("Either credentials_json or credentials_path must be provided")
            
            logging.info("Авторизация в Google Sheets...")
            self.client = gspread.authorize(creds)
            
            logging.info(f"Открываем объединенную таблицу с ключом: {spreadsheet_key}")
            self.spreadsheet = self.client.open_by_key(spreadsheet_key)
            
            # Проверяем доступ к листам новой структуры
            self._validate_unified_structure()
            
            logging.info("Успешное подключение к объединенной Google-таблице.")
        except Exception as e:
            logging.error(f"Не удалось инициализировать объединенную Google-таблицу: {e}")
            raise
    
    def _validate_unified_structure(self):
        """Проверяет наличие необходимых листов в объединенной таблице"""
        available_sheets = [ws.title for ws in self.spreadsheet.worksheets()]
        logging.info(f"Доступные листы в объединенной таблице: {available_sheets}")
        
        # Обязательные листы для новой структуры
        required_sheets = [
            'Config',
            'Questions_Female', 'Answers_Female', 'Archetypes_Female',
            'Questions_Male', 'Answers_Male', 'Archetypes_Male'
        ]
        
        missing_sheets = [sheet for sheet in required_sheets if sheet not in available_sheets]
        if missing_sheets:
            logging.error(f"Отсутствуют обязательные листы в объединенной таблице: {missing_sheets}")
            logging.error("Убедитесь, что таблица содержит все необходимые листы для обоих полов")
            raise ValueError(f"Отсутствуют обязательные листы: {missing_sheets}")
        
        logging.info("Структура объединенной таблицы корректна")
    
    def _get_sheet_name(self, base_name: str, user_gender: str) -> str:
        """Возвращает название листа в зависимости от пола пользователя"""
        if base_name == "Config":
            return "Config"  # Config общий для всех пользователей
        
        # Валидация пола с fallback на female
        if user_gender not in ["male", "female"]:
            logging.warning(f"Некорректный пол пользователя '{user_gender}', используем 'female'")
            user_gender = "female"
        
        # Формируем название листа
        suffix = "Male" if user_gender == "male" else "Female"
        sheet_name = f"{base_name}_{suffix}"
        
        logging.debug(f"Выбран лист '{sheet_name}' для пола '{user_gender}'")
        return sheet_name
    
    def validate_user_gender(self, user_gender: str) -> str:
        """Валидация пола пользователя с fallback на female"""
        if user_gender not in ["male", "female"]:
            logging.warning(f"Некорректный пол пользователя: {user_gender}, используем 'female'")
            return "female"
        return user_gender
    
    @cached(cache=TTLCache(maxsize=128, ttl=300))
    def get_question(self, question_id, user_gender="female"):
        """Получить вопрос из соответствующего листа в зависимости от пола"""
        user_gender = self.validate_user_gender(user_gender)
        sheet_name = self._get_sheet_name("Questions", user_gender)
        
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            all_rows = sheet.get_all_values()
            for row in all_rows:
                if row and row[0] == str(question_id):
                    return {'question_text': row[1], 'prompt_text': row[2]}
            return None
        except gspread.exceptions.WorksheetNotFound:
            logging.error(f"Лист '{sheet_name}' не найден.")
            return None
        except Exception as e:
            logging.error(f"Ошибка получения вопроса {question_id} из листа {sheet_name}: {e}")
            return None
    
    @cached(cache=TTLCache(maxsize=128, ttl=300))
    def get_answers(self, question_id, user_gender="female"):
        """Получить ответы из соответствующего листа в зависимости от пола"""
        user_gender = self.validate_user_gender(user_gender)
        sheet_name = self._get_sheet_name("Answers", user_gender)
        
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            records = sheet.get_all_records()
            return [record for record in records if record.get('question_id') == question_id]
        except gspread.exceptions.WorksheetNotFound:
            logging.error(f"Лист '{sheet_name}' не найден.")
            return []
        except Exception as e:
            logging.error(f"Ошибка получения ответов для вопроса {question_id} из листа {sheet_name}: {e}")
            return []
    
    @cached(cache=TTLCache(maxsize=128, ttl=300))
    def get_archetype_result(self, archetype_id, user_gender="female"):
        """Получить архетип из соответствующего листа в зависимости от пола"""
        user_gender = self.validate_user_gender(user_gender)
        sheet_name = self._get_sheet_name("Archetypes", user_gender)
        
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            all_rows = sheet.get_all_values()
            for row in all_rows:
                if row and row[0] == archetype_id:
                    return {'main_description': row[1], 'secondary_description': row[2]}
            return None
        except gspread.exceptions.WorksheetNotFound:
            logging.error(f"Лист '{sheet_name}' не найден.")
            return None
        except Exception as e:
            logging.error(f"Ошибка получения архетипа {archetype_id} из листа {sheet_name}: {e}")
            return None
    
    @cached(cache=TTLCache(maxsize=10, ttl=3600))
    def get_all_archetypes(self, user_gender="female"):
        """Получить все архетипы из соответствующего листа в зависимости от пола"""
        user_gender = self.validate_user_gender(user_gender)
        sheet_name = self._get_sheet_name("Archetypes", user_gender)
        
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            records = sheet.get_all_records()
            return records
        except gspread.exceptions.WorksheetNotFound:
            logging.error(f"Лист '{sheet_name}' не найден.")
            return []
        except Exception as e:
            logging.error(f"Не удалось получить список архетипов из листа {sheet_name}: {e}")
            return []
    
    def _handle_sheet_error(self, sheet_name: str, operation: str, error: Exception):
        """Централизованная обработка ошибок доступа к листам"""
        if isinstance(error, gspread.exceptions.WorksheetNotFound):
            logging.error(f"Лист '{sheet_name}' не найден при выполнении операции '{operation}'")
            logging.error("Проверьте структуру объединенной таблицы")
        elif isinstance(error, gspread.exceptions.APIError):
            logging.error(f"Ошибка Google Sheets API при работе с листом '{sheet_name}': {error}")
        else:
            logging.error(f"Неожиданная ошибка при работе с листом '{sheet_name}' в операции '{operation}': {error}")
    
    def check_sheet_exists(self, base_name: str, user_gender: str) -> bool:
        """Проверяет существование листа для указанного пола"""
        sheet_name = self._get_sheet_name(base_name, user_gender)
        try:
            self.spreadsheet.worksheet(sheet_name)
            return True
        except gspread.exceptions.WorksheetNotFound:
            logging.warning(f"Лист '{sheet_name}' не найден")
            return False
        except Exception as e:
            logging.error(f"Ошибка проверки существования листа '{sheet_name}': {e}")
            return False
    
    def get_available_sheets_info(self) -> dict:
        """Возвращает информацию о доступных листах для диагностики"""
        try:
            available_sheets = [ws.title for ws in self.spreadsheet.worksheets()]
            
            info = {
                'all_sheets': available_sheets,
                'config_available': 'Config' in available_sheets,
                'female_sheets': {
                    'questions': 'Questions_Female' in available_sheets,
                    'answers': 'Answers_Female' in available_sheets,
                    'archetypes': 'Archetypes_Female' in available_sheets
                },
                'male_sheets': {
                    'questions': 'Questions_Male' in available_sheets,
                    'answers': 'Answers_Male' in available_sheets,
                    'archetypes': 'Archetypes_Male' in available_sheets
                }
            }
            
            return info
        except Exception as e:
            logging.error(f"Ошибка получения информации о листах: {e}")
            return {'error': str(e)}