# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram archetype quiz bot built with Python and aiogram. The bot conducts a 19-question quiz to determine users' personality archetypes. All content is managed externally in Google Sheets for easy editing by non-programmers.

## Architecture

The bot follows a modular structure:

- **main.py**: Entry point that initializes the bot and starts polling
- **config.py**: Environment variable configuration using python-dotenv
- **app/handlers.py**: Core bot logic including FSM states and callback handlers
- **app/keyboards.py**: Inline keyboard generation for quiz answers
- **app/gsheets.py**: Google Sheets integration with caching for quiz content
- **Procfile**: Railway deployment configuration

## Key Components

### State Management
Uses aiogram's FSM with these states:
- `Introduction.awaiting_promo_confirmation`
- `Introduction.awaiting_quiz_start`
- `Quiz.in_progress`
- `Quiz.awaiting_result_confirmation`

### Quiz Logic
- 19 questions total, each with 6 possible answers
- Users select 3 answers per question (ranked scoring: 3, 2, 1 points)
- Answers are numbered 1-6 and displayed with emoji feedback
- Final results show primary archetype + 2 secondary energies

### Google Sheets Integration
Data is cached (TTL 300s) and fetched from these sheets:
- `Config`: Bot messages and button text
- `Questions`: Question text and prompts
- `Answers`: Answer options linked to archetypes
- `Archetypes`: Result descriptions

## Common Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot locally
python main.py

# Deploy to Railway
# Uses Procfile: web: python main.py
```

## Environment Variables

Required in `.env`:
- `BOT_TOKEN`: Telegram bot token
- `GOOGLE_CREDENTIALS_PATH`: Path to service account JSON (default: "google_credentials.json")
- `SPREADSHEET_KEY`: Google Sheets document ID

## Testing

No automated tests are currently implemented. Manual testing involves:
1. Start conversation with `/start`
2. Complete quiz flow (19 questions × 3 selections each)
3. Verify archetype results are displayed correctly
4. Test `/help` command

## Important Notes

- The bot uses Russian language for user interface
- Google Sheets API has rate limits - caching is essential
- Answer buttons use numbered display (1-6) but track by answer_id internally
- Quiz state is cleared after completion or on new `/start`
- Error handling includes graceful fallbacks when Google Sheets is unavailable