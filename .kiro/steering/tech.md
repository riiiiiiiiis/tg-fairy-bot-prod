# Technology Stack

## Core Technologies
- **Python 3.8+** - Primary language
- **aiogram** - Telegram Bot API framework with async support
- **Google Sheets API** - Content management backend
- **Railway** - Deployment platform

## Key Libraries
- `aiogram` - Modern Telegram Bot framework
- `gspread` - Google Sheets Python API
- `oauth2client` - Google OAuth2 authentication
- `python-dotenv` - Environment variable management
- `cachetools` - Response caching with TTL

## Architecture Patterns
- **Async/await** - All bot operations are asynchronous
- **FSM (Finite State Machine)** - User state management with aiogram states
- **Router pattern** - Message handlers organized in routers
- **Caching** - Google Sheets responses cached with TTL (5min-1hr)
- **Environment-based config** - All secrets in .env files

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
```

## Environment Variables
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `SPREADSHEET_KEY` - Google Sheets document ID
- `GOOGLE_CREDENTIALS_JSON` - Service account JSON (preferred)
- `GOOGLE_CREDENTIALS_PATH` - Local credentials file path (fallback)