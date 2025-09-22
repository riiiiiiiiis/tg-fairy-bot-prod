#!/usr/bin/env python3
"""
Скрипт для генерации правильно отформатированной JSON строки
для переменной окружения GOOGLE_CREDENTIALS_JSON в Railway
"""
import json
import sys

def minify_json_for_env():
    try:
        # Читаем JSON файл
        with open('google_credentials.json', 'r') as f:
            data = json.load(f)

        # Минифицируем JSON (убираем лишние пробелы)
        minified = json.dumps(data, separators=(',', ':'))

        print("=" * 80)
        print("ИНСТРУКЦИЯ ДЛЯ RAILWAY:")
        print("=" * 80)
        print("\n1. Зайдите в настройки проекта на Railway")
        print("2. Перейдите в раздел Variables")
        print("3. Добавьте или обновите переменную GOOGLE_CREDENTIALS_JSON")
        print("4. В качестве значения используйте строку ниже (скопируйте всё целиком):\n")
        print("-" * 80)
        print(minified)
        print("-" * 80)
        print("\n5. Убедитесь что также установлены переменные:")
        print("   - BOT_TOKEN")
        print("   - SPREADSHEET_KEY")
        print("\n6. Сохраните и передеплойте приложение")

        # Также сохраним в файл для удобства
        with open('railway_env_json.txt', 'w') as f:
            f.write(minified)
        print("\n✅ JSON также сохранён в файл: railway_env_json.txt")

    except FileNotFoundError:
        print("❌ Файл google_credentials.json не найден!")
        print("   Сначала создайте его с данными сервисного аккаунта")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в формате JSON: {e}")
        sys.exit(1)

if __name__ == "__main__":
    minify_json_for_env()