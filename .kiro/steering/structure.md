# Project Structure

## Directory Organization

```
tg-fairy-bot/
├── main.py              # Application entry point
├── config.py            # Environment configuration loader
├── requirements.txt     # Python dependencies
├── Procfile            # Railway deployment configuration
├── .env                # Local environment variables (not in git)
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
├── .venv/              # Python virtual environment (not in git)
└── app/                # Main application package
    ├── __init__.py     # Package initialization (empty)
    ├── handlers.py     # Telegram bot message handlers
    ├── keyboards.py    # Inline keyboard generation
    └── gsheets.py      # Google Sheets API integration
```

## File Responsibilities

### Root Level
- **main.py** - Bot initialization, dispatcher setup, and polling start
- **config.py** - Loads environment variables using python-dotenv
- **requirements.txt** - All Python dependencies with versions
- **Procfile** - Railway deployment command (`web: python main.py`)

### app/ Package
- **handlers.py** - All Telegram message and callback handlers
  - State management (Introduction, Quiz states)
  - Command handlers (/start, /help)
  - Quiz flow logic and scoring
- **keyboards.py** - Inline keyboard generation utilities
  - Answer selection keyboards with emoji feedback
- **gsheets.py** - Google Sheets integration
  - Cached data retrieval methods
  - Authentication handling
  - Worksheet access (Config, Questions, Answers, Archetypes)

## Code Organization Patterns

### State Management
- Uses aiogram FSM with defined state groups
- `Introduction` states for onboarding flow
- `Quiz` states for question progression

### Handler Organization
- All handlers in single router for simplicity
- Async functions with proper error handling
- State data passed between handlers

### Data Flow
- Google Sheets as single source of truth
- Cached responses to minimize API calls
- Environment-based configuration

### Naming Conventions
- Snake_case for Python variables and functions
- Descriptive handler function names ending in `_handler`
- State classes use PascalCase
- Callback data uses colon-separated format (`ans_num:1`)

## Dependencies
- Keep requirements.txt minimal and focused
- Pin versions for production stability
- Use virtual environment for isolation