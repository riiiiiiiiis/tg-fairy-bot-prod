# Настройка Service Account для Google Sheets

## Обзор

Для работы Telegram Fairy Bot с Google Таблицей необходимо настроить Service Account - специальный аккаунт для программного доступа к Google API без участия пользователя.

## Шаг 1: Создание проекта в Google Cloud

### 1.1 Создание проекта
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Нажмите на выпадающий список проектов в верхней панели
3. Нажмите **"New Project"** (Новый проект)
4. Введите название проекта: `telegram-fairy-bot`
5. Нажмите **"Create"** (Создать)
6. Дождитесь создания проекта и переключитесь на него

### 1.2 Включение Google Sheets API
1. В левом меню выберите **"APIs & Services"** → **"Library"**
2. В поиске введите: `Google Sheets API`
3. Нажмите на **"Google Sheets API"** в результатах
4. Нажмите кнопку **"Enable"** (Включить)
5. Дождитесь активации API

## Шаг 2: Создание Service Account

### 2.1 Создание аккаунта
1. Перейдите в **"APIs & Services"** → **"Credentials"**
2. Нажмите **"Create Credentials"** → **"Service Account"**
3. Заполните форму:
   - **Service account name**: `fairy-bot-sheets`
   - **Service account ID**: `fairy-bot-sheets` (заполнится автоматически)
   - **Description**: `Service account for Telegram Fairy Bot Google Sheets access`
4. Нажмите **"Create and Continue"**

### 2.2 Настройка ролей (опционально)
1. В разделе **"Grant this service account access to project"**:
   - Можно оставить пустым для минимальных прав
   - Или выбрать роль **"Viewer"** для дополнительной безопасности
2. Нажмите **"Continue"**

### 2.3 Завершение создания
1. Раздел **"Grant users access to this service account"** можно пропустить
2. Нажмите **"Done"**

## Шаг 3: Создание JSON-ключа

### 3.1 Генерация ключа
1. В списке **Service Accounts** найдите созданный аккаунт `fairy-bot-sheets`
2. Нажмите на email аккаунта для перехода к деталям
3. Перейдите на вкладку **"Keys"**
4. Нажмите **"Add Key"** → **"Create new key"**
5. Выберите тип **"JSON"**
6. Нажмите **"Create"**

### 3.2 Сохранение ключа
1. Файл автоматически скачается на ваш компьютер
2. **Важно**: Сохраните файл в безопасном месте
3. Скопируйте содержимое файла - оно понадобится для настройки бота

### 3.3 Структура JSON-ключа
Файл содержит примерно такую структуру:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "fairy-bot-sheets@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

**Важно запомнить `client_email`** - он понадобится для настройки доступа к таблице!##
 Шаг 4: Настройка доступа к Google Таблице

### 4.1 Создание или подготовка таблицы
1. Откройте [Google Sheets](https://sheets.google.com/)
2. Создайте новую таблицу или откройте существующую
3. Создайте 4 листа с названиями: `Config`, `Questions`, `Answers`, `Archetypes`
4. Скопируйте ID таблицы из URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

### 4.2 Предоставление доступа Service Account
1. В открытой Google Таблице нажмите кнопку **"Поделиться"** (Share) в правом верхнем углу
2. В поле **"Добавить пользователей и группы"** вставьте email Service Account:
   ```
   fairy-bot-sheets@your-project.iam.gserviceaccount.com
   ```
3. Установите права доступа: **"Читатель"** (Viewer)
4. **Снимите галочку** "Уведомить пользователей" (чтобы не отправлять email на Service Account)
5. Нажмите **"Поделиться"**

### 4.3 Проверка доступа
После настройки в списке пользователей таблицы должен появиться Service Account с правами "Читатель".

## Шаг 5: Конфигурация бота

### 5.1 Настройка переменных окружения
Добавьте в файл `.env` следующие переменные:

```env
# ID таблицы из URL
SPREADSHEET_KEY=1BvhqJXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Полный JSON-ключ Service Account (в одну строку)
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"fairy-bot-sheets@your-project.iam.gserviceaccount.com","client_id":"123456789","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/fairy-bot-sheets%40your-project.iam.gserviceaccount.com","universe_domain":"googleapis.com"}
```

### 5.2 Альтернативный способ (через файл)
Вместо JSON в переменной окружения можно использовать файл:

1. Сохраните JSON-ключ как `google_credentials.json` в корне проекта
2. Добавьте в `.env`:
   ```env
   GOOGLE_CREDENTIALS_PATH=google_credentials.json
   ```
3. **Важно**: Добавьте файл в `.gitignore`!

## Шаг 6: Проверка настройки

### 6.1 Тестовый запуск
1. Убедитесь, что все зависимости установлены:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустите бота:
   ```bash
   python main.py
   ```

3. Проверьте логи на наличие ошибок подключения к Google Sheets

### 6.2 Проверка через код
Можно создать тестовый скрипт для проверки:

```python
from app.gsheets import GoogleSheetsDB
from config import GOOGLE_CREDENTIALS_JSON, SPREADSHEET_KEY

try:
    db = GoogleSheetsDB(
        credentials_json=GOOGLE_CREDENTIALS_JSON,
        spreadsheet_key=SPREADSHEET_KEY
    )
    
    # Тест чтения конфигурации
    welcome_msg = db.get_config_value('welcome_sequence_1')
    print(f"Успешно прочитано: {welcome_msg}")
    
    # Тест чтения вопроса
    question = db.get_question(1)
    print(f"Вопрос 1: {question}")
    
    print("✅ Подключение к Google Sheets работает!")
    
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
```

## Устранение проблем

### Ошибка "Permission denied"
**Причина**: Service Account не имеет доступа к таблице
**Решение**: 
1. Проверьте, что Service Account добавлен в права доступа к таблице
2. Убедитесь, что используется правильный `client_email` из JSON-ключа
3. Проверьте правильность `SPREADSHEET_KEY`

### Ошибка "Worksheet not found"
**Причина**: Неправильные названия листов
**Решение**:
1. Убедитесь, что листы называются точно: `Config`, `Questions`, `Answers`, `Archetypes`
2. Названия чувствительны к регистру

### Ошибка "API not enabled"
**Причина**: Google Sheets API не включен в проекте
**Решение**:
1. Перейдите в Google Cloud Console
2. Включите Google Sheets API в разделе "APIs & Services" → "Library"

### Ошибка парсинга JSON
**Причина**: Неправильное экранирование в `GOOGLE_CREDENTIALS_JSON`
**Решение**:
1. Убедитесь, что JSON записан в одну строку
2. Все кавычки внутри JSON должны быть экранированы
3. Используйте альтернативный способ через файл

### Ошибка "Invalid credentials"
**Причина**: Поврежденный или неправильный JSON-ключ
**Решение**:
1. Пересоздайте JSON-ключ в Google Cloud Console
2. Проверьте целостность скопированного JSON
3. Убедитесь, что используется правильный Service Account

## Безопасность

### Рекомендации по безопасности
1. **Никогда не публикуйте** JSON-ключи в публичных репозиториях
2. Добавьте `google_credentials.json` и `.env` в `.gitignore`
3. Используйте минимальные права доступа (только "Читатель")
4. Регулярно ротируйте ключи Service Account
5. Мониторьте использование API в Google Cloud Console

### Ограничения доступа
Service Account должен иметь доступ только к:
- Чтению Google Sheets API
- Конкретной таблице с данными бота
- Никаких дополнительных прав не требуется