# Telegram Fairy Bot

A sophisticated Telegram personality quiz bot that helps users discover their archetype through a comprehensive 19-question interactive quiz with gender-specific content and personalized results.

## Features

- **Gender-Based Personalization**: Separate content and scoring for male and female users
- **Interactive Quiz**: 19 carefully crafted questions with multiple choice answers
- **Advanced Scoring**: Users select 3 out of 6 options per question with weighted scoring
- **Personality Analysis**: Results show top 3 matching archetypes with detailed descriptions
- **Media Delivery**: Automatic PDF reports and video content after completion
- **Payment Integration**: Built-in premium content upselling
- **Google Sheets Backend**: Dynamic content management without code deployment
- **Caching System**: Optimized performance with TTL-based caching
- **Comprehensive Logging**: Detailed monitoring and debugging capabilities

## Quick Start

### Prerequisites

- Python 3.8+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Google Cloud account with Sheets API enabled
- Google Sheets document with proper structure

### Setup

```bash
# Clone and setup
git clone <repository-url>
cd tg-fairy-bot

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Add to `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
SPREADSHEET_KEY=your_default_sheets_id
SPREADSHEET_KEY_FEMALE=your_female_sheets_id
SPREADSHEET_KEY_MALE=your_male_sheets_id
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

### Run

```bash
 source .venv/bin/activate && python main.py
source .venv/bin/activate
python main.py
```

## Documentation

### Setup Guides

- **[Service Account Setup](docs/service-account-setup.md)** - Google Cloud configuration
- **[Worksheet Schemas](docs/worksheet-schemas.md)** - Complete data structure guide
- **[Google Sheets Structure](docs/google-sheets-structure.md)** - Content examples

### Development Guidelines

- **[Technology Stack](.kiro/steering/tech.md)** - Tech stack and tools
- **[Project Structure](.kiro/steering/structure.md)** - Code organization
- **[Development Guide](.kiro/steering/development.md)** - Development workflow
- **[Product Overview](.kiro/steering/product.md)** - Product requirements

## Architecture

### Project Structure

```
tg-fairy-bot/
├── main.py              # Application entry point
├── config.py            # Environment configuration
├── requirements.txt     # Python dependencies
├── Procfile            # Railway deployment config
├── .env                # Local environment variables
├── app/                # Main application package
│   ├── handlers.py     # Telegram bot handlers
│   ├── keyboards.py    # Inline keyboard generation
│   └── gsheets.py      # Google Sheets integration
├── tests/              # Test suite
├── docs/               # Technical documentation
└── .kiro/              # Kiro IDE configuration
    ├── specs/          # Feature specifications
    └── steering/       # Development guidelines
```

### Key Components

- **Async Architecture**: Full async/await implementation for performance
- **FSM State Management**: Robust user session handling with aiogram
- **Caching Layer**: TTL-based caching for Google Sheets API optimization
- **Error Handling**: Comprehensive error handling with graceful fallbacks
- **Gender-Based Logic**: Dynamic table selection based on user choice

## Development

### Local Development

```bash
# Activate environment
source .venv/bin/activate

# Run bot
python main.py

# Run tests
python -m pytest tests/ -v

# Monitor logs
tail -f bot.log
```

### Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Test Google Sheets integration
python -m pytest tests/test_unified_gsheets.py -v
```

## Deployment

### Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway link
railway up
```

### Environment Variables (Production)

- `BOT_TOKEN` - Telegram bot token
- `SPREADSHEET_KEY` - Default/fallback Google Sheets ID
- `SPREADSHEET_KEY_FEMALE` - Female-specific content sheets
- `SPREADSHEET_KEY_MALE` - Male-specific content sheets
- `GOOGLE_CREDENTIALS_JSON` - Service account credentials

## Troubleshooting

### Common Issues

- **Google Sheets API**: Check service account permissions and API enablement
- **Bot Token**: Verify token from @BotFather and environment configuration
- **Virtual Environment**: Ensure proper activation and dependency installation
- **Caching**: Clear cache if data appears stale

### Debug Commands

```bash
# Test configuration
python -c "from config import *; print('Config loaded')"

# Test Google Sheets connection
python -c "from app.gsheets import GoogleSheetsDB; db = GoogleSheetsDB(); print(db.get_config_value('welcome_sequence_1'))"

# Validate bot token
python -c "from aiogram import Bot; from config import BOT_TOKEN; Bot(BOT_TOKEN)"
```

## Contributing

1. Create feature branch from main
2. Follow development guidelines in `.kiro/steering/`
3. Write tests for new functionality
4. Update documentation as needed
5. Submit pull request for review

## Support

- Review troubleshooting section above
- Check console logs for detailed error messages
- Ensure all environment variables are properly configured
- Verify Google Sheets structure matches schema documentation
