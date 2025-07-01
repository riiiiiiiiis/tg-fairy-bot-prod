
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from cachetools import cached, TTLCache

# Define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

class GoogleSheetsDB:
    def __init__(self, credentials_path, spreadsheet_key):
        # Authenticate with Google Sheets
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(spreadsheet_key)

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def get_config_value(self, key):
        sheet = self.spreadsheet.worksheet('Config')
        cell = sheet.find(key)
        return sheet.cell(cell.row, cell.col + 1).value

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def get_question(self, question_id):
        sheet = self.spreadsheet.worksheet('Questions')
        cell = sheet.find(str(question_id))
        row = sheet.row_values(cell.row)
        return {'question_text': row[1], 'prompt_text': row[2]}

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def get_answers(self, question_id):
        sheet = self.spreadsheet.worksheet('Answers')
        records = sheet.get_all_records()
        return [record for record in records if record['question_id'] == question_id]

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def get_archetype_result(self, archetype_id):
        sheet = self.spreadsheet.worksheet('Archetypes')
        cell = sheet.find(archetype_id)
        row = sheet.row_values(cell.row)
        return {'main_description': row[1], 'secondary_description': row[2]}
