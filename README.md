# Telegram Fairy Bot

A Telegram archetype quiz bot that helps users discover their personality type through a 19-question quiz.

## Prerequisites

- Python 3.8+
- macOS with Terminal
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google Sheets API credentials

## Local Development Setup (macOS)

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd tg-fairy-bot
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (you should see (.venv) in your terminal prompt)
which python
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your credentials
nano .env
```

Add your credentials to `.env`:
```env
BOT_TOKEN=your_telegram_bot_token_here
SPREADSHEET_KEY=your_google_sheets_key_here
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
```

### 5. Google Sheets Setup
1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create service account credentials
4. Download JSON credentials
5. Copy the entire JSON content to `GOOGLE_CREDENTIALS_JSON` in `.env`

### 6. Run the Bot
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Run the bot
python main.py
```

### 7. Test the Bot
1. Send `/start` to your bot on Telegram
2. Complete the quiz flow
3. Check console logs for any errors

## Development Commands

```bash
# Activate virtual environment (run this every time you open a new terminal)
source .venv/bin/activate

# Install new dependencies
pip install package_name
pip freeze > requirements.txt

# Deactivate virtual environment
deactivate

# Run with logging
python main.py

# Check bot status
ps aux | grep python
```

## Project Structure

```
tg-fairy-bot/
├── main.py              # Entry point
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── Procfile            # Railway deployment config
├── .env                # Environment variables (local)
├── .gitignore          # Git ignore rules
└── app/
    ├── __init__.py     # Package initialization
    ├── handlers.py     # Bot message handlers
    ├── keyboards.py    # Inline keyboard generation
    └── gsheets.py      # Google Sheets integration
```

## Troubleshooting

### Virtual Environment Issues
```bash
# If activation fails
which python3
python3 -m venv .venv --clear

# If .venv already exists
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

### Google Sheets Connection
- Verify service account has access to your spreadsheet
- Check that JSON credentials are properly formatted
- Ensure Google Sheets API is enabled in Google Cloud Console

### Bot Token Issues
- Get token from [@BotFather](https://t.me/BotFather)
- Ensure token is properly set in `.env`
- Check for extra spaces or newlines in `.env` file

## Deployment

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard:
   - `BOT_TOKEN`
   - `SPREADSHEET_KEY`
   - `GOOGLE_CREDENTIALS_JSON`
3. Deploy automatically on push to main branch

### Manual Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

## Support

For issues and questions:
- Check the troubleshooting section above
- Review console logs for error messages
- Ensure all environment variables are set correctly