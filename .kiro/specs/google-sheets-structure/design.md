# Design Document

## Overview

Данный документ описывает детальную структуру Google Таблицы, необходимой для работы Telegram Fairy Bot. Таблица состоит из четырех основных листов, каждый из которых имеет специфическую структуру столбцов и содержит определенные типы данных.

## Architecture

### Data Flow
```
Google Sheets ← Service Account Authentication
     ↓
Cache Layer (TTL: 5min-1hr)
     ↓
Bot Application (gsheets.py)
     ↓
Telegram Bot Handlers
```

### Authentication
- Service Account с JSON credentials
- OAuth2 через oauth2client library
- Права доступа: чтение Google Sheets

## Components and Interfaces

### 1. Config Worksheet

**Назначение:** Хранение конфигурационных текстов бота

**Структура столбцов:**
| Столбец A | Столбец B |
|-----------|-----------|
| key       | value     |

**Обязательные ключи:**
- `welcome_sequence_1` - Первое приветственное сообщение
- `welcome_sequence_2` - Второе приветственное сообщение  
- `promo_sequence` - Промо-текст с призывом к действию
- `promo_button_text` - Текст кнопки промо
- `instruction_sequence` - Инструкции перед началом теста
- `start_button_text` - Текст кнопки начала теста
- `final_cta_text` - Финальный призыв к показу результатов
- `final_cta_button` - Текст кнопки показа результатов

**Пример данных:**
```
key                    | value
welcome_sequence_1     | Добро пожаловать в тест архетипов!
welcome_sequence_2     | Узнайте свой тип личности за 5 минут
promo_sequence         | Готовы начать увлекательное путешествие?\\nОтветьте на 19 вопросов
promo_button_text      | Начать тест
```

### 2. Questions Worksheet

**Назначение:** Хранение вопросов викторины

**Структура столбцов:**
| Столбец A    | Столбец B      | Столбец C    |
|--------------|----------------|--------------|
| question_id  | question_text  | prompt_text  |

**Требования к данным:**
- `question_id`: Числа от 1 до 19 (тип: integer)
- `question_text`: Основной текст вопроса (тип: string)
- `prompt_text`: Дополнительная подсказка или инструкция (тип: string)

**Пример данных:**
```
question_id | question_text                           | prompt_text
1          | Как вы предпочитаете проводить выходные? | Выберите 3 наиболее подходящих варианта
2          | Что вас больше всего мотивирует?        | Отметьте то, что резонирует с вами
```

### 3. Answers Worksheet

**Назначение:** Хранение вариантов ответов с привязкой к архетипам

**Структура столбцов:**
| Столбец A  | Столбец B    | Столбец C    | Столбец D     |
|------------|--------------|--------------|---------------|
| answer_id  | question_id  | answer_text  | archetype_id  |

**Требования к данным:**
- `answer_id`: Уникальный идентификатор ответа (тип: integer)
- `question_id`: Ссылка на вопрос (тип: integer, 1-19)
- `answer_text`: Текст варианта ответа (тип: string)
- `archetype_id`: Идентификатор архетипа для подсчета баллов (тип: string)

**Логика подсчета баллов:**
- 1-й выбранный ответ: 3 балла
- 2-й выбранный ответ: 2 балла  
- 3-й выбранный ответ: 1 балл

**Пример данных:**
```
answer_id | question_id | answer_text                    | archetype_id
1         | 1          | Читать книги дома              | introvert
2         | 1          | Встречаться с друзьями         | extrovert
3         | 1          | Заниматься творчеством         | creator
4         | 1          | Изучать что-то новое           | explorer
5         | 1          | Помогать другим                | caregiver
6         | 1          | Планировать будущее            | ruler
```

### 4. Archetypes Worksheet

**Назначение:** Хранение описаний архетипов для результатов

**Структура столбцов:**
| Столбец A     | Столбец B         | Столбец C              |
|---------------|-------------------|------------------------|
| archetype_id  | main_description  | secondary_description  |

**Требования к данным:**
- `archetype_id`: Уникальный идентификатор архетипа (тип: string)
- `main_description`: Полное описание для основного результата (тип: string, HTML)
- `secondary_description`: Краткое описание для 2-го и 3-го места (тип: string, HTML)

**Пример данных:**
```
archetype_id | main_description                                    | secondary_description
introvert    | <b>Интроверт</b>\\n\\nВы черпаете энергию...       | Также в вас есть черты интроверта...
extrovert    | <b>Экстраверт</b>\\n\\nВы получаете энергию...     | Экстравертные качества проявляются...
creator      | <b>Творец</b>\\n\\nВы видите мир через призму...   | Творческое начало присутствует...
```

## Data Models

### GoogleSheetsDB Class Methods

```python
# Конфигурация
get_config_value(key: str) -> str

# Вопросы  
get_question(question_id: int) -> dict
# Возвращает: {'question_text': str, 'prompt_text': str}

# Ответы
get_answers(question_id: int) -> list[dict]
# Возвращает: [{'answer_id': int, 'question_id': int, 'answer_text': str, 'archetype_id': str}]

# Архетипы
get_archetype_result(archetype_id: str) -> dict
# Возвращает: {'main_description': str, 'secondary_description': str}

get_all_archetypes() -> list[dict]
# Возвращает: [{'archetype_id': str, ...}]
```

## Error Handling

### Worksheet Access Errors
- `WorksheetNotFound`: Лист не существует
- `CellNotFound`: Ключ не найден в Config
- Логирование всех ошибок с понятными сообщениями

### Data Validation
- Проверка существования обязательных столбцов
- Валидация типов данных (question_id как integer)
- Обработка пустых значений

## Testing Strategy

### Manual Testing Checklist
1. Создать тестовую Google Таблицу с правильной структурой
2. Заполнить минимальный набор данных (1-2 вопроса)
3. Настроить Service Account и права доступа
4. Протестировать каждый метод GoogleSheetsDB
5. Проверить кэширование и TTL
6. Протестировать обработку ошибок

### Required Test Data
- Минимум 2 вопроса с 6 ответами каждый
- Все обязательные конфигурационные ключи
- Минимум 3 архетипа с описаниями
- Корректные связи question_id ↔ answer_id ↔ archetype_id