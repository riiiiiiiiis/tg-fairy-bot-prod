# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot locally
python main.py

# Monitor logs
tail -f bot.log
```

### Configuration Testing
```bash
# Test configuration loading
python -c "from config import *; print('Config loaded successfully')"

# Test Google Sheets connection
python -c "from app.gsheets import GoogleSheetsDB; db = GoogleSheetsDB(); print(db.get_config_value('welcome_sequence_1'))"

# Validate bot token
python -c "from aiogram import Bot; from config import BOT_TOKEN; bot = Bot(BOT_TOKEN); print('Bot token valid')"
```

### Testing
```bash
# Run tests (if tests/ directory exists)
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Deployment (Railway)
```bash
railway login
railway link
railway up
railway status
railway logs
```

## Architecture

### Core Components
- **main.py**: Application entry point with async bot initialization
- **config.py**: Environment variable management with migration warnings for deprecated variables
- **app/handlers.py**: Telegram bot handlers using aiogram FSM for state management
- **app/gsheets.py**: Google Sheets integration with TTL-based caching (300s)
- **app/keyboards.py**: Inline keyboard generation utilities

### Key Architecture Patterns
- **Async/Await**: Full async implementation throughout codebase
- **FSM State Management**: Uses aiogram's finite state machine for user sessions
- **Unified Google Sheets**: Single spreadsheet with gender-specific worksheets
- **Caching Strategy**: TTL cache (300s) for Google Sheets API responses to minimize API calls
- **Gender-Based Logic**: Dynamic worksheet selection based on user gender choice

### Google Sheets Structure
The bot uses a unified Google Sheets approach with these required worksheets:
- `Config` - Global configuration messages
- `Questions_Female/Questions_Male` - Gender-specific questions
- `Answers_Female/Answers_Male` - Gender-specific answer choices
- `Archetypes_Female/Archetypes_Male` - Gender-specific personality results

### State Management
- `Introduction` states: gender selection, promo confirmation, quiz start
- `Quiz` states: in progress, result confirmation
- User data stored in FSM context includes: selected_gender, current_question_id, sheets_db instance

### Environment Variables
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `SPREADSHEET_KEY` - Unified Google Sheets document ID
- `GOOGLE_CREDENTIALS_JSON` - Service account credentials as JSON string
- `GOOGLE_CREDENTIALS_PATH` - Optional fallback to credentials file

### Error Handling
- Comprehensive logging with structured messages in Russian
- Graceful fallbacks for missing Google Sheets data
- User-friendly error messages for configuration issues
- Migration warnings for deprecated environment variables

### Development Guidelines
- Follow async/await patterns consistently
- Use TTL caching for all external API calls
- Implement proper state cleanup and error recovery
- Log all significant operations with context
- Validate all data from Google Sheets before use

### Documentation Structure
- `docs/service-account-setup.md` - Google Cloud configuration
- `docs/worksheet-schemas.md` - Complete data structure specifications
- `docs/google-sheets-structure.md` - Content examples and migration guide
- `.kiro/steering/` - Development guidelines and architecture decisions