# Development Guidelines

## Setup and Installation

### Prerequisites
- Python 3.8+ installed
- Google Cloud account with billing enabled
- Telegram Bot Token from @BotFather
- Google Sheets document with proper structure

### Initial Setup
```bash
# Clone and navigate to project
git clone <repository-url>
cd tg-fairy-bot

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials
```

### Google Sheets Setup
1. Follow `docs/service-account-setup.md` for Google Cloud configuration
2. Use `docs/worksheet-schemas.md` for proper sheet structure
3. Reference `docs/google-sheets-structure.md` for content examples

## Development Workflow

### Code Standards
- **Type Hints**: Use for all function parameters and return values
- **Docstrings**: Write comprehensive docstrings for all functions
- **Error Handling**: Implement proper try/catch with logging
- **Async/Await**: Use consistently for all I/O operations
- **PEP 8**: Follow Python style guidelines
- **Logging**: Use structured logging throughout

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_unified_gsheets.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Local Development
```bash
# Activate environment
source .venv/bin/activate

# Run bot locally
python main.py

# Monitor logs
tail -f bot.log

# Check processes
ps aux | grep python
```

## Architecture Principles

### State Management
- Use aiogram FSM for user session handling
- Store minimal data in state - prefer stateless design
- Handle state transitions gracefully
- Implement proper cleanup for expired states

### Caching Strategy
- Cache Google Sheets responses with appropriate TTL
- Use memory-based caching for development
- Consider Redis for production scaling
- Implement cache invalidation strategies

### Error Handling
- Log all errors with context
- Provide user-friendly error messages
- Implement graceful fallbacks
- Use retry mechanisms for external API calls

### Performance Optimization
- Minimize Google Sheets API calls through caching
- Use async/await for concurrent operations
- Batch operations where possible
- Monitor and optimize response times

## Feature Development

### Adding New Features
1. **Spec Creation**: Use Kiro specs for complex features
2. **Requirements**: Define clear user stories and acceptance criteria
3. **Design**: Create comprehensive design document
4. **Implementation**: Follow task-based development
5. **Testing**: Write tests before and during implementation
6. **Documentation**: Update relevant docs

### Modifying Existing Features
1. **Impact Analysis**: Assess changes to existing functionality
2. **Backward Compatibility**: Ensure existing users aren't affected
3. **Testing**: Test both new and existing functionality
4. **Migration**: Plan data migration if needed

## Google Sheets Integration

### Best Practices
- **Caching**: Always cache responses with appropriate TTL
- **Error Handling**: Handle API rate limits and network issues
- **Data Validation**: Validate all data from sheets
- **Fallbacks**: Implement fallback mechanisms for missing data

### Schema Changes
- **Backward Compatibility**: Ensure changes don't break existing data
- **Migration**: Plan migration strategy for schema changes
- **Testing**: Test with both old and new schema formats
- **Documentation**: Update schema documentation

## Deployment

### Railway Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Deploy
railway up

# Check status
railway status

# View logs
railway logs
```

### Environment Variables
- **Production**: Set all required environment variables in Railway
- **Security**: Never commit credentials to repository
- **Validation**: Validate all environment variables on startup
- **Documentation**: Document all required variables

## Monitoring and Debugging

### Logging Strategy
- **Structured Logging**: Use consistent log format
- **Log Levels**: Use appropriate levels (DEBUG, INFO, WARNING, ERROR)
- **Context**: Include relevant context in log messages
- **Performance**: Log performance metrics for critical operations

### Debugging Tools
- **Local Testing**: Use ngrok for webhook testing
- **Log Analysis**: Monitor logs for errors and performance issues
- **API Testing**: Test Google Sheets integration separately
- **User Flow Testing**: Test complete user journeys

## Security Considerations

### Credentials Management
- **Environment Variables**: Store all secrets in environment variables
- **Service Accounts**: Use minimal required permissions
- **Key Rotation**: Regularly rotate API keys and credentials
- **Access Control**: Limit access to production credentials

### Data Protection
- **User Data**: Minimize collection and storage of user data
- **Logging**: Avoid logging sensitive information
- **API Security**: Validate all external API responses
- **Input Validation**: Sanitize all user inputs

## Troubleshooting

### Common Issues
- **Google Sheets API**: Check credentials and permissions
- **Telegram API**: Verify bot token and webhook configuration
- **Caching**: Clear cache if data seems stale
- **State Management**: Check for state corruption or expiration

### Debug Commands
```bash
# Check environment variables
python -c "from config import *; print('Config loaded successfully')"

# Test Google Sheets connection
python -c "from app.gsheets import GoogleSheetsDB; db = GoogleSheetsDB(); print(db.get_config_value('welcome_sequence_1'))"

# Check bot token
python -c "from aiogram import Bot; from config import BOT_TOKEN; bot = Bot(BOT_TOKEN); print('Bot token valid')"
```

## Contributing

### Code Review Process
1. **Feature Branch**: Create feature branch from main
2. **Implementation**: Follow development guidelines
3. **Testing**: Ensure all tests pass
4. **Documentation**: Update relevant documentation
5. **Review**: Submit pull request for review
6. **Deployment**: Deploy after approval

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Documentation Updates
- Update steering docs for architectural changes
- Update technical docs for implementation details
- Update README for setup changes
- Update specs for feature changes