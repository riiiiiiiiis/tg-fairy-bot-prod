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
├── README.md           # Project documentation
├── .venv/              # Python virtual environment (not in git)
├── app/                # Main application package
│   ├── __init__.py     # Package initialization (empty)
│   ├── handlers.py     # Telegram bot message handlers
│   ├── keyboards.py    # Inline keyboard generation
│   └── gsheets.py      # Google Sheets API integration
├── tests/              # Test suite
│   ├── README.md       # Testing documentation
│   └── test_unified_gsheets.py  # Google Sheets integration tests
├── docs/               # Documentation files
│   ├── google-sheets-structure.md  # Sheets structure documentation
│   ├── service-account-setup.md    # Google service account setup
│   └── worksheet-schemas.md        # Worksheet schema definitions
└── .kiro/              # Kiro IDE configuration
    ├── specs/          # Feature specifications
    │   ├── gender-based-quiz/      # Gender selection feature
    │   ├── google-sheets-structure/ # Sheets structure spec
    │   └── unified-quiz-table/     # Unified quiz implementation
    └── steering/       # Development guidelines
        ├── product.md  # Product requirements
        ├── structure.md # Project structure
        └── tech.md     # Technology stack
```

## File Responsibilities

### Root Level
- **main.py** - Bot initialization, dispatcher setup, and polling start
- **config.py** - Loads environment variables using python-dotenv
- **requirements.txt** - All Python dependencies with pinned versions
- **Procfile** - Railway deployment command (`web: python main.py`)

### app/ Package
- **handlers.py** - All Telegram message and callback handlers
  - State management (Introduction, Quiz states)
  - Command handlers (/start, /help)
  - Quiz flow logic and scoring
  - Gender selection and table switching
- **keyboards.py** - Inline keyboard generation utilities
  - Answer selection keyboards with emoji feedback
  - Gender selection keyboards
- **gsheets.py** - Google Sheets integration
  - Cached data retrieval methods
  - Authentication handling
  - Worksheet access (Config, Questions, Answers, Archetypes)
  - Gender-based table selection

### tests/ Package
- **test_unified_gsheets.py** - Comprehensive Google Sheets integration tests
- **README.md** - Testing guidelines and setup instructions

### docs/ Package
- Configuration and setup documentation
- Feature-specific setup guides
- Schema definitions and examples

## Code Organization Patterns

### State Management
- Uses aiogram FSM with defined state groups
- `Introduction` states for onboarding and gender selection
- `Quiz` states for question progression
- State data persistence across handlers

### Handler Organization
- All handlers in single router for simplicity
- Async functions with comprehensive error handling
- State data passed between handlers
- Callback query handlers for interactive elements

### Data Flow
- Google Sheets as single source of truth
- Cached responses to minimize API calls (TTL-based)
- Environment-based configuration
- Gender-based dynamic table selection

### Error Handling
- Comprehensive logging throughout the application
- Graceful fallbacks for missing data
- User-friendly error messages
- Automatic retry mechanisms for API calls

### Naming Conventions
- Snake_case for Python variables and functions
- Descriptive handler function names ending in `_handler`
- State classes use PascalCase
- Callback data uses colon-separated format (`ans_num:1`, `gender:male`)
- Constants in UPPER_CASE

## Dependencies Management
- Keep requirements.txt minimal and focused
- Pin versions for production stability
- Use virtual environment (.venv) for isolation
- Regular dependency updates with testing
- Separate dev dependencies if needed

## Testing Strategy
- Unit tests for core functionality
- Integration tests for Google Sheets API
- Mock external dependencies in tests
- Test coverage for critical paths
- Automated testing in CI/CD pipeline