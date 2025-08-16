# Technology Stack

## Core Technologies
- **Python 3.8+** - Primary language
- **aiogram 3.x** - Modern Telegram Bot API framework with async support
- **Google Sheets API** - Content management backend via gspread
- **Railway** - Cloud deployment platform

## Key Libraries
- `aiogram` - Modern Telegram Bot framework with FSM support
- `gspread` - Google Sheets Python API client
- `oauth2client` - Google OAuth2 authentication
- `python-dotenv` - Environment variable management
- `cachetools` - Response caching with TTL for performance

## Architecture Patterns
- **Async/await** - All bot operations are asynchronous
- **FSM (Finite State Machine)** - User state management with aiogram states
- **Router pattern** - Message handlers organized in routers
- **Caching** - Google Sheets responses cached with TTL (5min-1hr)
- **Environment-based config** - All secrets in .env files
- **Gender-based content** - Dynamic table selection based on user gender

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
# Edit .env with your credentials
```

### Running the Bot
```bash
# Activate environment (required each session)
source .venv/bin/activate

# Run bot locally
python main.py

# Check running processes
ps aux | grep python

# View logs
tail -f bot.log
```

### Testing
```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_unified_gsheets.py -v
```

### Dependency Management
```bash
# Install new package
pip install package_name
pip freeze > requirements.txt

# Deactivate environment
deactivate
```

### Deployment
```bash
# Railway CLI deployment
railway login
railway link
railway up

# Check deployment status
railway status
```

## Environment Variables
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `SPREADSHEET_KEY` - Default/Female Google Sheets document ID
- `SPREADSHEET_KEY_FEMALE` - Female-specific Google Sheets document ID
- `SPREADSHEET_KEY_MALE` - Male-specific Google Sheets document ID
- `GOOGLE_CREDENTIALS_JSON` - Service account JSON (preferred)
- `GOOGLE_CREDENTIALS_PATH` - Local credentials file path (fallback)

## Code Quality Standards
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Write comprehensive docstrings for all functions
- Implement proper error handling with logging
- Use async/await consistently for all I/O operations
- Cache expensive operations (Google Sheets API calls)
- Validate all user inputs and external data